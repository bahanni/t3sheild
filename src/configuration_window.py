from PyQt5.QtWidgets import QMessageBox, QPushButton
from PyQt5.QtGui import QIcon, QPixmap
from src.http_thread import HttpThread

import requests

class Configuration:
    def __init__(self, data, stacked_widget, line_edit_aref, line_edit_dp, line_edit_ville,
                 line_edit_lycee, line_edit_verificateur, combo_box_salle, combo_box_matiere,
                 push_button_enregistrer, ui, loader):
        self.loader = loader
        self.data = data
        self.ui = ui 
        self.stacked_widget = stacked_widget
        self.line_edit_aref = line_edit_aref
        self.line_edit_dp = line_edit_dp
        self.line_edit_ville = line_edit_ville
        self.line_edit_lycee = line_edit_lycee
        self.line_edit_verificateur = line_edit_verificateur
        self.combo_box_salle = combo_box_salle
        self.combo_box_matiere = combo_box_matiere
        self.push_button_enregistrer = push_button_enregistrer

        # You can now connect signals, set defaults, etc.
        self.push_button_enregistrer.clicked.connect(self.save_configuration)

    def save_configuration(self):
        self.push_button_enregistrer.setDisabled(True)
        self.loader.show()
        # Récupérer les valeurs des champs
        aref = self.line_edit_aref.text()
        dp = self.line_edit_dp.text()
        ville = self.line_edit_ville.text()
        lycee = self.line_edit_lycee.text()
        verificateur = self.line_edit_verificateur.text()
        salle = self.combo_box_salle.currentText()
        matiere = self.combo_box_matiere.currentText()

        # Construire le dictionnaire JSON (payload)
        payload = {
            "id_verificateur": self.data.get('id_verificateur'),
            "aref": aref,
            "dp": dp,
            "Ville": ville,
            "Lycée": lycee,
            "Vérificateur": verificateur,
            "Salle": salle,
            "Matière": matiere
        }

        # Afficher ou utiliser le payload
        print("Configuration enregistrée :", payload)

        url = "http://185.255.131.80:8000/t3shield/api/send_configurations"
        self.thread = HttpThread(url, payload)
        self.thread.finished.connect(self.on_general_response)
        self.thread.start()

    def on_general_response(self, success, data):
        self.push_button_enregistrer.setDisabled(False)
        self.loader.hide()
        try:
            if success:
                self.warning_messagebox("./static/icon/check-mark-2-48.ico", "Information", "Configuration enregistrée")
                self.ui.label_aref.setText(data.get('aref'))
                self.ui.label_dp.setText(data.get('dp'))
                self.ui.label_ville.setText(data.get('ville'))
                self.ui.label_lycee.setText(data.get('lycee'))
                self.ui.label_salle.setText(data.get('salle'))
            else:
                error = data.get("detail") or "Échec de la connexion."
                self.warning_messagebox("./static/icon/exclamation-48.ico", "Avertissement", error)

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion : {str(e)}")

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