import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QCompleter, QLabel
from PyQt6.QtCore import Qt

class SearchableComboBoxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пошук у списку")
        self.resize(350, 120)

        # Головний віджет та макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        layout.addWidget(QLabel("Почніть вводити назву для пошуку:"))

        # 1. Створюємо випадаючий список
        self.combo_box = QComboBox()
        self.combo_box.setEditable(True)  # Дозволяє вводити текст користувачу
        self.combo_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert) # Забороняє випадково додавати лівий текст у список

        # 2. Імітація списку даних з вашої БД
        data_from_db = ["ТОВ 'Ромашка'", "ПП 'Патріот'", "ТОВ 'Агро-Трейд'", "ФОП Іванов", "ТОВ 'Мега Плюс'"]
        self.combo_box.addItems(data_from_db)

        completer = QCompleter(data_from_db, self)  # 3. Налаштовуємо автодоповнення та розумний пошук (Completer)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # Пошук буде працювати незалежно від великої/малої літери (Ромашка і ромашка)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)   # Шукає збіг у будь-якій частині назви (наприклад, ввели "Трейд" -> знайшло "ТОВ 'Агро-Трейд'")
        self.combo_box.setCompleter(completer)    # зєднуємо пошуковий рушій completer до нашого списку

        # Додаємо елемент на екран
        layout.addWidget(self.combo_box)
        layout.addStretch()

    # Метод для зчитування того, що вибрав або ввів користувач
    def get_selected_value(self):
        return self.combo_box.currentText()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchableComboBoxWindow()
    window.show()
    sys.exit(app.exec())
