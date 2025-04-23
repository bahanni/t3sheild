from PyQt5.QtCore import QThread, pyqtSignal
import socketio
import json
import time

class SocketIOWorker(QThread):
    mobility_analyse_s = pyqtSignal(str)
    general_analyse_s = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.running = False
        self.analysis_type = ""
        self.connected = False

        # === Event handlers ===
        @self.sio.on('connect')
        def on_connect():
            self.connected = True
            print("✅ Connecté au serveur Socket.IO")

        @self.sio.on('disconnect')
        def on_disconnect():
            self.connected = False
            print("🔌 Déconnecté du serveur Socket.IO")

        @self.sio.on('analysis_started')
        def on_analysis_started(data):
            print(f"🔄 Analyse démarrée : {data}")

        @self.sio.on('mobility_data')
        def on_mobility_data(data):
            print(data)
            parsed_data = json.loads(data)
            self.mobility_analyse_s.emit(json.dumps(parsed_data)) 

        @self.sio.on('general_data')
        def on_general_data(data):
            parsed_data = json.loads(data)
            self.general_analyse_s.emit(json.dumps(parsed_data))

    def run(self):
        try:
            self.sio.connect('http://localhost:5000')
            self.running = True
            self.sio.wait()
        except Exception as e:
            print(f"❌ Erreur connexion SocketIO : {e}")

    def start_mobility_analysis(self):
        print("🚀 Tentative de démarrage de l’analyse mobilité")
        if self.connected:
            self.sio.emit('start_mobility')
            print("✅ Événement 'start_mobility' émis")
        else:
            print("❌ Impossible d'émettre 'start_mobility' : pas connecté")

    def start_general_analysis(self):
        print("🚀 Tentative de démarrage de l’analyse general")
        if self.connected:
            self.sio.emit('start_general')
            print("✅ Événement 'start_general' émis")
        else:
            print("❌ Impossible d'émettre 'start_general' : pas connecté")

    def stop_m(self):
        self.running = False
        if self.connected:
            print("⛔ STOP_M envoyé")
            self.sio.emit('stop_mobility')
        else:
            print("❌ Non connecté, 'stop_mobility' non envoyé")

    def stop_g(self):
        self.running_ = False
        if self.connected:
            print("⛔ STOP_G envoyé")
            self.sio.emit('stop_general')
        else:
            print("❌ Non connecté, 'stop_general' non envoyé")
