import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QFrame, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from conn_to_db import DBConnector # клас для підключення до бд
#import pyodbc
# Тільки класи для реалізації підменю "Склад". Незабудь новий створюваний клас відмітити в файлі: string_to_class
class ZalushTovary(QMainWindow):       #   Реалізує вкладку  - "Склад" - "Залишки товарів"
    def __init__(self):
        super().__init__()
        central_widget = QWidget()    # Головний віджет
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.init_ui()
        self.load_data_from_db()

    def init_ui(self):
        # --- 1. ШАПКА ЗВІТУ (Метадані) ---
        header_layout = QHBoxLayout()    #  Секція header_layout з назвою звіту, динамічною датою (можна додати QDate.currentDate()) та інфо про склад.
        meta_info = QVBoxLayout()
        
        title = QLabel("Залишки товарів")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        self.lbl_warehouse = QLabel("Склад: Основний склад (Склад №1)")
        self.lbl_date = QLabel("Дата звіту: 09.03.2025")
        self.lbl_manager = QLabel("Відповідальна особа: Іванов І.І.")
        
        meta_info.addWidget(title)
        meta_info.addWidget(self.lbl_warehouse)
        meta_info.addWidget(self.lbl_date)
        meta_info.addWidget(self.lbl_manager)
        
        header_layout.addLayout(meta_info)
        header_layout.addStretch()
        
        btn_refresh = QPushButton("Оновити дані")
        btn_refresh.setFixedSize(120, 40)
        btn_refresh.clicked.connect(self.load_data_from_db)
        header_layout.addWidget(btn_refresh)
        
        self.layout.addLayout(header_layout)

        # --- 2 & 3. ТАБЛИЧНА ЧАСТИНА ТА ПРОСУНУТІ ПОЛЯ ---
        self.table = QTableWidget()
        headers = ["id", "Manuf", "DDR", "Volume", "Partnumb", "Price"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        
        self.layout.addWidget(self.table)

        # --- 4. ПІДСУМОК (Футер) ---
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        footer_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        footer_layout = QHBoxLayout(footer_frame)
        
        self.lbl_total_qty = QLabel("Загальна кількість: 0")
        self.lbl_total_sum = QLabel("Загальна вартість: 0.00 ₴")
        self.lbl_total_qty.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_total_sum.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        footer_layout.addWidget(self.lbl_total_qty)   # Окрема панель знизу, яка автоматично підсумовує кількість та загальну вартість усіх товарів у таблиці.
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total_sum)
        
        self.layout.addWidget(footer_frame)

    def load_data_from_db(self):
        """Метод для підключення до MS SQL та завантаження даних"""
        with DBConnector() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM hardware.memory")
            rows = cursor.fetchall()
              
        
        
            #self.table.setRowCount(0)
            #total_sum = 0
            #total_items = 0

            #for row_idx, row_data in enumerate(rows):
                #self.table.insertRow(row_idx)
                #for col_idx, value in enumerate(row_data):
                   # item = QTableWidgetItem(str(value))
                    
                    # Логіка підсвічування критичного залишку (Мін. поріг)
                    # У коді реалізована перевірка: якщо залишок <= мін. поріг, рядок підсвічується червоним.
                    #qty = row_data[4]
                    #min_threshold = row_data[7]
                    #if qty <= min_threshold:
                    #    item.setBackground(QColor("#ffcccc")) # Світло-червоний
                    
                    #self.table.setItem(row_idx, col_idx, item)
                
                #total_items += row_data[4]
                #total_sum += row_data[9]

            # Оновлення футера
            #self.lbl_total_qty.setText(f"Загальна кількість: {total_items}")
            #self.lbl_total_sum.setText(f"Загальна вартість: {total_sum:,.2f} ₴")

