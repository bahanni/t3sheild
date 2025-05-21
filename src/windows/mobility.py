from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject, Qt, pyqtSlot, QDateTime
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QApplication,
                             QSpacerItem, QSizePolicy)

from src.utils.http_thread import HttpThread
from src.utils.gen_excel import generate_styled_excel
from src.utils.matrix import matrice_transitions

import requests

class MyLineEdit(QLineEdit):
    def __init__(self, row, col, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row = row
        self.col = col
        self.k = 2

        # Style enregistré avant focusIn
        self.default_style = self.styleSheet()
        # Flag + style à réappliquer après focusOut
        self.is_validated = False
        self.validation_style = ""

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # On enregistre le style courant (potentiellement validé)
        self.default_style = self.styleSheet()

        # Flèche gauche ou droite
        if self.col < self.k:
            self.setStyleSheet("""
                QLineEdit {
                    padding-right: 25px;
                    height: 30px;
                    background-image: url(./static/icon/left_arrow.svg);
                    background-repeat: no-repeat;
                    background-position: right center;
                    background-origin: content;
                    background-clip: padding;
                    padding-right: 30px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLineEdit {
                    padding-left: 25px;
                    height: 30px;
                    background-image: url(./static/icon/right_arrow.svg);
                    background-repeat: no-repeat;
                    background-position: left center;
                    background-origin: content;
                    background-clip: padding;
                    padding-left: 30px;
                }
            """)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.is_validated:
            # si on avait validé, on remet la bordure validée
            self.setStyleSheet(self.validation_style)
        else:
            # sinon on revient au style d'avant focusIn
            self.setStyleSheet(self.default_style)

    def applyValidationStyle(self):
        """
        Appelé depuis MobilityAnalyse.valider()
        : vert si texte non vide, jaune sinon
        """
        if self.text().strip():
            style = "border: 2px solid lightgreen;"
        else:
            style = "border: 2px solid yellow;"

        self.validation_style = style
        self.is_validated = True
        self.setStyleSheet(style)

class MobilityAnalyse(QObject):
    data_annotation = pyqtSignal(list)

    def __init__(self, dataModel, main_window, client_thread, stacked_widget, pushButton_valider, 
                 pushButton_effacer, pushButton_retour_m, pushButton_envoyer_r_m, label_mul_m, 
                 pushButton_lancer_m, pushButton_stop_m, label_analyse_en_cours, frame_2):
        super().__init__()

        self.timestamp = str()
        self.operator = str()
        self.frequency = str()
        self.power = str()
        self.risk_level = str()
        self.color = str()
        self.style = str()
        self.validation = False
        self.matrice = []
        self.risque = False

        self.dataModel = dataModel
        self.data = self.dataModel.get()
        self.rows = int(self.data.get('roos'))
        self.cols = int(self.data.get('cols'))

        self.frame_2 = frame_2
        self.client_thread = client_thread
        self.last_notification = None
        self.main_window = main_window
        self.stacked_widget = stacked_widget
        self.pushButton_retour_m = pushButton_retour_m
        self.pushButton_envoyer_m = pushButton_envoyer_r_m
        self.label_mul_m = label_mul_m
        self.pushButton_lancer_m = pushButton_lancer_m
        self.pushButton_stop_m = pushButton_stop_m
        self.label_analyse_en_cours = label_analyse_en_cours
        self.pushButton_valider = pushButton_valider
        self.pushButton_effacer = pushButton_effacer

        self.pushButton_retour_m.clicked.connect(lambda: self.change_page(0))
        self.pushButton_envoyer_m.clicked.connect(lambda: self.send_repport())
        self.pushButton_lancer_m.clicked.connect(lambda:  self.start_analyse())
        self.pushButton_valider.clicked.connect(lambda:  self.valider())
        self.pushButton_effacer.clicked.connect(lambda:  self.effacer())

        self.pushButton_valider.setFocusPolicy(Qt.NoFocus)
        self.pushButton_effacer.setFocusPolicy(Qt.NoFocus)

        self.pushButton_stop_m.setDisabled(True)
        self.label_analyse_en_cours.hide()

        self.client_thread.mobility_analyse_s.connect(self.handle_data)
        
        self.initUI_matrix()
        self.fixed_status = 'L'
        self.fixed_power  = -55

        self.matrix_inputs = [[QLineEdit() for _ in range(self.cols)] 
                              for _ in range(self.rows)]
        
        self.matrice = [[None for _ in range(self.cols)]
                        for _ in range(self.rows)]

        if self.rows and self.cols:
            self.create_matrix(self.rows, self.cols)

        self.dataModel.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self, new_data):
        self.data = new_data

    def effacer(self):
        current = QApplication.focusWidget()

        if isinstance(current, QLineEdit):
            # Recherche de la position (r, c) dans self.matrix_inputs
            for r, row in enumerate(self.matrix_inputs):
                if current in row:
                    c = row.index(current)
                    break
            else:
                return
            
            # Affectation dans la matrice 2D
            self.matrice[r][c] = ("L", "0", "-100")
            print(self.matrice)
            current.setStyleSheet("border: 2px solid rgb(100, 100, 100);")
            current.clear()
        else:
            self.warning_messagebox("Le focus n'est pas sur un champ de saisie.")

    def valider(self):
        current = QApplication.focusWidget()
        if not isinstance(current, QLineEdit):
            self.warning_messagebox("Le focus n'est pas sur un champ de saisie.")
            return

        # Récupération du CNE, status, power
        cne_text = current.text().strip()
        cne = cne_text if cne_text else 0
        status = self.fixed_status
        power  = self.fixed_power

        current.applyValidationStyle()

        # Recherche de la position (r, c) dans self.matrix_inputs
        for r, row in enumerate(self.matrix_inputs):
            if current in row:
                c = row.index(current)
                break
        else:
            return
        
        # Affectation dans la matrice 2D
        if cne:
            self.matrice[r][c] = (status, cne, power)
        else:
            self.matrice[r][c] = ("L", "0", "-100")
        
        print(self.matrice)

        self._tab_par_colonne(current, 2)


    def _tab_par_colonne(self, widget, k):
        """
        Déplace le focus dans la même colonne en respectant la règle :
        - si c < k : on descend
        - si c >= k : on remonte
        Quand on dépasse en haut ou en bas, on passe à la colonne suivante
        (avec wrap-around) et on s’aligne sur l’extrémité opposée.
        """
        # retrouver r, c
        for r, row in enumerate(self.matrix_inputs):
            if widget in row:
                c = row.index(widget)
                break
        else:
            return

        n_rows = len(self.matrix_inputs)
        n_cols = len(self.matrix_inputs[0]) if n_rows else 0

        print(n_rows, n_cols)

        # déterminer le sens pour cette colonne
        descendre = (c < k)

        # calculer r_next, c_next
        if descendre:
            r_next = r + 1
            if r_next >= n_rows:
                # dépassement bas → nouvelle colonne
                c_next = (c + 1) % n_cols
                # positionner au bord opposé de la nouvelle colonne
                if c_next < k:
                    r_next = 0
                else:
                    r_next = n_rows - 1
            else:
                c_next = c

        else:
            r_next = r - 1
            if r_next < 0:
                # dépassement haut → nouvelle colonne
                c_next = (c + 1) % n_cols
                if c_next < k:
                    r_next = 0
                else:
                    r_next = n_rows - 1
            else:
                c_next = c

        # Focus sur le widget suivant
        next_widget = self.matrix_inputs[r_next][c_next]
        next_widget.setFocus()

    def start_analyse(self):
        self.pushButton_stop_m.setDisabled(False)
        self.pushButton_lancer_m.setDisabled(True)
        self.label_analyse_en_cours.show()
        self.client_thread.start_mobility_analysis()
        
    def stop_analyse(self):
        self.pushButton_stop_m.setDisabled(True)
        self.pushButton_lancer_m.setDisabled(False)
        self.label_analyse_en_cours.hide()
        self.label_mul_m.setText("L'analyse est arrêtée")
        self.client_thread.stop_m()

    def send_repport(self):
        try:

            flat = [
                self.matrice[r][c]
                for r in range(len(self.matrice))
                for c in range(len(self.matrice[0]))
            ]
            print("\nMatrice finale (signal, CNE) :")
            print(flat)
            finale = matrice_transitions(flat, n_col=self.cols, neighbor='right')

            print("\nMatrice finale (signal, CNE) :")
            print(finale)

            date_str = QDateTime.currentDateTime().toString("yyyy_MM_dd_HH-mm-ss")
            generate_styled_excel(flat, finale, date_str, date_str)

            QMessageBox.information(self.frame_2, "Résultat", "La matrice a été affichée dans la console.")

        except ValueError as e:
            QMessageBox.warning(self.frame_2, "Erreur",
                                f"Veuillez entrer des CNE valides.\nDétails : {e}")

    def send_to_server(self, data_map, data):
        # Construire le dictionnaire JSON (payload)
        payload = {
            "id_verificateur": data_map.get("id_verificateur"),
            "salle":           data_map.get("salle"),
            "matiere":         data_map.get("matiere"),
            "aref":            data_map.get("aref"),
            "dp":              data_map.get("dp"),
            "ville":           data_map.get("ville"),
            "lycee":           data_map.get("lycee"),
            "data":            data
        }

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

    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def warning_messagebox(self, content):
        """
        Affiche un QMessageBox stylé sans parent explicite.
        """
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Attention")
        msgBox.setText(content)

        # Icône personnalisée (facultatif)
        msgBox.setWindowIcon(QIcon("./static/icon/icon.png"))

        # Bouton Fermer personnalisé
        close_button = QPushButton("Fermer", msgBox)
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
        
    
    def handle_data(self, data_json):
        import json
        data = json.loads(data_json)

        # Affectation aux variables
        self.timestamp = data["timestamp"]
        self.operator = data["operator"]
        self.frequency = data["frequency_mhz"]
        self.power = data["power_dbm"]
        self.risk_level = data["risk_level"]
        self.color = data["color"]
        self.risque = data["risque"]

        self.label_mul_m.setText(f"{self.risk_level} {self.power}")

    def initUI_matrix(self):
        # Trouver le layout existant de frame_2 (s'il existe)
        existing_layout = self.frame_2.layout()
        
        # Si pas de layout, créer un nouveau
        if existing_layout is None:
            existing_layout = QVBoxLayout(self.frame_2)
        
        # Conteneur pour la matrice
        matrix_container = QWidget()
        matrix_layout = QVBoxLayout(matrix_container)
        dim_layout = QHBoxLayout()

        # Section pour la matrice
        self.matrix_layout = QGridLayout()
        self.matrix_layout.setVerticalSpacing(30)
        self.matrix_layout.setHorizontalSpacing(50)
        self.matrix_widget = QWidget()
        self.matrix_widget.setLayout(self.matrix_layout)
        
        # Ajout des widgets au layout de la matrice
        matrix_layout.addWidget(self.matrix_widget)
        matrix_layout.addLayout(dim_layout)

        # Ajouter le conteneur de matrice au layout existant
        existing_layout.addWidget(matrix_container)
        
        # Liste pour stocker les références aux champs de saisie
        self.matrix_inputs = []

    @pyqtSlot(int, int)
    def create_matrix(self, rows, cols):
        self.rows = rows
        self.cols = cols
        # Effacer la matrice existante
        self.clear_matrix_layout()
        
        # Créer des champs de saisie pour chaque élément de la matrice
        self.matrix_inputs = []
        
        # Ajouter les en-têtes de colonnes (centrés)
        for c in range(cols):
            col_header = QLabel(f"Colonne {c+1}")
            # on n’appelle plus setAlignment ici
            self.matrix_layout.addWidget(
                col_header,
                0, c+1,
                Qt.AlignCenter
            )
        
        # Ajouter les en-têtes de lignes (droite + centré vertical) et les champs de saisie
        for r in range(rows):
            row_inputs = []
            
            # En-tête de ligne
            row_header = QLabel(f"Ligne {r+1}")
            self.matrix_layout.addWidget(
                row_header,
                r+1, 0,
                Qt.AlignRight | Qt.AlignVCenter
            )
            
            for c in range(cols):
                # Utilise MyLineEdit pour chaque cellule
                input_field = MyLineEdit(r, c)
                input_field.setAlignment(Qt.AlignCenter)
                input_field.setMinimumSize(40, 25)
                self.matrix_layout.addWidget(input_field, r+1, c+1)
                row_inputs.append(input_field)

            self.matrix_inputs.append(row_inputs)
        
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.matrix_layout.addItem(vertical_spacer, rows + 1, 0, 1, cols + 1)
    
    def clear_matrix_layout(self):
        while self.matrix_layout.count():
            item = self.matrix_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()