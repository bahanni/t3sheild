from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton
from PyQt5.QtCore import Qt, QPoint, pyqtSlot, QSize
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QMouseEvent, QIcon, QPixmap

from ui.login_ui import Ui_Form
from src.main_window import MainWindow
from src.communication import SocketIOWorker
from src.http_thread import HttpThread

class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.client_thread = SocketIOWorker() 
        self.client_thread.start()

        self._startPos = None
        self._endPos = None
        self._tracking = False

        # initialize QPushButtons in the login window.
        self.ui.exitBtn.setFocusPolicy(Qt.NoFocus)
        self.ui.loginBtn.setFocusPolicy(Qt.NoFocus)

        # show login window when start app 
        self.ui.funcWidget.setCurrentIndex(0)

        # hide the frame and background of the app 
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Charger et afficher le loader SVG
        self.loader = QSvgWidget("static/icon/waiting.svg", self)
        self.loader.setFixedSize(QSize(90, 90))
        self.center_loader()
        self.loader.hide()

        self.refresh_connnection()
    
    def refresh_connnection(self):
        if self.client_thread.sio.connected:
            print(f"✅ Connected to server")
        else:
            print(f"❌ Not connected to server")
    
    def center_loader(self):
        """
        Fonction pour centrer le loader dans la fenêtre.
        """
        # Calculer la position du centre de la fenêtre
        window_width = self.width()
        window_height = self.height()
        loader_width = self.loader.width()
        loader_height = self.loader.height()

        # Calculer la position pour centrer le loader
        x = (window_width - loader_width) // 2
        y = (window_height - loader_height) // 2

        # Déplacer le loader au centre
        self.loader.move(x, y)

    # Make the window movable after hide window frame 
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._tracking:
            self._endPos = a0.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self._startPos = QPoint(a0.x(), a0.y())
            self._tracking = True

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    # login window 
    @pyqtSlot()
    def on_exitBtn_clicked(self):
        """
        function for exit button
        """
        self.close()

    @pyqtSlot()
    def on_registerBtn_clicked(self):
        """
        function for going to register page
        """
        self.ui.funcWidget.setCurrentIndex(1)

    @pyqtSlot()
    def on_loginBtn_clicked(self):
        """
        function for login app
        """
        self.ui.loginBtn.setEnabled(False)
        self.loader.show()

        username = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text().strip()

        # check if input username and password.
        if not username and not password:
            self.warning_messagebox("Please input username and password")
            return
        
        url = "http://185.255.131.80:8000/t3shield/api/login"
        payload = {
            'username': username,
            'password': password
        }

        self.thread = HttpThread(url, payload)
        self.thread.finished.connect(self.on_login_response)
        self.thread.start()

    def on_login_response(self, success, data):
        if success:
            self.main_window = MainWindow(data=data, client_thread=self.client_thread)
            self.main_window.show()
            if self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
            self.thread = None 
            self.close()
        else:
            error = data.get("detail") or "Échec de la connexion."
            self.warning_messagebox(error)
            self.ui.lineEdit.clear()
            self.ui.lineEdit_2.clear()
        self.ui.loginBtn.setEnabled(True)
        self.loader.hide()

    def warning_messagebox(self, content):
        """
        Common messagebox function
        """
        # Create QMessageBox
        msgBox = QMessageBox(self)
        msgBox.setWindowIcon(QIcon("./static/icon/icon.png"))
        msgBox.setIconPixmap(QPixmap("./static/icon/exclamation-48.ico"))
        msgBox.setWindowTitle("Warning")
        msgBox.setText(content)
        
        # Create and style custom Close button
        close_button = QPushButton("Fermer")
        close_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #4d4d4d;
                background-color: #202020;
                color: #d1d1d1;
                border-radius: 5px;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: #777;
            }
        """)
        msgBox.addButton(close_button, QMessageBox.AcceptRole)
        
        msgBox.exec_()







