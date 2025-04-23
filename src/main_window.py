from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtSvg import QSvgWidget

from ui.main_ui import Ui_MainWindow
from src.general_window import GeneralAnalyse
from src.mobility_window import MobilityAnalyse
from src.configuration_window import Configuration

class MainWindow(QMainWindow):
    def __init__(self, data, client_thread):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.client_thread = client_thread
        
        # Charger et afficher le loader SVG
        self.loader = QSvgWidget("static/icon/waiting.svg", self)
        self.loader.setFixedSize(QSize(90, 90))
        self.center_loader()
        self.loader.raise_()
        self.loader.hide()

        # Remove the title bar and set the window to be frameless
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ui.maxmize_btn.setCheckable(True)

        # Connect the custom minimize, maximize/restore, and close buttons to their functions
        self.ui.minimize_btn.clicked.connect(self.showMinimized)
        self.ui.maxmize_btn.clicked.connect(self.toggle_maximize_restore)
        self.ui.close_btn.clicked.connect(self.handle_close)

        self.toggle_maximize_restore()

        # Variables to keep track of the window dragging
        self.old_pos = None  # Initial position of the window
        self.mouse_pressed = False  # Flag to track if the mouse is pressed

        # Page navigation with index numbers
        self.pages = [
            GeneralAnalyse( data, self.client_thread, self.ui.stackedWidget, self.ui.pushButton_retour_g, self.ui.tableWidget_g, 
                            self.ui.label_ctr_gsm_g, self.ui.progressBar_g, self.ui.label_counter_g, 
                            self.ui.pushButton_enregistrer_g, self.ui.pushButton_lancer_g, self.loader),

            MobilityAnalyse(data, self, self.client_thread, self.ui.stackedWidget, self.ui.pushButton_retour_mh, self.ui.tableWidget_m, 
                            self.ui.pushButton_annoter_m, self.ui.pushButton_envoyer_r_m, self.ui.label_mul_m, self.ui.label_counter_m_,
                            self.ui.pushButton_lancer_m, self.ui.pushButton_stop_m, self.ui.label_analyse_en_cours),
                            
            Configuration(data, self.ui.stackedWidget, self.ui.lineEdit_aref, self.ui.lineEdit_dp, self.ui.lineEdit_ville, 
                          self.ui.lineEdit_lycee, self.ui.lineEdit_verificateur, self.ui.comboBox_salle, self.ui.comboBox_matiere,
                          self.ui.pushButton_enregistrer, self.ui, self.loader)
            ]

        # Set default page
        self.ui.stackedWidget.setCurrentIndex(0)

        # Connect buttons to change pages by index number
        self.ui.pushButton_home.clicked.connect(lambda: self.change_page(0)) 
        self.ui.toolButton_mobility.clicked.connect(lambda: self.change_page(1))
        self.ui.toolButton_general.clicked.connect(lambda: self.change_page(2))
        self.ui.pushButton_config.clicked.connect(lambda: self.change_page(3))

        self.ui.pushButton_exit.clicked.connect(lambda: self.disconnection())

        self.ui.label_aref.setText(data.get('aref'))
        self.ui.label_dp.setText(data.get('dp'))
        self.ui.label_ville.setText(data.get('ville'))
        self.ui.label_lycee.setText(data.get('lycee'))
        self.ui.label_salle.setText(data.get('salle'))

        self.refresh_connnection()
    
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

    def resizeEvent(self, event):
        """
        Centrer le loader chaque fois que la taille de la fenêtre change.
        """
        super().resizeEvent(event)
        self.center_loader()

    def refresh_connnection(self):
        if self.client_thread.sio.connected:
            print(f"✅ Connected to server")
        else:
            print(f"❌ Not connected to server")

    def handle_close(self):
        if self.client_thread:
            self.client_thread.stop_m()
        self.close()


    def toggle_maximize_restore(self):
        # Toggle between fullscreen and normal size
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and not self.isFullScreen():  # Vérifier si la fenêtre n'est pas en plein écran
            self.old_pos = event.globalPos()
            self.mouse_pressed = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_pressed and self.old_pos and not self.isFullScreen():  # Vérifier si la fenêtre n'est pas en plein écran
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False


    def change_page(self, index):
        # Change the page by index
        self.ui.stackedWidget.setCurrentIndex(index)

    def disconnection(self):
        from src.login_window import LoginWindow
        if self.client_thread:
            self.client_thread.stop_m()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

