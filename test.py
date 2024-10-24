import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QEvent
import keyboard


PatternRedactor = None
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Нажмите W, A, S, D на любой раскладке")
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Установим обработчики для клавиш только когда окно в фокусе
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.WindowActivate:
            # Когда окно активируется, устанавливаем обработчики клавиш
            keyboard.on_press_key("w", self.on_key_w)
            keyboard.on_press_key("a", self.on_key_a)
            keyboard.on_press_key("s", self.on_key_s)
            keyboard.on_press_key("d", self.on_key_d)

        elif event.type() == QEvent.Type.WindowDeactivate:
            # Когда окно теряет фокус, удаляем обработчики клавиш
            keyboard.unhook_all()

        return super().eventFilter(obj, event)

    def on_key_w(self, e):
        self.label.setText("W Pressed")
        move_pattern("y", -1, PatternRedactor)

    def on_key_a(self, e):
        self.label.setText("A Pressed")
        move_pattern("x", -1, PatternRedactor)

    def on_key_s(self, e):
        self.label.setText("S Pressed")
        move_pattern("y", 1, PatternRedactor)

    def on_key_d(self, e):
        self.label.setText("D Pressed")
        move_pattern("x", 1, PatternRedactor)

def move_pattern(direction, value, PatternRedactor):
    # Ваш код для перемещения объекта
    print(f"Move {direction} by {value}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
