from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtSvg import QSvgWidget

from ui.main_ui import Ui_MainWindow
from src.windows.general import GeneralAnalyse
from src.windows.mobility import MobilityAnalyse
from src.windows.configuration import Configuration
from src.utils.datamodel import DataModel

import json
import os

class MainWindow(QMainWindow):
    def __init__(self, data, client_thread):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.data = data
        self.client_thread = client_thread

        self.dataModel = DataModel(self.data)

        # Set default page
        self.ui.stackedWidget.setCurrentIndex(0)
        
        svg_widget = QSvgWidget("./static/icon/svg.svg")
        svg_widget.setFixedSize(180, 190)
        self.ui.Layout_svg.setContentsMargins(0, 20, 0, 20)
        self.ui.Layout_svg.addWidget(svg_widget, alignment=Qt.AlignCenter)
        
        # Charger et afficher le loader SVG
        self.loader = QSvgWidget("./static/icon/waiting.svg", self)
        self.loader.setFixedSize(QSize(90, 90))
        self.center_loader()
        self.loader.raise_()
        self.loader.hide()

        # Charger la config JSON
        json_path = os.path.join(os.path.dirname(__file__), '..', 'configurations/configuration.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)

        # Les items combos
        self.ui.comboBox_aref.addItems(cfg.get("AREF", []))
        self.ui.comboBox_dp.addItems(cfg.get("DP", []))
        self.ui.comboBox_ville.addItems(cfg.get("ville", []))
        self.ui.comboBox_lycee.addItems(cfg.get("Lycee", []))
        self.ui.comboBox_salle.addItems(cfg.get("Salle", []))
        self.ui.comboBox_matiere.addItems(cfg.get("Matiere", []))

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
        self.old_pos = None
        self.mouse_pressed = False 

        # Page navigation with index numbers
        general_page  = GeneralAnalyse(self.dataModel, self.client_thread, self.ui.stackedWidget,
                                       self.ui.pushButton_retour_g, self.ui.tableWidget_g, 
                                       self.ui.label_ctr_gsm_g, self.ui.progressBar_g,
                                       self.ui.label_counter_g, self.ui.pushButton_enregistrer_g,
                                       self.ui.pushButton_lancer_g, self.loader)

        mobility_page = MobilityAnalyse(self.dataModel, self, self.client_thread, self.ui.stackedWidget, 
                                        self.ui.pushButton_valider, self.ui.pushButton_effacer,
                                        self.ui.pushButton_retour_mh, self.ui.pushButton_envoyer_r_m,
                                        self.ui.label_mul_m, self.ui.pushButton_lancer_m, self.ui.pushButton_stop_m,
                                        self.ui.label_analyse_en_cours, self.ui.frame_2)

        config_page   = Configuration(self.dataModel, self.ui.stackedWidget, self.ui.comboBox_rows, self.ui.comboBox_cols,
                                      self.ui.comboBox_aref, self.ui.comboBox_dp, self.ui.comboBox_ville, 
                                      self.ui.comboBox_lycee, self.ui.comboBox_salle, 
                                      self.ui.comboBox_matiere, self.ui.pushButton_enregistrer,
                                      self.ui, self.loader, mobility=mobility_page)

        self.pages = [ general_page, mobility_page, config_page ]

        # Connect buttons to change pages by index number
        self.ui.pushButton_home.clicked.connect(lambda: self.change_page(0)) 
        self.ui.toolButton_mobility.clicked.connect(lambda: self.change_page(1))
        self.ui.toolButton_general.clicked.connect(lambda: self.change_page(2))
        self.ui.toolButton_configuration.clicked.connect(lambda: self.change_page(3))
        self.ui.pushButton_config.clicked.connect(lambda: self.change_page(3))
        self.ui.toolButton_test.clicked.connect(lambda: self.change_page(4))
        self.ui.pushButton_exit.clicked.connect(lambda: self.disconnection())

        self.ui.label_aref.setText(self.data.get('aref'))
        self.ui.label_dp.setText(self.data.get('dp'))
        self.ui.label_ville.setText(self.data.get('ville'))
        self.ui.label_lycee.setText(self.data.get('lycee'))
        self.ui.label_salle.setText(f"{self.data.get('salle')} ({self.data.get('cols')}x{self.data.get('roos')})")
        self.ui.label_matiere.setText(self.data.get('matiere'))
        print(self.data)

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
        if event.button() == Qt.LeftButton and not self.isFullScreen():
            self.old_pos = event.globalPos()
            self.mouse_pressed = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_pressed and self.old_pos and not self.isFullScreen():
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
        from src.windows.login import LoginWindow
        if self.client_thread:
            self.client_thread.stop_m()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()