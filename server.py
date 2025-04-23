from flask import Flask
from flask_socketio import SocketIO, emit
import threading
import time
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

stop_message_m = False
stop_message_g = False

def start_mobility_analyze():
    global stop_message_m
    stop_message_m = False
    i = 0
    while not stop_message_m:
        message_to_send = {
                            "timestamp": "2025-04-23 15:13:45",
                            "operator": "Inwi",
                            "frequency_mhz": 882.7396745932416,
                            "power_dbm": i,
                            "risk_level": "Risque Minime",
                            "color": "#FFD700",
                            "risque": True
                            }
                        

        json_data = json.dumps(message_to_send)
        socketio.emit('mobility_data', json_data)
        time.sleep(0.1)
        i += 1

def start_general_analyze():
    global stop_message_g
    time.sleep(2)
    message_to_send = {'data': [{'Date': '2025-04-09 17:21:31', 'Orange': 2, 'type_communication': 'gsm'}, {'Date': '2025-04-09 17:21:31', 'Inwi': 2, 'type_communication': 'gsm'}, {'Date': '2025-04-09 17:21:31', 'IAM': 1, 'type_communication': 'gsm'}]}
 
    json_data = json.dumps(message_to_send)
    socketio.emit('general_data', json_data)

@socketio.on('start_general')
def handle_start_general():
    print("++ START_G reçu")
    start_general_analyze()

@socketio.on('start_mobility')
def handle_start_mobility():
    print("++ START_M reçu")
    start_mobility_analyze()

@socketio.on('stop_mobility')
def handle_stop_mobility():
    global stop_message_m
    stop_message_m = True
    print("🛑 STOP_M reçu")

@socketio.on('stop_general')
def handle_stop_general():
    global stop_message_g
    stop_message_g = True
    print("🛑 STOP_G reçu")

if __name__ == '__main__':
    print("✅ Serveur Flask-SocketIO démarré...")
    socketio.run(app, host='0.0.0.0', port=5000)