from PyQt5.QtGui import QMouseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QMessageBox, QPushButton

from src.http_thread import HttpThread
from src.database import ConnectSQLite
from ui.annotation_ui import Ui_Annotation

import requests


class AnnotationWindow(QMainWindow):
    def __init__(self, _data, timestamp, operator, frequency, power, risk_level, color, risque, parent=None):
        super(AnnotationWindow, self).__init__()

        self.ui = Ui_Annotation()
        self.ui.setupUi(self)

        self.timestamp = timestamp
        self.operator = operator
        self.frequency = frequency
        self.power = power
        self.risk_level = risk_level
        self.color = color
        self.risque = risque

        self.sql = ConnectSQLite()

        self.ui.maxmize_btn.setCheckable(True)

        # Connect the custom minimize, maximize/restore, and close buttons to their functions
        self.ui.minimize_btn.clicked.connect(self.showMinimized)
        self.ui.maxmize_btn.clicked.connect(self.toggle_maximize_restore)
        self.ui.close_btn.clicked.connect(self.close)

        # Remove the title bar and set the window to be frameless
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.ui.label_title.setText(f"Annotation")
        self.ui.pushButton_annoter.clicked.connect(lambda: self.add_cne(_data)) 
        self.ui.pushButton_sortir.clicked.connect(lambda: self.close())
        self.parent = parent

        # Charger et afficher le loader SVG
        self.loader = QSvgWidget("static/icon/waiting.svg", self)
        self.loader.setFixedSize(QSize(90, 90))
        self.center_loader()
        self.loader.raise_()
        self.loader.hide()

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

    def add_cne(self, _data):
        self.loader.show()
        self.ui.pushButton_annoter.setDisabled(True)
        cne = self.ui.lineEdit_cin.text()
        
        if not cne:
            self.loader.hide()
            self.warning_messagebox(content="Veuillez entrer CNE.")
            self.ui.pushButton_annoter.setDisabled(False)
            return
        
        result = self.sql.check_cne(cne)

        if result:
            self.loader.hide()
            self.warning_messagebox(content="The CNE is already in database. Please try another one.")
            self.ui.pushButton_annoter.setDisabled(False)
            return
        
        # date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        success = self.sql.add_to_list_annotation(cne, self.timestamp, self.risk_level, self.operator)

        print(success, self.risque)

        if success:
            data = self.sql.get_list_annotation()
            self.parent.data_annotation.emit(data)
            if self.risque:
                self.send_to_server(_data, cne)
            self.close()
        elif not success:
            QMessageBox.critical(self, "Erreur", "Échec de l'enregistrement dans la base de données.")
        self.ui.pushButton_annoter.setDisabled(False)
        self.loader.hide()

    def send_to_server(self, _data, cne):
        # Construire le dictionnaire JSON (payload)
        payload = {
                    "id_verificateur": _data.get('id_verificateur'),
                    "salle": _data.get('salle'),
                    "cne": cne,
                    "timestamp": self.timestamp,
                    "operator": self.operator,
                    "frequency": self.frequency,
                    "power": self.power,
                    "risk_level": self.risk_level,
                    "aref": _data.get('aref'),
                    "dp": _data.get('dp'),
                    "ville": _data.get('ville'),
                    "lycee": _data.get('lycee')
                }

        # Afficher ou utiliser le payload
        print(payload)

        url = "http://185.255.131.80:8000/t3shield/api/send_mobility_analysis"
        self.thread = HttpThread(url, payload)
        self.thread.finished.connect(self.on_general_response)
        self.thread.start()

    def on_general_response(self, success, data):
        try:
            if not success:
                error = data.get("detail") or "Échec de la connexion."
                self.warning_messagebox(str(error))

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion : {str(e)}")

    def warning_messagebox(self, content):
        """
        Custom styled QMessageBox with QPushButton
        """
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


    def toggle_maximize_restore(self):
        # Toggle between fullscreen and normal size
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.mouse_pressed = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_pressed and self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
