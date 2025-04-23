from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, QObject, QDateTime, Qt

# from pyqttoast import Toast, ToastPreset, ToastPosition

from src.annotation_window import AnnotationWindow
from src.database import ConnectSQLite
from src.gen_excel import *

# import time 
class MobilityAnalyse(QObject):
    data_annotation = pyqtSignal(list)

    def __init__(self, _data, main_window, client_thread, stacked_widget, pushButton_retour_m, tableWidget_m,
                    pushButton_annoter_m, pushButton_envoyer_r_m, label_mul_m, label_counter_m, pushButton_lancer_m,
                    pushButton_stop_m, label_analyse_en_cours):
        super().__init__()

        self.sql = ConnectSQLite()

        self.timestamp = str()
        self.operator = str()
        self.frequency = str()
        self.power = str()
        self.risk_level = str()
        self.color = str()
        self.risque = False

        self.client_thread = client_thread
        self.last_notification = None
        self.main_window = main_window
        self.stacked_widget = stacked_widget
        self.tableWidget_m = tableWidget_m
        self.pushButton_annoter_m = pushButton_annoter_m
        self.pushButton_retour_m = pushButton_retour_m
        self.pushButton_envoyer_m = pushButton_envoyer_r_m
        # self.progressBar_generale_m = progressBar_generale_m
        # self.progressBar_generale_p_m = progressBar_generale_p_m

        # self.label_blink_m = label_blink_m
        # self.label_detection_m = label_detection_m
        self.label_mul_m = label_mul_m
        self.label_counter_m = label_counter_m
        self.pushButton_lancer_m = pushButton_lancer_m
        # self.label_progress_m = label_progress_m
        # self.label_progress_p_m =label_progress_p_m
        self.pushButton_stop_m = pushButton_stop_m
        self.label_analyse_en_cours = label_analyse_en_cours

        self.tableWidget_m.resizeColumnsToContents()
        self.tableWidget_m.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_m.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.pushButton_retour_m.clicked.connect(lambda: self.change_page(0))
        self.pushButton_annoter_m.clicked.connect(lambda: self.annotation(_data))
        self.pushButton_envoyer_m.clicked.connect(lambda: self.send_repport())
        self.pushButton_lancer_m.clicked.connect(lambda:  self.start_analyse())
        self.pushButton_stop_m.clicked.connect(lambda:  self.stop_analyse())

        self.pushButton_stop_m.setDisabled(True)
        self.pushButton_annoter_m.setDisabled(True)
        self.label_analyse_en_cours.hide()
        # self.progressBar_generale_m.setValue(0)
        # self.progressBar_generale_p_m.setValue(0)

        data = self.sql.get_list_annotation()
        self.update_table_annotation(data)
        self.data_annotation.connect(self.update_table_annotation)

        self.client_thread.mobility_analyse_s.connect(self.handle_data)

    def start_analyse(self):
        self.pushButton_stop_m.setDisabled(False)
        self.pushButton_annoter_m.setDisabled(False)
        self.pushButton_lancer_m.setDisabled(True)
        self.label_analyse_en_cours.show()
        self.client_thread.start_mobility_analysis()
        
    
    def stop_analyse(self):
        self.pushButton_stop_m.setDisabled(True)
        self.pushButton_annoter_m.setDisabled(True)
        self.pushButton_lancer_m.setDisabled(False)
        self.label_analyse_en_cours.hide()
        self.tableWidget_m.setRowCount(50)
        self.label_mul_m.setText("L'analyse est arrêtée")
        self.label_mul_m.setStyleSheet(f"""
                                            QLabel {{
                                                margin-bottom:10px;
                                                margin-top:10px;
                                                background: #777;
                                                font: bold 60px "Arial";
                                                color: white;
                                                border-radius: 10px;
                                                qproperty-alignment: 'AlignCenter';
                                                padding: 40px 250px 40px 250px;
                                            }}
                                        """)
        self.client_thread.stop_m()
        
    def send_repport(self):
        date = QDateTime.currentDateTime().toString("yyyy_MM_dd_HH-mm-ss")
        print(date)
        generate_styled_excel(self.tableWidget_m, date)
        self.sql.delete_all_annotations()
        data = self.sql.get_list_annotation()
        self.update_table_annotation(data)

    def annotation(self, _data):
        # Change the page by index
        self.annotation_window = AnnotationWindow(
            _data,
            timestamp=self.timestamp,
            operator=self.operator,
            frequency=self.frequency,
            power=self.power,
            risk_level=self.risk_level,
            color=self.color,
            risque=self.risque,
            parent=self
        )        
        # Mettre la fenêtre toujours au-dessus
        self.annotation_window.setWindowFlags(self.annotation_window.windowFlags() | Qt.WindowStaysOnTopHint)
        self.annotation_window.show()
        
    def change_page(self, index):
        # Change the page by index
        self.stacked_widget.setCurrentIndex(index)

    def update_table_annotation(self, message):
        self.tableWidget_m.setRowCount(len(message))

        for row, emp in enumerate(message):
            self.tableWidget_m.setItem(row, 0, QTableWidgetItem(emp['cne']))
            self.tableWidget_m.setItem(row, 1, QTableWidgetItem(emp['timestamp']))
            self.tableWidget_m.setItem(row, 2, QTableWidgetItem(emp['risk_level']))
            self.tableWidget_m.setItem(row, 3, QTableWidgetItem(emp['operator']))

        self.tableWidget_m.setRowCount(50)
        self.label_counter_m.setText(str(len(message)))
        
    # def func_label_blink_m(self):
    #     blink_timer = QTimer(self)
    #     state = {"visible": True}

    #     def toggle():
    #         self.label_blink_m.setVisible(state["visible"])
    #         state["visible"] = not state["visible"]

    #     blink_timer.timeout.connect(toggle)
    #     blink_timer.start(500)

    #     QTimer.singleShot(3000, lambda: (
    #         blink_timer.stop(),
    #         self.label_blink_m.setVisible(True)
    #     ))
    
    # def apply_progressbar_styles(self, progressBar, a, b, c, d, opacity):
    #     progressBar.setStyleSheet(f"""
    #         QProgressBar {{
    #             background-color: rgba(255, 255, 255, {opacity});
    #             border-style: none;
    #             border-radius: 10px;
    #             text-align: center;
    #             height: 70px;
    #             min-height: 70px; 
    #             color: transparent;
    #         }}

    #         QProgressBar::chunk {{
    #             border-radius: 10px;
    #             background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5,
    #                 stop:{a} rgba(0, 255, 0, {opacity}),   /* Vert entre 0 et 0.3 */
    #                 stop:{b} rgba(255, 255, 0, {opacity}), /* Jaune entre 0.3 et 0.6 */
    #                 stop:{c} rgba(255, 165, 0, {opacity}), /* Jaune fixe entre 0.3 et 0.6 */
    #                 stop:{d} rgba(255, 0, 0, {opacity}));  /* Rouge à partir de 1 */
    #         }}
    #     """)

    # def _fun(self, val_puissance):
    #     current_time = time.time()

    #     if current_time - self.last_update_time >= 1.0:
    #         self._val_precedente = val_puissance
    #         self.last_update_time = current_time

    #     return self._val_precedente
    
    # def fun(self, val_puissance):
    #     self.buffer.append((time.time(), val_puissance))
        
    #     while self.buffer and self.buffer[0][0] < time.time() - self.retard:
    #         _, value = self.buffer.pop(0)
    #         self.val_precedente = value
    #         return self._fun(value)
        
    #     return self._fun(self.val_precedente)
    
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

        self.label_mul_m.setText(self.risk_level)
        self.label_mul_m.setStyleSheet(f"""
                                            QLabel {{
                                                margin-bottom:10px;
                                                margin-top:10px;
                                                background: {self.color};
                                                font: bold 60px "Arial";
                                                color: white;
                                                border-radius: 10px;
                                                qproperty-alignment: 'AlignCenter';
                                                padding: 40px 250px 40px 250px;
                                            }}
                                        """)




        # self.progressBar_generale_m.setRange(0, 0)

        # if not saut :
        #     self.progressBar_generale_m.setValue(int(self.val_puissance))
        #     self.label_progress_m.setText(f"{self.val_puissance} %")

        # self.progressBar_generale_p_m.setValue(int(val_precedente))
        # self.label_progress_p_m.setText(f"{val_precedente} %")

        # self.label_mul_m.setText(multiples if multiples else "0")

        # Notifications basées sur les conditions
        # self.handle_notifications(self.val_puissance, val_precedente, saut)

        # if self.val_puissance > 80:
        #     self.apply_progressbar_styles(self.progressBar_generale_m, 0, 0.2, 0.3, 0.5, 255)
        # elif self.val_puissance > 30:
        #     self.apply_progressbar_styles(self.progressBar_generale_m, 0, 0.3, 0.99, 1, 255)
        # else:
        #     self.apply_progressbar_styles(self.progressBar_generale_m, 0, 0.8, 0.99, 1, 255)

        # if val_precedente > 80:
        #     self.apply_progressbar_styles(self.progressBar_generale_p_m, 0, 0.2, 0.3, 0.5, 77)
        # elif val_precedente > 30:
        #     self.apply_progressbar_styles(self.progressBar_generale_p_m, 0, 0.3, 0.99, 1, 77)
        # else:
        #     self.apply_progressbar_styles(self.progressBar_generale_p_m, 0, 0.8, 0.99, 1, 77)

        # Par défaut
        # couleur = "black"
        # bg_couleur = "blackorange"
        # texte = "Aucune détection"
        # blink_visible = False

        # if self.val_puissance > 80:
        #     couleur = "red"
        #     bg_couleur = "red"
        #     texte = "DÉTECTION FORTE"
        # elif self.val_puissance > 50:
        #     couleur = "orange"
        #     bg_couleur = "orange"
        #     texte = "DÉTECTION"

        # if not(multiples == "0") and self.val_puissance > 50:
        #     texte += " MULTIPLES"
        # if saut and self.val_puissance > 50:
        #     texte += f" {saut}"
        #     blink_visible = True
        #     self.func_label_blink_m()

        # # Appliquer les styles
        # self.label_detection_m.setText(texte)
        # self.label_detection_m.setStyleSheet(f"""
        #     color: {couleur};
        #     font: bold 30px 'Arial';
        #     line-height: 30px;
        #     letter-spacing: 1px;
        #     qproperty-alignment: AlignCenter;
        # """)

        # self.label_mul_m.setStyleSheet(f"""
        #     margin-bottom: 10px;
        #     background-color: {bg_couleur};
        #     font: bold 40px 'Arial';
        #     color: white;
        #     border-radius: 10px;
        #     qproperty-alignment: AlignCenter;
        #     padding: 40px;
        #     padding-left: 100px;
        #     padding-right: 100px;
        # """)

        # # Icône de saut
        # self.label_blink_m.setVisible(blink_visible)


    # def handle_notifications(self, val_puissance, val_precedente, saut):
    #     message = None

    #     if val_precedente is not None:
    #         # Message de pic atteint
    #         if val_puissance > 80:
    #             message = "arrêter"
    #             description = "Position optimale atteinte"
    #             style = ToastPreset.SUCCESS

    #         # Message d'approche
    #         elif val_puissance > val_precedente * 1.15:
    #             message = "Approche d'une source"
    #             description = "Continuer le déplacement"
    #             style = ToastPreset.INFORMATION

    #         # Message d'éloignement
    #         elif val_puissance < val_precedente * 0.85:
    #             message = "Éloignement de la source"
    #             description = "Revenir en arrière"
    #             style = ToastPreset.WARNING

    #     if saut == "ON":
    #         message = "Saut de fréquence détecté"
    #         description = "Attente de stabilisation"
    #         self.progressBar_generale_m.setValue(0)
    #         style = ToastPreset.ERROR
    #         duration = float('inf')
    #     elif saut == "OFF":
    #         message = "Signal stabilisé"
    #         description = "Analyse en cours"
    #         style = ToastPreset.SUCCESS
    #         duration = 3000
    #     else:
    #         duration = 3000

    #     if message and (message != self.last_notification):
    #         self.display_notification(message, description, duration, style)
    #         self.last_notification = message

    # def display_notification(self, message, description, duration, style):
    #     toast = Toast(self.main_window)
    #     toast.setDuration(duration)
    #     toast.setTitle(message)
    #     toast.setText(description)
    #     toast.applyPreset(style)
    #     toast.setPosition(ToastPosition.BOTTOM_MIDDLE)
    #     toast.setBorderRadius(3)
    #     toast.show()
