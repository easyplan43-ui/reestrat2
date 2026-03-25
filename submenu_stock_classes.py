import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout,
                             QPushButton, QHeaderView, QFrame, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from constants import *
from conn_to_db import DBConnector, SelectCategory # клас для підключення до бд
from check_functions import InputValidator  #  для перевірки введених даних від користувача 

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

class InsertTovar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow { background-color: #f4f4f9; }
            QLabel { font-size: 14px; color: #333; font-weight: bold; }
            QLineEdit, QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; background: white; }
            QPushButton { background-color: #2c3e50; color: white; padding: 10px; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #34495e; }
            QTableWidget { background-color: white; border: 1px solid #ddd; }
        """)
        self.cat_tag = None   #  Це тег взятий з табл: Categories, щоби знати яку вибирати табл: Memory_det, Processor_det, ....
        central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget) # Горизонтальний розподіл: Форма | Таблиця

        left_panel_ins_data = QVBoxLayout()       # ---------------- ЛІВА ПАНЕЛЬ (Введення даних + випадаючий список) -----------------
        left_panel_ins_data.addWidget(QLabel("📦 КАТЕГОРІЯ"))  # Створює віджет (елемент інтерфейсу), який відображає текст або зображення. 
        
        self.vupad_spusok = QComboBox()   # Создает новый экземпляр  ---------- «Головн випадаючий список»  ------------------------
        self.ekzemp_category = SelectCategory(Table_category)  # Створюємо екземпляр класу, передаючи назву таблиці
        category = self.ekzemp_category.get_category_and_id()   # отримуєм назви категорій і її id з таблиці типу: [(3, 'Процесори'), (7, 'Накопичувачі'), (12, 'Оперативна память'), (15, 'Материнська плата')]
        self.vupad_spusok.clear()    #  Очищуємо віджет перед оновленням (щоб категорії не дублювалися)
        self.vupad_spusok.addItem("Виберіть категорію товара", (0, None))   # Додаємо дефолтний елемент першим до випадаючого списку
        for cat_id, cat_name, self.cat_tag in category: # category = [(3, 'Процесори', 'cpu'), (7, 'Накопичувачі', 'storage'), (12, 'Оперативна память', 'ram'), (15, 'Материнська плата', 'mainboard')]
            self.vupad_spusok.addItem(cat_name, (cat_id, self.cat_tag))   #  addItem(видимий_текст, (приховані_дані, приховані_дані))
        self.vupad_spusok.currentIndexChanged.connect(self.show_sub_vupad_spusok)  # Коли корист вибирає якийсь елем у випадаючому списку, показуємо sub список під головн випад списком
        left_panel_ins_data.addWidget(self.vupad_spusok)  # Випадаюч список додаємо до лівої панелі
       
        self.sub_vupad_spusok = QComboBox()   # -------  Створюємо sub випадаючий список відразу, але ховаємо його --------
        self.sub_vupad_spusok.hide()
        self.sub_vupad_spusok.currentIndexChanged.connect(self.show_forma_vvody_danux)  # Коли корист вибирає якийсь елем у sub списку - показуємо форму вводу даних
        left_panel_ins_data.addWidget(self.sub_vupad_spusok)   #  Випадаюч sub список додаємо до лівої панелі

        # ---------------------  Контейнер форми для введення даних в бд ----------------------------------------------
        self.forma_vvody = QWidget()   # Батьківський віджет для форми вводу інфи в бд
        self.forma_vvody.hide()
        self.text_forma_vvody = QFormLayout(self.forma_vvody)  # QFormLayout - клас який вирівн віджети у 2 стовпці: зліва - надпис, справа - поле вводу
        left_panel_ins_data.addWidget(self.forma_vvody)  # Форму вводу додаємо до лівої панелі
        
        self.btn_addto_sklad = QPushButton("ДОДАТИ НА СКЛАД")    # ------------------ Кнопка під формою ---------------------------
        self.btn_addto_sklad.hide()
        self.btn_addto_sklad.clicked.connect(self.receive_users_data)  # При нажаті на кнопку вставляєм дані які ввів користув в полях вводу в бд і робимо попередній перегляд в таблиці справа
        left_panel_ins_data.addWidget(self.btn_addto_sklad)   # Кнопку додаемо до лівої панелі
        left_panel_ins_data.addStretch() # Притиснути все вгору
        # -----------------------------------------  ПРАВА ПАНЕЛЬ (Попередній перегляд залишків в таблиці) -----------------------------------------------
        right_panel_table = QVBoxLayout()
        right_panel_table.addWidget(QLabel("📋 ОСТАННІ ВВЕДЕННЯ"))  # Створює віджет (елемент інтерфейсу), який відображає текст або зображення.     
        self.table = QTableWidget(0, 4)  # Создает виджет с 0 начальными строками и 4 столбцами
        self.table.setHorizontalHeaderLabels(["Товар", "Категорія", "К-сть", "Ціна"]) # зверт до обєкту таблиці і встановл назви стовпців
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # режим розтягування шапки таблиці
        right_panel_table.addWidget(self.table)
        
        # Додаємо панелі в головний лейаут
        layout.addLayout(left_panel_ins_data, 2)  # 1 частина ширини
        layout.addLayout(right_panel_table, 4) # 2 частини ширини
    
    def show_sub_vupad_spusok(self):  # Показує sub випадаючий список, після того як корист вибере щось з основного випад. списку
        self.sub_vupad_spusok.blockSignals(True)  # Тимчасово вимикаємо сигнали, щоб форма вводу не вискакувала завчасно при додавані елементів до sub випад списку
        select_id, self.cat_tag = self.vupad_spusok.currentData()  # currentData(): Метод, который вертає прихов дані, а саме cat_id з vupad_spusok.addItem(cat_name, cat_id)
        sub_category = self.ekzemp_category.get_subcategory_by_id(select_id) # за вказаним id виводимо підкатегоріїї, які є дітьми від категорії з цим id
        if sub_category:   #  Якщо користувач вибрав любу з категорій окрім категорії по замовчуванню 
            self.sub_vupad_spusok.clear()    #  Очищуємо віджет перед оновленням 
            self.sub_vupad_spusok.addItem("Виберіть підкатегорію товара", 0)   # Додаємо дефолтний елемент першим до випадаючого списку
            for cat_name in sub_category: # іsubcategory = [('SSD SATA',), ('SSD M2 Nvme',), ('SSD SAS',), ('HDD',)]
                self.sub_vupad_spusok.addItem(cat_name[0])  # Додаємо до sub випадаючого списку елементи
            self.sub_vupad_spusok.setCurrentIndex(0)   # Форма вводу з'явиться лише тоді, коли ви перемкнетеся з "Виберіть підкатегорію товара" на реальний товар
            self.sub_vupad_spusok.blockSignals(False) # Вмикаємо сигнали назад
            self.forma_vvody.hide()     # Ховаємо форму, якщо вона була відкрита раніше для іншого товару
            self.sub_vupad_spusok.show()
        else:       #  Якщо користувач вибрав категорії по замовчуванню 
            self.sub_vupad_spusok.hide()       #    Ховаємо випадаючий список, якщо підкатегорій немає
            self.forma_vvody.hide()            #    Ховаємо форму вводу, якщо підкатегорій немає
            self.btn_addto_sklad.hide()        #    Ховаємо кнопку під формою, якщо підкатегорій немає
       
    def show_forma_vvody_danux(self, index):
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            self.forma_vvody.hide()
            self.btn_addto_sklad.hide()
            return
        while self.text_forma_vvody.count():  # Доки кількість елементів у макеті більша за нуль
            item = self.text_forma_vvody.takeAt(0)  # Видаляє посилання на перший елемент (з індексом 0) з вашого макета (layout)
            if item.widget():
                item.widget().deleteLater()    #   Чи є цей елемент віджетом, якщо так то Видали цей об'єкт
            
        list_stovp_datatype = self.formyem_slovnuk(Table_main_product) # [('Artukyl', 'nvarchar', 30), ('Nazva_tov', 'nvarchar', 100), ('Description', 'nvarchar', -1), ('Kilkist', 'int', None), ('Price', 'decimal', None)]
        korteg_table_name = self.ekzemp_category.get_name_table_by_tag(Table_tag, self.cat_tag) # по cat_tag шукаємо назву відпов таблиці, вертає кортеж типу: [('hardware.Storage_detail',)]
        table_name =  korteg_table_name[0][0]  # беремо 1-ий елемент кортежу -  hardware.Storage_det
        list_stovp_datatype2 = self.formyem_slovnuk(table_name)   # [('socket', 'nvarchar', 30), ('cores', 'int', None), ('threads', 'int', None), ('frequency', 'decimal', None), ('watt', 'int', None)]
        self.dict_stovp_type_size = {}   # Створюємо словник типу: назва_стовпця : об'єкт QLineEdit, тип_даних, розмір_або_точність    
        list_stovpciv_full = list_stovp_datatype + list_stovp_datatype2  # Обєднуємо списки отримані з таблиці Products і з таблиці залежної, напр, Memory, Storage,....
        
        for stovpec, datatype, size in list_stovpciv_full: # Формується словник dict_stovp_type_size[stovpec] + наповнюєт. текст укр момою при формі вводу
            widget =  QLineEdit()   #  создаем однорядкове поле вводу даних
            korteg_ukr_namestovp = self.ekzemp_category.get_display_ukrtext(Table_translate, stovpec) # за вказан імям stovpec на анг отримуєм укр читабел текст при полі вводу даних
            ukr_namestovp = korteg_ukr_namestovp[0][0]    # беремо 1-ий елемент кортежу 
            InputValidator.apply(widget, datatype, size)  # Викликаємо клас для накладання обмежень при вводі даних користув в форму вводу
            self.dict_stovp_type_size[stovpec] = (widget, datatype, size)  #    Формується словник dict_stovp_type_size[stovpec] типу:  <PyQt6.QtWidgets.QLineEdit object at 0x00000162CB4898B0>, 'nvarchar', 30)      
            self.text_forma_vvody.addRow(f"{ukr_namestovp}:", widget)  # Створ новий рядок у формі: назва - поле вводу
        self.forma_vvody.show()
        self.btn_addto_sklad.show()

    def formyem_slovnuk(self, table_name):    #  За вказан імям таблиці видає список Не всіх [(стовпців, тип_даних, відвед_кілкість_символ)]
        list_stovpciv_type = self.ekzemp_category.get_neccess_stovpci_and_type(table_name)
        return  list_stovpciv_type
    
    def receive_users_data(self):   # Вставляє дані в дві таблиці Products і іншу табл залежно від tag
        dict_dani_z_formu = {}
        for stovpec, (widget, datatype, size) in self.dict_stovp_type_size.items():
            users_data = widget.text().strip()   # Отримуємо дані які ввів користувач із кожного поля вводу
            print(f"Стовпець: {stovpec}")
            print(f"Введено: {users_data}")
            print(f"Тип: {datatype}")
            print(f"Розмір: {size}")
            print("-" * 30)



        #self.table.setItem(row, 0, QTableWidgetItem(name))
        #self.table.setItem(row, 1, QTableWidgetItem(cat))
        #self.table.setItem(row, 2, QTableWidgetItem(qty))
        #self.table.setItem(row, 3, QTableWidgetItem(f"{price} грн"))
        
        # Очищення полів
        #for inp in self.dict.values(): inp.clear()

