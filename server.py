import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PySide6.QtNetwork import QTcpServer, QHostAddress

go_dark = False
try:
    import qdarktheme

    go_dark = True
except Exception:
    pass


class Server(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server = QTcpServer(self)
        self.server.listen(QHostAddress.LocalHost, 12345)
        self.server.newConnection.connect(self.newConnection)

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Server")
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Set it to read-only for history
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.text_edit)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def newConnection(self):
        self.client_connection = self.server.nextPendingConnection()
        self.client_connection.readyRead.connect(self.receiveMessage)

    def receiveMessage(self):
        message = self.client_connection.readAll().data().decode()
        self.text_edit.append(f"Received: {message}")
        self.client_connection.write(f"Server received: {message}".encode())


def main():
    app = QApplication(sys.argv)

    if go_dark:
        qdarktheme.setup_theme(additional_qss="QToolTip {color: black;}")

    server = Server()
    server.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
