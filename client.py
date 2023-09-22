import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QFormLayout,
)
from PySide6.QtNetwork import QTcpSocket, QHostAddress

go_dark = False
try:
    import qdarktheme

    go_dark = True
except Exception:
    pass


class Client(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.connected)
        self.socket.readyRead.connect(self.receiveMessage)

    def initUI(self):
        self.setGeometry(600, 100, 400, 300)
        self.setWindowTitle("Client")

        # Layouts
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)
        form = QFormLayout()

        # Widgets
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Set it to read-only for history

        self.input_line = QLineEdit(self)
        self.input_line.returnPressed.connect(self.sendMessage)  # Send when Return key is pressed

        # Add Widgets
        form.addRow("Message:", self.input_line)
        self.layout.addWidget(self.text_edit)
        self.layout.addLayout(form)
        self.layout.addWidget(connect_btn)

    def connect(self):
        self.socket.connectToHost(QHostAddress.LocalHost, 12345)

    def connected(self):
        self.text_edit.append("Connected to server.")

    def sendMessage(self):
        message = self.input_line.text()
        if message:
            self.text_edit.append(f"Sent: {message}")
            self.socket.write(message.encode())
            self.input_line.clear()  # Clear the input field after sending

    def receiveMessage(self):
        message = self.socket.readAll().data().decode()
        self.text_edit.append(f"Received: {message}")


def main():
    app = QApplication(sys.argv)

    if go_dark:
        qdarktheme.setup_theme(additional_qss="QToolTip {color: black;}")

    client = Client()
    client.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