class Peremichena(QMainWindow):    #   Реалізує вкладку  - "Склад" -  "Переміщення" 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Облік переміщень товарів")
        self.resize(1200, 750)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.init_ui()
        self.load_data_from_db()

    def init_ui(self):
        # --- 1. ШАПКА ЗВІТУ (Метадані) ---
        header_layout = QHBoxLayout()
        meta_info = QVBoxLayout()
        
        title = QLabel("Журнал переміщення товарів")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        self.lbl_period = QLabel("Період: Поточний місяць (Березень 2025)")
        self.lbl_filter = QLabel("Фільтр: Всі склади")
        self.lbl_count = QLabel("Кількість операцій: 0")
        
        meta_info.addWidget(title)
        meta_info.addWidget(self.lbl_period)
        meta_info.addWidget(self.lbl_filter)
        meta_info.addWidget(self.lbl_count)
        
        header_layout.addLayout(meta_info)
        header_layout.addStretch()
        
        # Кнопки керування
        btn_add = QPushButton("+ Нове переміщення")
        btn_add.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        btn_add.setFixedSize(160, 40)
        
        btn_refresh = QPushButton("Оновити дані")
        btn_refresh.setFixedSize(120, 40)
        btn_refresh.clicked.connect(self.load_data_from_db)
        
        header_layout.addWidget(btn_add)
        header_layout.addWidget(btn_refresh)
        
        self.layout.addLayout(header_layout)

        # --- 2 & 3. ТАБЛИЧНА ЧАСТИНА + ПРОСУНУТІ ПОЛЯ ---
        # Просунуті поля тут: Склад-відправник, Склад-отримувач, Статус (Проведено/Чернетка), Тип переміщення
        self.table = QTableWidget()
        headers = [
            "Дата/Час", "№ Документа", "Товар (Артикул)", "Звідки (Склад)", 
            "Куди (Склад)", "К-сть", "Од. вим.", "Відповідальний", "Статус", "Коментар"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Товар ширший
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.layout.addWidget(self.table)

        # --- 4. ПІДСУМОК (Футер) ---
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        footer_frame.setStyleSheet("background-color: #e9ecef; border-top: 2px solid #dee2e6;")
        footer_layout = QHBoxLayout(footer_frame)
        
        self.lbl_total_qty = QLabel("Всього переміщено одиниць: 0")
        self.lbl_total_docs = QLabel("Всього документів: 0")
        
        bold_font = QFont("Arial", 10, QFont.Weight.Bold)
        self.lbl_total_qty.setFont(bold_font)
        self.lbl_total_docs.setFont(bold_font)
        
        footer_layout.addWidget(self.lbl_total_docs)
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total_qty)
        
        self.layout.addWidget(footer_frame)

    def load_data_from_db(self):
        """Підключення до MS SQL Server"""
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=YOUR_SERVER_NAME;"
            "DATABASE=YOUR_DB_NAME;"
            "Trusted_Connection=yes;"
        )
        
        try:
            # Демо-дані (структура під MS SQL)
            rows = [
                ("2025-03-09 10:15", "TR-00124", "Лампа Baseus (4021-А)", "Основний", "Магазин №2", 10, "шт.", "Адмін", "Проведено", "Поповнення вітрини"),
                ("2025-03-09 12:30", "TR-00125", "Кабель Type-C (1005-B)", "Магазин №2", "Сервіс", 5, "шт.", "Іванов", "Чернетка", "На ремонт"),
            ]
            
            # Реальний виклик:
            # conn = pyodbc.connect(conn_str)
            # cursor = conn.cursor()
            # cursor.execute("SELECT Date, DocNum, ProductName, FromStock, ToStock, Qty, Unit, User, Status, Note FROM ProductTransfers")
            # rows = cursor.fetchall()
            
            self.table.setRowCount(0)
            total_qty = 0

            for row_idx, row_data in enumerate(rows):
                self.table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    
                    # Логіка для "Просунутих полів" (Статус)
                    if col_idx == 8: # Колонка "Статус"
                        if value == "Чернетка":
                            item.setForeground(QColor("#6c757d")) # Сірий
                            item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
                        elif value == "Проведено":
                            item.setForeground(QColor("#28a745")) # Зелений
                    
                    self.table.setItem(row_idx, col_idx, item)
                
                total_qty += row_data[5] # Додаємо кількість

            # Оновлення метаданих та футера
            self.lbl_count.setText(f"Кількість операцій: {len(rows)}")
            self.lbl_total_docs.setText(f"Всього документів: {len(rows)}")
            self.lbl_total_qty.setText(f"Всього переміщено одиниць: {total_qty}")

        except Exception as e:
            print(f"Помилка БД: {e}")

class InsertTovar(QMainWindow):     #   Реалізує вкладку  - "Склад" -  "Внесення товару"
     def __init__(self):
        super().__init__()
        central_widget =QWidget()  # Головний віджет
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.init_ui()       # зовнішній вигляд інтерфейсу, каркас з кнопками, таблицями, вікнами
        self.insert_data_to_db() #  щоб заповнити каркас з init_ui реальними даними з таблиці відразу після запуску програми

     def init_ui(self):
        # --- 1. ШАПКА ЗВІТУ (Метадані) ---
        header_layout = QHBoxLayout()    #  Секція header_layout з назвою звіту, динамічною датою (можна додати QDate.currentDate()) та інфо про склад.
        meta_info = QVBoxLayout()
        
        title = QLabel("Залишки товарів")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        self.lbl_warehouse = QLabel("Склад: Основний склад (Склад №1)")
        self.lbl_date = QLabel("Дата звіту: 09.03.2025")
        self.lbl_manager = QLabel("Відповідальна особа: Іванов І.І.")
        
        meta_info.addWidget(title)
        meta_info.addWidget(self.lbl_warehouse)
        meta_info.addWidget(self.lbl_date)
        meta_info.addWidget(self.lbl_manager)
        
        header_layout.addLayout(meta_info)
        header_layout.addStretch()
        
        btn_refresh = QPushButton("Оновити дані")
        btn_refresh.setFixedSize(120, 40)
        #btn_refresh.clicked.connect(self.load_data_from_db)
        header_layout.addWidget(btn_refresh)
        
        self.layout.addLayout(header_layout)

        # --- 2 & 3. ТАБЛИЧНА ЧАСТИНА ТА ПРОСУНУТІ ПОЛЯ ---
        self.table = QTableWidget()
        headers = ["id", "Manuf", "DDR", "Volume", "Partnumb", "Price"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        
        self.layout.addWidget(self.table)

        # --- 4. ПІДСУМОК (Футер) ---
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        footer_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        footer_layout = QHBoxLayout(footer_frame)
        
        self.lbl_total_qty = QLabel("Загальна кількість: 0")
        self.lbl_total_sum = QLabel("Загальна вартість: 0.00 ₴")
        self.lbl_total_qty.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_total_sum.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        footer_layout.addWidget(self.lbl_total_qty)   # Окрема панель знизу, яка автоматично підсумовує кількість та загальну вартість усіх товарів у таблиці.
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total_sum)
        
        self.layout.addWidget(footer_frame)    

     def insert_data_to_db(self):
         print('hello') 


