from PyQt5.QtWidgets import QHeaderView, QMessageBox, QPushButton
from PyQt5.QtGui import QIcon, QPixmap

import requests
import json
from src.utils.http_thread import HttpThread

class GeneralAnalyse:
    def __init__(self, dataModel, client_thread, stacked_widget, pushButton_retour_g, 
                 tableWidget_g, label_ctr_gsm_g, progressBar_g, label_counter_g, 
                 pushButton_enregistrer_g, pushButton_lancer_g, loader):
        
        self.dataModel = dataModel
        self.data = self.dataModel.get()
        self.json_data = str()
        self.loader = loader
        self.client_thread = client_thread
        self.stacked_widget = stacked_widget
        self.pushButton_retour_g = pushButton_retour_g
        self.tableWidget_g = tableWidget_g
        self.label_ctr_gsm_g = label_ctr_gsm_g
        self.progressBar_g = progressBar_g
        self.label_counter_g = label_counter_g
        self.pushButton_enregistrer_g = pushButton_enregistrer_g
        self.pushButton_lancer_g = pushButton_lancer_g

        self.progressBar_g.setValue(0)

        self.pushButton_retour_g.clicked.connect(lambda: self.change_page(0))
        self.pushButton_lancer_g.clicked.connect(lambda:  self.start_analyse())
        self.pushButton_enregistrer_g.clicked.connect(lambda:  self.send_data())
        self.pushButton_enregistrer_g.setDisabled(True)

        self.tableWidget_g.resizeColumnsToContents()
        self.tableWidget_g.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_g.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.client_thread.general_analyse_s.connect(self.handle_data)

        self.dataModel.dataChanged.connect(self.on_data_changed)

    def on_data_changed(self, new_data):
        self.data = new_data

    def send_data(self):
        url = "http://185.255.131.80:8000/t3shield/api/send_general_analysis"

        self.pushButton_enregistrer_g.setDisabled(True)
        self.loader.show()
        parsed_json_data = json.loads(self.json_data)

        payload = {
            "id_verificateur": self.data.get('id_verificateur'),
            "salle": self.data.get('salle'),
            "matiere": "math",
            "data": parsed_json_data
        }

        self.thread = HttpThread(url, payload)
        self.thread.finished.connect(self.on_general_response)
        self.thread.start()

    def on_general_response(self, success, data):
        try:
            # Envoyer les données en tant que dictionnaire JSON
            if success:
                self.tableWidget_g.clearContents()
            else:
                error = data.get("detail") or "Échec de la connexion."
                self.warning_messagebox(error)
                self.pushButton_enregistrer_g.setDisabled(False)
            self.loader.hide()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion : {str(e)}")


    def change_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        print("actualiser les donnees test:", self.data)
    
    def start_analyse(self):
        self.pushButton_lancer_g.setDisabled(True)
        self.label_ctr_gsm_g.setText("0")
        self.label_counter_g.setText("0")
        self.tableWidget_g.setRowCount(0)
        self.client_thread.start_general_analysis()
        self.progressBar_g.setRange(0, 0)
    
    def handle_data(self, data_json): 
        import json
        from PyQt5.QtWidgets import QTableWidgetItem

        self.progressBar_g.setRange(0, 100)
        self.progressBar_g.setValue(100)
        self.pushButton_lancer_g.setDisabled(False)
        
        # Charger les données JSON
        data = json.loads(data_json)

        # Récupération des entrées dans la clé "data"
        rows = data.get("data", [])

        expanded_rows = []
        total_count = 0

        for row in rows:
            date = row['Date']
            communication_type = row['type_communication']
            
            if 'Orange' in row:
                for _ in range(row['Orange']):
                    expanded_rows.append({'Date': date, 'Operateur': 'Orange', 'Type de communication': communication_type})
                total_count += row['Orange']
            
            if 'Inwi' in row:
                for _ in range(row['Inwi']):
                    expanded_rows.append({'Date': date, 'Operateur': 'Inwi', 'Type de communication': communication_type})
                total_count += row['Inwi']
            
            if 'IAM' in row:
                for _ in range(row['IAM']):
                    expanded_rows.append({'Date': date, 'Operateur': 'IAM', 'Type de communication': communication_type})
                total_count += row['IAM']

        # Affichage dans le tableau
        self.tableWidget_g.setRowCount(len(expanded_rows))

        for row, emp in enumerate(expanded_rows):
            self.tableWidget_g.setItem(row, 0, QTableWidgetItem(emp['Date']))
            self.tableWidget_g.setItem(row, 1, QTableWidgetItem(emp['Operateur']))
            self.tableWidget_g.setItem(row, 2, QTableWidgetItem(emp['Type de communication']))

        # Extraction des données affichées en JSON
        data_list = []
        row_count = self.tableWidget_g.rowCount()
        
        for row in range(row_count):
            date = self.tableWidget_g.item(row, 0).text() if self.tableWidget_g.item(row, 0) else ''
            operateur = self.tableWidget_g.item(row, 1).text() if self.tableWidget_g.item(row, 1) else ''
            type_comm = self.tableWidget_g.item(row, 2).text() if self.tableWidget_g.item(row, 2) else ''
            
            data_list.append({
                "date": date,
                "operateur": operateur,
                "type_communication": type_comm
            })

        self.json_data = json.dumps(data_list, indent=4, ensure_ascii=False)
        if self.json_data:
            self.pushButton_enregistrer_g.setDisabled(False)

        # Mise à jour du label avec le nombre d'éléments
        self.tableWidget_g.setRowCount(50)
        self.label_counter_g.setText(str(total_count))
        self.label_ctr_gsm_g.setText(str(total_count))

    def warning_messagebox(self, content):
        """
        Common messagebox function
        """
        # Create QMessageBox
        msgBox = QMessageBox()
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