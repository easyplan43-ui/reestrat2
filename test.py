import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetSelectionRange,
                             QPushButton, QLabel, QComboBox)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Структурний шаблон форми (Стиль ERP)")
        self.resize(900, 500)

        # Головний контейнер та його ВЕРТИКАЛЬНИЙ макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10) # зазори між великими блоками
        main_layout.setContentsMargins(10, 10, 10, 10) # відступи від країв вікна

        # =====================================================================
        # 1. ВЕРХНЯ ШАПКА (shapka_layout) — Горизонтальна, вузька
        # =====================================================================
        shapka_layout = QHBoxLayout()
        
        shapka_layout.addWidget(QLabel("Дата:"))
        self.input_date = QLineEdit("11.10.2026")
        self.input_date.setFixedWidth(100)
        shapka_layout.addWidget(self.input_date)
        
        shapka_layout.addSpacing(15) # невеликий жорсткий відступ
        
        shapka_layout.addWidget(QLabel("Документ №:"))
        self.input_doc_num = QLineEdit()
        self.input_doc_num.setPlaceholderText("Авто")
        self.input_doc_num.setFixedWidth(120)
        shapka_layout.addWidget(self.input_doc_num)
        
        shapka_layout.addStretch() # "Пружина" штовхає все вліво, роблячи макет вузьким
        main_layout.addLayout(shapka_layout)


        # =====================================================================
        # 2. СЕРЕДНЯ ЧАСТИНА (Центральний робочий блок)
        # =====================================================================
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)

        #--- Ліва панель введення (left_input) — Вузька ---
        left_input_layout = QVBoxLayout()
        left_input_layout.setSpacing(8)
        
        left_input_layout.addWidget(QLabel("Контрагент:"))
        self.combo_agent = QComboBox()
        self.combo_agent.setFixedWidth(200) # Фіксуємо вузьку ширину лівої панелі
        left_input_layout.addWidget(self.combo_agent)
        
        left_input_layout.addWidget(QLabel("Склад:") )
        self.combo_sklad = QComboBox()
        self.combo_sklad.setFixedWidth(200)
        left_input_layout.addWidget(self.combo_sklad)
        
        left_input_layout.addWidget(QLabel("Артикул:"))
        self.input_artikul = QLineEdit()
        self.input_artikul.setFixedWidth(200)
        left_input_layout.addWidget(self.input_artikul)
        
        # Кнопка додавання позиції в таблицю
        self.btn_add_pos = QPushButton("Додати товар ->")
        self.btn_add_pos.setFixedWidth(200)
        self.btn_add_pos.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        left_input_layout.addWidget(self.btn_add_pos)
        
        left_input_layout.addStretch() # Штовхає всі елементи вводу догори
        middle_layout.addLayout(left_input_layout)
        

        #--- Права панель (table) — Займає весь основний простір ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Артикул", "Назва", "Кількість", "Ціна"])
        # Автоматичне розтягування колонок по ширині вікна
        self.table.horizontalHeader().setStretchLastSection(True) 
        middle_layout.addWidget(self.table)

        # Додаємо всю середню частину в головний макет
        main_layout.addLayout(middle_layout)


        # =====================================================================
        # 3. НИЖНЯ ПАНЕЛЬ КНОПОК (btn_layout) — Горизонтальна, вузька
        # =====================================================================
        btn_layout = QHBoxLayout()
        
        btn_layout.addStretch() # Пружина штовхає кнопки в крайній правий кут
        
        self.btn_cancel = QPushButton("Скасувати")
        self.btn_cancel.setFixedWidth(100)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_save = QPushButton("Провести накладну")
        self.btn_save.setFixedWidth(150)
        self.btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        btn_layout.addWidget(self.btn_save)
        
        main_layout.addLayout(btn_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
