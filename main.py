import sys, os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream
from src.login_window import LoginWindow

def setQss(file_path, obj):
    """
    function for reading style file
    """
    with open(file_path, "r") as rf:
        style = rf.read()
        obj.setStyleSheet(style)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    style_file_path = os.path.join(script_dir, "./static/style.qss")

    # Charger le fichier de style
    style_file = QFile(style_file_path)
    if not style_file.open(QFile.ReadOnly | QFile.Text):
        print("Impossible d'ouvrir le fichier style.qss")
    else:
        style_stream = QTextStream(style_file)
        app.setStyleSheet(style_stream.readAll())

    window = LoginWindow()
    window.show()

    sys.exit(app.exec_())