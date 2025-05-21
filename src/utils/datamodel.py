from PyQt5.QtCore import QObject, pyqtSignal

class DataModel(QObject):
    """
    Contient l'état partagé et notifie tout changement via le signal dataChanged.
    """
    dataChanged = pyqtSignal(dict)

    def __init__(self, initial_data=None):
        super().__init__()
        self._data = initial_data or {}

    def get(self):
        return self._data

    def update(self, value):
        """
        Met à jour self.data[key] = value et émet dataChanged.
        """
        self.dataChanged.emit(value)
