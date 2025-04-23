import requests
from PyQt5.QtCore import QThread, pyqtSignal

class HttpThread(QThread):
    finished = pyqtSignal(bool, dict)

    def __init__(self, url, payload):
        super().__init__()
        self.url = url
        self.payload = payload

    def run(self):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.post(self.url, json=self.payload, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                self.finished.emit(True, response.json())
            else:
                self.finished.emit(False, response.json())
        except requests.exceptions.RequestException as e:
            self.finished.emit(False, {"error": f"Erreur de connexion : {str(e)}"})