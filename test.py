import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

class MyForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Валідація форми")
        self.layout = QVBoxLayout()

        # Створюємо список полів для зручної перевірки циклом
        self.fields = []
        for i in range(3):
            line_edit = QLineEdit()
            self.layout.addWidget(line_edit)
            self.fields.append(line_edit)

        # Кнопка для перевірки
        self.btn = QPushButton("Перевірити")
        self.btn.clicked.connect(self.validate_form)
        self.layout.addWidget(self.btn)

        self.setLayout(self.layout)

    def validate_form(self):
        # Перевіряємо кожне поле: .text() отримує текст, .strip() прибирає пробіли
        is_valid = True
        for field in self.fields:
            if not field.text().strip():
                is_valid = False
                break

        if not is_valid:
            # Вивід вікна попередження
            QMessageBox.warning(self, "Попередження", "Всі поля мають бути заповнені!")
        else:
            # Повідомлення про успіх
            QMessageBox.information(self, "Успіх", "Форму успішно заповнено.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyForm()
    window.show()
    sys.exit(app.exec())
