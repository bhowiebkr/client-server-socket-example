# Import necessary modules
import errno
import sys
import socket
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QLineEdit,
)
from PySide6.QtCore import QObject, QThread, Signal


# Create a class for the client-side logic
class ClientClient(QObject):
    messageReceived = Signal(str)  # Signal to emit received messages
    errorOccurred = Signal(str)  # Signal to emit error messages

    def __init__(self):
        super().__init__()

        self.client_socket = None  # Socket object for communication
        self.running = True  # Flag to track the client's running state

    # Helper method to get the local IP address
    def lookup_ip(self) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        address = sock.getsockname()[0]
        sock.close()
        return address

    # Method to establish a socket connection to a server
    def connect_socket(self) -> bool:
        try:
            self.client_socket = socket.socket()
            self.client_socket.connect((self.lookup_ip(), 1234))  # Connect to a server on port 1234
            return True
        except socket.error as error:
            self.errorOccurred.emit(f"Connection error: {str(error)}")
            return False

    # Method to send a message and receive a response from the server
    def send_receive(self, msg: str) -> str:
        if not self.client_socket:
            self.errorOccurred.emit("Socket is not connected")
            return ""

        if not msg:
            self.errorOccurred.emit("Empty message")
            return ""

        try:
            self.client_socket.sendall(msg.encode("utf-8"))
            recv = self.client_socket.recv(1024).decode("utf-8")
            self.messageReceived.emit(recv)  # Emit the received message
            return recv
        except socket.error as error:
            self.errorOccurred.emit(f"Socket error: {str(error)}")
            return ""

    # Method to stop the client and close the socket
    def stop(self):
        if self.client_socket:
            print("Stopping client")
            self.client_socket.close()
        else:
            print("No client yet")


# Create the main window for the application
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client")

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        form = QFormLayout()
        self.input = QLineEdit()
        form.addRow("Input", self.input)
        self.layout.addLayout(form)

        # Create buttons to start and stop the client
        self.start_button = QPushButton("Start Client")
        self.start_button.clicked.connect(self.start_client)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Client")
        self.stop_button.clicked.connect(self.stop_client)
        self.layout.addWidget(self.stop_button)

        # Set the layout for the central widget
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Create a client instance and move it to a separate thread
        self.client_thread = QThread()
        self.client = ClientClient()
        self.client.moveToThread(self.client_thread)
        self.client_thread.started.connect(self.client.connect_socket)
        self.client_thread.start()

        # Connect UI signals to client methods
        self.input.returnPressed.connect(self.send_msg)
        self.client.messageReceived.connect(self.display_message)
        self.client.errorOccurred.connect(self.display_error)

    # Method to send a message when the user presses Enter
    def send_msg(self):
        msg = self.input.text()
        self.client.send_receive(msg)
        self.input.clear()

    # Method to start the client when the "Start Client" button is clicked
    def start_client(self):
        if not self.client.connect_socket():
            self.display_error("Failed to connect to the server")
        else:
            self.display_message("Client started")

    # Method to stop the client when the "Stop Client" button is clicked
    def stop_client(self):
        self.client.stop()
        self.client_thread.quit()
        self.client_thread.wait()
        self.display_message("Client stopped")

    # Method to display received messages in the text edit area
    def display_message(self, message):
        self.text_edit.append(message)

    # Method to display error messages in the text edit area
    def display_error(self, error_message):
        self.text_edit.append(f"Error: {error_message}")


# Main function to start the application
def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())


# Check if the script is being run as the main program
if __name__ == "__main__":
    main()
