import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QSpacerItem, QSizePolicy, QPushButton, QMessageBox
)

class MyLineEdit(QLineEdit):
    def __init__(self, row, col, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row = row
        self.col = col
        # Style par défaut
        self.setStyleSheet("background-color: red;")

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # Appliquer style vert à la sélection
        self.setStyleSheet("background-color: lightgreen;")
        print(f"Vous avez sélectionné le champ ({self.row}, {self.col})")

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # Appliquer style rouge à la désélection
        self.setStyleSheet("background-color: red;")
        print(f"Vous avez désélectionné le champ ({self.row}, {self.col})")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrice de QLineEdit avec validation")
        self.resize(400, 350)

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Boutons pour créer la matrice et valider
        controls_layout = QVBoxLayout()
        btn_create = QPushButton("Créer matrice")
        btn_create.clicked.connect(lambda: self.create_matrix(4, 5))
        btn_validate = QPushButton("Valider champ actif")
        btn_validate.clicked.connect(self.validate_current)
        controls_layout.addWidget(btn_create)
        controls_layout.addWidget(btn_validate)
        main_layout.addLayout(controls_layout)

        # Layout de la matrice
        self.matrix_layout = QGridLayout()
        main_layout.addLayout(self.matrix_layout)

    def clear_matrix_layout(self):
        # Supprime tous les widgets du layout
        while self.matrix_layout.count():
            item = self.matrix_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def create_matrix(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.clear_matrix_layout()
        self.matrix_inputs = []

        # En-têtes de colonnes
        for c in range(cols):
            col_header = QLabel(f"Col {c+1}")
            self.matrix_layout.addWidget(col_header, 0, c+1, Qt.AlignCenter)

        for r in range(rows):
            row_inputs = []
            # En-tête de ligne
            row_header = QLabel(f"Ligne {r+1}")
            self.matrix_layout.addWidget(row_header, r+1, 0, Qt.AlignRight | Qt.AlignVCenter)

            for c in range(cols):
                # Utilise MyLineEdit pour chaque cellule
                input_field = MyLineEdit(r, c)
                input_field.setAlignment(Qt.AlignCenter)
                input_field.setMinimumSize(40, 25)
                self.matrix_layout.addWidget(input_field, r+1, c+1)
                row_inputs.append(input_field)

            self.matrix_inputs.append(row_inputs)

        # Espaceur vertical
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.matrix_layout.addItem(vertical_spacer, rows+1, 0, 1, cols+1)

    def validate_current(self):
        current = QApplication.focusWidget()
        if isinstance(current, MyLineEdit):
            # Appliquer un bord vert sur le champ actif
            current.setStyleSheet("border: 2px solid lightgreen;")
            print(f"Champ ({current.row}, {current.col}) validé.")
        else:
            QMessageBox.warning(self, "Validation", "Le focus n'est pas sur un champ MyLineEdit.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
