class InsertTovar(QMainWindow):
    def __init__(self):
        super().__init__()
        # Словник з налаштуваннями полів для кожного товару
        self.tovar_fields = {
            "Смартфон": ["Модель", "Пам'ять", "Колір", "Ціна"],
            "Ноутбук": ["Процесор", "RAM", "SSD", "Ціна"],
            "Одяг": ["Розмір", "Матеріал", "Бренд", "Ціна"]
        }
        
        # ... (ваш код ініціалізації комбобоксів)
        self.sub_vupad_spusok.currentIndexChanged.connect(self.show_forma_vvody_danux)

    def show_sub_vupad_spusok(self):
        self.sub_vupad_spusok.blockSignals(True)
        self.sub_vupad_spusok.clear()
        self.sub_vupad_spusok.addItem("Оберіть товар...")
        # Додаємо ключі з нашого словника fields
        self.sub_vupad_spusok.addItems(self.tovar_fields.keys())
        self.sub_vupad_spusok.setCurrentIndex(0)
        self.sub_vupad_spusok.blockSignals(False)
        
        self.forma_vvody.hide()
        self.sub_vupad_spusok.show()

    def show_forma_vvody_danux(self, index):
        # 1. Перевіряємо, чи обрано реальний товар
        tovar_name = self.sub_vupad_spusok.currentText()
        if tovar_name not in self.tovar_fields:
            self.forma_vvody.hide()
            return

        # 2. Очищуємо стару форму
        while self.text_forma_vvody.count() > 0:
            self.text_forma_vvody.removeRow(0)

        # 3. Створюємо поля саме для цього товару
        self.inputs = {} 
        fields_to_create = self.tovar_fields[tovar_name]

        for field_name in fields_to_create:
            line_edit = QLineEdit()
            self.text_forma_vvody.addRow(f"{field_name}:", line_edit)
            # Зберігаємо посилання на поле, щоб потім забрати текст
            self.inputs[field_name] = line_edit
        
        self.forma_vvody.show()
