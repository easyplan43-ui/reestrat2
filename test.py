import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
def say_hello():
    send_btn = app.focusWidget()
    print(f"nazata knopka with text:{send_btn.text()}")

app = QApplication(sys.argv)

# 3. Создаем главное окно (простой виджет)
window = QWidget()
window.setWindowTitle("Пример без ООП")
layout = QVBoxLayout()

btn = QPushButton("Нажми меня!")

btn.clicked.connect(say_hello)


# 6. Добавляем кнопку в макет и отображаем окно
layout.addWidget(btn)
window.setLayout(layout)
window.show()

# Запуск цикла обработки событий
sys.exit(app.exec())