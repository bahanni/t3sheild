from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, 
                           QGridLayout, QDesktopWidget, QMainWindow, QLineEdit)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QFont


class KeyboardWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Touch Keyboard")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet(
            "background-color: rgba(32, 32, 32, 0.95);"
            "border-radius: 10px; border: 1px solid #555;"
        )
        self.setCentralWidget(central_widget)

        # Main layout
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(6)

        # State
        self.target = None
        self.uppercase = False
        self.symbols_mode = False
        self.manual_hide = False
        self._startPos = None
        self._endPos = None
        self._tracking = False

        # Build keyboard
        self.create_keyboard()
        self.setFixedSize(800, 270)
        self.position_at_bottom()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                self.clear_layout(item.layout())
            elif item.widget():
                item.widget().deleteLater()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._tracking:
            self._endPos = event.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._startPos = QPoint(event.x(), event.y())
            self._tracking = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    def position_at_bottom(self):
        if self.parent():
            rect = self.parent().geometry()
            x = rect.x() + (rect.width() - self.width()) // 2
            y = rect.y() + rect.height() - self.height() - 10
        else:
            screen = QDesktopWidget().screenGeometry()
            x = (screen.width() - self.width()) // 2
            y = screen.height() - self.height() - 10
        self.move(x, y)

    def create_keyboard(self):
        # Clear previous keys
        self.clear_layout(self.layout)

        grid = QGridLayout()
        grid.setSpacing(2)

        # Row 0: letters or numbers + backspace
        row0 = ['1','2','3','4','5','6','7','8','9','0'] if self.symbols_mode else ['q','w','e','r','t','y','u','i','o','p']
        for i, key in enumerate(row0):
            btn = self._create_key(key)
            grid.addWidget(btn, 0, i+1)
        back = QPushButton("⌫")
        back.clicked.connect(self.backspace_pressed)
        self.style_button(back, is_special=True)
        grid.addWidget(back, 0, len(row0)+1)

        # Row 1: letters or symbols + enter
        row1 = ['@','#','$','%','&','*','-','+','='] if self.symbols_mode else ['a','s','d','f','g','h','j','k','l']
        for i, key in enumerate(row1):
            btn = self._create_key(key)
            grid.addWidget(btn, 1, i+2)
        ent = QPushButton("⏎")
        ent.clicked.connect(self.enter_pressed)
        self.style_button(ent, is_enter=True)
        grid.addWidget(ent, 1, len(row1)+2)

        # Row 2: shift, letters, shift
        shift_l = QPushButton("⇧")
        shift_l.clicked.connect(self.shift_pressed)
        self.style_button(shift_l, is_special=True)
        grid.addWidget(shift_l, 2, 1)
        row2 = ['!','"',"'",':',';','/','?'] if self.symbols_mode else ['z','x','c','v','b','n','m']
        for i, key in enumerate(row2):
            btn = self._create_key(key)
            grid.addWidget(btn, 2, i+2)
        shift_r = QPushButton("⇧")
        shift_r.clicked.connect(self.shift_pressed)
        self.style_button(shift_r, is_special=True)
        grid.addWidget(shift_r, 2, len(row2)+2)

        # Row 3: toggle, comma, space, period
        toggle = QPushButton("ABC" if self.symbols_mode else "?123")
        toggle.clicked.connect(self.toggle_symbols)
        self.style_button(toggle, is_special=True)
        grid.addWidget(toggle, 3, 1)
        comma = QPushButton(",")
        comma.clicked.connect(lambda: self.key_pressed(","))
        self.style_button(comma)
        grid.addWidget(comma, 3, 2)
        space = QPushButton("Space")
        space.clicked.connect(lambda: self.key_pressed(" "))
        space.setFixedHeight(50)
        space.setStyleSheet(
            "QPushButton { background-color: #202020; color: #d1d1d1;"
            "border-radius: 6px; border: 1px solid #4d4d4d; }"
            "QPushButton:pressed { background-color: #555555; }"
        )
        grid.addWidget(space, 3, 3, 1, 6)
        period = QPushButton(".")
        period.clicked.connect(lambda: self.key_pressed("."))
        self.style_button(period)
        grid.addWidget(period, 3, 9)

        # Stretch columns for centering
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(len(row0)+2, 1)

        self.layout.addLayout(grid)

    def _create_key(self, key):
        # Determine displayed text vs actual input
        display = key.upper() if self.uppercase and not self.symbols_mode else key
        # Qt interprets '&' as shortcut - escape it
        qt_text = '&&' if display == '&' else display
        btn = QPushButton(qt_text)
        btn.clicked.connect(lambda _, t=display: self.key_pressed(t))
        self.style_button(btn)
        return btn

    def style_button(self, button, is_special=False, is_enter=False):
        button.setFixedSize(65, 50)
        button.setFont(QFont('Arial', 12))
        if is_enter:
            button.setStyleSheet(
                "QPushButton { background-color: #28a745; color: white;"
                "border-radius: 6px; border: none; font-weight: bold;}"
                "QPushButton:pressed { background-color: #218838;}"
            )
        elif is_special:
            button.setStyleSheet(
                "QPushButton { background-color: #3a3a3a; color: white;"
                "border-radius: 6px; border: none;}"
                "QPushButton:pressed { background-color: #555555;}"
            )
        else:
            button.setStyleSheet(
                "QPushButton { background-color: #202020; color: #d1d1d1;"
                "border-radius: 6px; border: 1px solid #4d4d4d;}"
                "QPushButton:pressed { background-color: #555555;}"
            )

    def key_pressed(self, text):
        if self.target:
            pos = self.target.cursorPosition()
            cur = self.target.text()
            self.target.setText(cur[:pos] + text + cur[pos:])
            self.target.setCursorPosition(pos + len(text))
            if self.uppercase and not self.symbols_mode:
                self.uppercase = False
                self.create_keyboard()

    def backspace_pressed(self):
        if self.target:
            pos = self.target.cursorPosition()
            if pos > 0:
                cur = self.target.text()
                self.target.setText(cur[:pos-1] + cur[pos:])
                self.target.setCursorPosition(pos-1)

    def enter_pressed(self):
        if self.target:
            parent = self.target
            while parent.parent():
                parent = parent.parent()
            inputs = parent.findChildren(QLineEdit)
            logins = parent.findChildren(QPushButton, "loginBtn")
            idx = inputs.index(self.target) if self.target in inputs else -1
            if idx == len(inputs)-1 and logins:
                self.manual_hide = True
                logins[0].click()
            elif 0 <= idx < len(inputs)-1:
                self.manual_hide = False
                nxt = inputs[idx+1]
                self.target.clearFocus()
                nxt.setFocus()
                self.target = nxt

    def shift_pressed(self):
        self.uppercase = not self.uppercase
        self.create_keyboard()

    def toggle_symbols(self):
        self.symbols_mode = not self.symbols_mode
        self.create_keyboard()

    def showEvent(self, event):
        super().showEvent(event)
        self.position_at_bottom()

    def hide(self):
        self.manual_hide = True
        super().hide()