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


class SocketServer(QObject):
    messageReceived = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.server_socket = None
        self.running = False

    def lookup_ip(self) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        address = sock.getsockname()[0]
        sock.close()
        return address

    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.lookup_ip(), 1234))
            self.server_socket.listen(1)
            self.running = True

            while self.running:
                client_socket, _ = self.server_socket.accept()
                self.handle_client(client_socket)
        except socket.error as error:
            self.errorOccurred.emit(f"Server error: {str(error)}")

    def handle_client(self, client_socket):
        with client_socket:
            while self.running:
                try:
                    data = client_socket.recv(1024).decode("utf-8")
                    if not data:
                        break  # Client disconnected
                    client_socket.sendall(bytes(f"I got the message: {data}", "ascii"))

                    self.messageReceived.emit(data)
                except socket.error as error:
                    if error.errno in (errno.WSAECONNRESET, errno.WSAECONNABORTED):
                        self.errorOccurred.emit("Client connection reset or aborted")
                        break
                    else:
                        self.errorOccurred.emit(f"Socket error: {str(error)}")

    def stop(self):
        print("Stopping server...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def start_server(self):
        if not self.running:
            self.server_thread = QThread()
            self.moveToThread(self.server_thread)
            self.server_thread.started.connect(self.run)
            self.server_thread.start()


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server")

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_server)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_server)
        self.layout.addWidget(self.stop_button)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.server_thread = QThread()
        self.server = SocketServer()
        self.server.messageReceived.connect(self.display_message)
        self.server.errorOccurred.connect(self.display_error)

        # Connect the server's start_server method to the thread's started signal
        self.server_thread.started.connect(self.server.start_server)

    def start_server(self):
        print("Starting server")
        self.server.moveToThread(self.server_thread)
        self.server_thread.start()
        print("Server started")

    def stop_server(self):
        print("Stopping Server")
        self.server.stop()

        self.server_thread.quit()
        self.server_thread.wait()

        print("Server Stopped")

    def display_message(self, message):
        print(f"Adding message: {message}")
        self.text_edit.append(message)

    def display_error(self, error_message):
        self.text_edit.append(f"Error: {error_message}")


def main():
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
