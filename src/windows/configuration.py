from PyQt5.QtWidgets import (QMessageBox, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QObject, pyqtSignal

from src.utils.http_thread import HttpThread

import requests

class Configuration(QObject):
    trigger_matrix = pyqtSignal(int, int)

    def __init__(self, dataModel, stacked_widget, comboBox_rows, comboBox_cols,
                 comboBox_aref, comboBox_dp, comboBox_ville,
                 comboBox_lycee, comboBox_salle, comboBox_matiere,
                 push_button_enregistrer, ui, loader,
                 mobility, frame_4=None):
        super().__init__()

        self.dataModel = dataModel
        self.data = self.dataModel.get()
        self.loader = loader
        self.ui = ui 
        self.stacked_widget = stacked_widget
        self.comboBox_rows = comboBox_rows 
        self.comboBox_cols = comboBox_cols
        self.comboBox_aref = comboBox_aref
        self.comboBox_dp = comboBox_dp
        self.comboBox_ville = comboBox_ville
        self.comboBox_lycee = comboBox_lycee
        self.comboBox_salle = comboBox_salle
        self.comboBox_matiere = comboBox_matiere
        self.push_button_enregistrer = push_button_enregistrer
        self.mobility = mobility

        self.trigger_matrix.connect(self.mobility.create_matrix)
        self.push_button_enregistrer.clicked.connect(self.save_configuration)        

    def warning_messagebox(self, check_mark, title, content):
        """
        Common messagebox function
        """
        # Create QMessageBox
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QIcon("./static/icon/icon.png"))
        msgBox.setIconPixmap(QPixmap(check_mark))
        msgBox.setWindowTitle(title)
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

    def save_configuration(self):

        self.push_button_enregistrer.setDisabled(True)
        self.loader.show()
        aref         = self.comboBox_aref.currentText()
        dp           = self.comboBox_dp.currentText()
        ville        = self.comboBox_ville.currentText()
        lycee        = self.comboBox_lycee.currentText()
        salle        = self.comboBox_salle.currentText()
        matiere      = self.comboBox_matiere.currentText()
        rows         = self.comboBox_rows.currentText()
        cols         = self.comboBox_cols.currentText()

        # Construire le dictionnaire JSON (payload)
        payload = {
            "id_verificateur": self.data.get('id_verificateur'),
            "aref": aref,
            "dp": dp,
            "Ville": ville,
            "Lycée": lycee,
            "Salle": salle,
            "Matière": matiere,
            "cols": cols,
            "roos": rows
        }

        # Afficher ou utiliser le payload
        print("Configuration enregistrée :", payload)

        url = "http://185.255.131.80:8000/t3shield/api/send_configurations"
        self.thread = HttpThread(url, payload)
        self.thread.finished.connect(self.on_general_response)
        self.thread.start()

        self.trigger_matrix.emit(int(rows), int(cols))

    def on_general_response(self, success, data):
        self.push_button_enregistrer.setDisabled(False)
        self.loader.hide()
        try:
            if success:
                self.dataModel.update(data)
                self.warning_messagebox("./static/icon/check-mark-2-48.ico", "Information", "Configuration enregistrée")
                self.ui.label_aref.setText(data.get('aref'))
                self.ui.label_dp.setText(data.get('dp'))
                self.ui.label_ville.setText(data.get('ville'))
                self.ui.label_lycee.setText(data.get('lycee'))
                self.ui.label_salle.setText(f"{data.get('salle')} ({data.get('cols')}x{data.get('roos')})")
                self.ui.label_matiere.setText(data.get('matiere'))

            else:
                error = data.get("detail") or "Échec de la connexion."
                self.warning_messagebox("./static/icon/exclamation-48.ico", "Avertissement", error)

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion : {str(e)}")
            self.warning_messagebox("./static/icon/exclamation-48.ico", "Erreur", str(e))