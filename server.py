# Import necessary modules
import socket
import errno
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QObject, QThread, Signal


# Create a class for the server-side logic
class SocketServer(QObject):
    messageReceived = Signal(str)  # Signal to emit received messages
    errorOccurred = Signal(str)  # Signal to emit error messages

    def __init__(self):
        super().__init__()
        self.server_socket = None  # Socket object for server
        self.running = False  # Flag to track server's running state

    # Helper method to get the local IP address
    def lookup_ip(self) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        address = sock.getsockname()[0]
        sock.close()
        return address

    # Method to start the server and listen for incoming connections
    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.lookup_ip(), 1234))  # Bind to a specific IP and port
            self.server_socket.listen(1)
            self.running = True

            while self.running:
                client_socket, _ = self.server_socket.accept()
                self.handle_client(client_socket)
        except socket.error as error:
            self.errorOccurred.emit(f"Server error: {str(error)}")

    # Method to handle a client's connection
    def handle_client(self, client_socket):
        with client_socket:
            while self.running:
                try:
                    data = client_socket.recv(1024).decode("utf-8")
                    if not data:
                        break  # Client disconnected
                    client_socket.sendall(bytes(f"I got the message: {data}", "ascii"))

                    self.messageReceived.emit(data)  # Emit the received message
                except socket.error as error:
                    if error.errno in (errno.WSAECONNRESET, errno.WSAECONNABORTED):
                        self.errorOccurred.emit("Client connection reset or aborted")
                        break
                    else:
                        self.errorOccurred.emit(f"Socket error: {str(error)}")

    # Method to stop the server and close the socket
    def stop(self):
        print("Stopping server...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    # Method to start the server
    def start_server(self):
        if not self.running:
            self.server_thread = QThread()
            self.moveToThread(self.server_thread)
            self.server_thread.started.connect(self.run)
            self.server_thread.start()


# Create the main window for the application
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server")

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        # Create buttons to start and stop the server
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_server)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_server)
        self.layout.addWidget(self.stop_button)

        # Set the layout for the central widget
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.server_thread = QThread()
        self.server = SocketServer()
        self.server.messageReceived.connect(self.display_message)
        self.server.errorOccurred.connect(self.display_error)

        # Connect the server's start_server method to the thread's started signal
        self.server_thread.started.connect(self.server.start_server)

    # Method to start the server when the "Start Server" button is clicked
    def start_server(self):
        print("Starting server")
        self.server.moveToThread(self.server_thread)
        self.server_thread.start()
        print("Server started")

    # Method to stop the server when the "Stop Server" button is clicked
    def stop_server(self):
        print("Stopping Server")
        self.server.stop()

        self.server_thread.quit()
        self.server_thread.wait()

        print("Server Stopped")

    # Method to display received messages in the text edit area
    def display_message(self, message):
        print(f"Adding message: {message}")
        self.text_edit.append(message)

    # Method to display error messages in the text edit area
    def display_error(self, error_message):
        self.text_edit.append(f"Error: {error_message}")


# Main function to start the application
def main():
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()


# Check if the script is being run as the main program
if __name__ == "__main__":
    main()
