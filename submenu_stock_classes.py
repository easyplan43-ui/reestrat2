import sys
import pyodbc
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout,
                             QPushButton, QHeaderView, QFrame, QAbstractItemView, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from constants import *
from conn_to_db import DBConnector, SelectCategory # клас для підключення до бд
from check_functions import InputValidator  #  для перевірки введених даних від користувача 

# Тільки класи для реалізації підменю "Склад". Незабудь новий створюваний клас відмітити в файлі: string_to_class
class ZalushTovary(QMainWindow):    #   Реалізує вкладку  - "Склад" -  "Залишок товару" 
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
        self.table_name_depend = None # Це імя залежної таблиці від табл Products, наприклад це може бути табл: Memory, Storage, Proccessor,..
        self.cat_tag = None   #  Це тег взятий з табл: Categories, щоби знати яку вибирати табл: Memory_det, Processor_det, ....
        self.cat_id = None      # id вибраної КАТЕГОРІЇ    з табл Categories, яке користув вибрав в main випадаючому списку, наприклад: Процесори, Диски,....
        self.subcat_id = None   # id вибраної ПІДкатегорії з табл Categories, яке користув вибрав в sub випадаючому списку, наприклад: Intel Core, AMD Ryzen
         
        central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget) # Вертикальний розподіл: вгорі категорії, підкатегорії пошук, внизу - таблиця
        self.search_layout = QHBoxLayout()       # -------------- Горизонт панель де розміщено категорія і пошук -------------

        self.vupad_spusok = QComboBox()   # Создает новый экземпляр  ---------- «Головн випадаючий список»  ------------------------
        self.vupad_spusok.setMaximumWidth(260) 
        self.ekzemp_category = SelectCategory(Table_category)  # Створюємо екземпляр класу, передаючи назву таблиці
        category = self.ekzemp_category.get_category_and_id()   # отримуєм назви категорій і її id з таблиці типу: [(3, 'Процесори'), (7, 'Накопичувачі'), (12, 'Оперативна память'), (15, 'Материнська плата')]
        self.vupad_spusok.clear()    #  Очищуємо віджет перед оновленням (щоб категорії не дублювалися)
        self.vupad_spusok.addItem("Виберіть категорію товара", (0, None))   # Додаємо дефолтний елемент першим до випадаючого списку
        for cat_id, cat_name, cat_tag in category: # category = [(3, 'Процесори', 'cpu'), (7, 'Накопичувачі', 'storage'), (12, 'Оперативна память', 'ram'), (15, 'Материнська плата', 'mainboard')]
            self.vupad_spusok.addItem(cat_name, (cat_id, cat_tag))   #  addItem(видимий_текст, (приховані_дані, приховані_дані))
        self.vupad_spusok.currentIndexChanged.connect(self.show_sub_vupad_spusok)  # Коли корист вибирає якийсь елем у випадаючому списку, показуємо sub список під головн випад списком
        self.search_layout.addWidget(self.vupad_spusok)  # Випадаюч список додаємо до панелі пошуку інформації
        self.search_layout.addSpacing(25)  # Відступ між випад списком  і sub випадаючим списком

        self.sub_vupad_spusok = QComboBox()   # -----------  Створюємо sub випадаючий список відразу, але ховаємо його --------
        self.sub_vupad_spusok.hide()
        self.sub_vupad_spusok.currentIndexChanged.connect(self.show_table)  # Коли корист вибирає якийсь елем у sub списку - виводимо таблицю 
        self.search_layout.addWidget(self.sub_vupad_spusok)   #  Sub Випадаюч список додаємо до панелі пошуку інформації
        self.search_layout.addStretch()  # Ця "пружина" штовхає випадаючі списки вліво
        self.search_layout.addSpacing(25)  # Відступ між sub випад списком  і полем пошуку

        #  ------------------- Поле Пошуку по назві (динамічний) ------------------------
        self.search_text = QLabel()   # Це просто текст "Пошук" при строці пошуку
        self.search_text.hide()
        self.search_layout.addWidget(self.search_text)

        self.search_input = QLineEdit()   # Це поле пошуку чогось / поле вводу 
        self.search_input.hide()
        self.search_input.setPlaceholderText("Введіть назву товару...") 
        #self.search_input.textChanged.connect(self.apply_filters) # Оновлення при кожній букві
        self.search_layout.addWidget(self.search_input)
        self.main_layout.addLayout(self.search_layout)  # макет пошуку (горизонтальний) стає частиною основного вертикального макета
              
        # -------------------------------Таблиця виводу інфи з бд -------------------------------
        self.table = QTableWidget()
        self.table.hide()
        self.main_layout.addWidget(self.table)
        self.main_layout.addStretch()   # Випадаючі списки і таблицю даємо на саму гору

    def show_sub_vupad_spusok(self):  # Показує sub випадаючий список, після того як корист вибере щось з основного випад. списку
        self.sub_vupad_spusok.blockSignals(True)  # Тимчасово вимикаємо сигнали, щоб форма вводу не вискакувала завчасно при додавані елементів до sub випад списку
        self.cat_id, self.cat_tag = self.vupad_spusok.currentData()  # currentData(): Метод, который вертає прихов дані, а саме cat_id з vupad_spusok.addItem(cat_name, cat_id)
        sub_category = self.ekzemp_category.get_subcategory_by_id(self.cat_id) # за вказаним id виводимо id і підкатегоріїї, які є дітьми від категорії з цим id
        if sub_category:   #  Якщо користувач вибрав любу з підкатегорій окрім категорії по замовчуванню 
            self.sub_vupad_spusok.clear()    #  Очищуємо віджет перед оновленням 
            self.sub_vupad_spusok.addItem("Виберіть підкатегорію товара", 0)   # Додаємо дефолтний елемент першим до випадаючого списку
            for cat_id, cat_name in sub_category: # sub_category = [('SSD SATA',), ('SSD M2 Nvme',), ('SSD SAS',), ('HDD',)]
                self.sub_vupad_spusok.addItem(cat_name, cat_id)  # Додаємо до sub випадаючого списку елементи
            self.sub_vupad_spusok.setCurrentIndex(0)   # Форма вводу з'явиться лише тоді, коли ви перемкнетеся з "Виберіть підкатегорію товара" на реальний товар
            self.sub_vupad_spusok.blockSignals(False) # Вмикаємо сигнали назад
            self.table.hide()                  # Очищаємо таблицю показу щойно введених даних
            self.sub_vupad_spusok.show()
        else:       #  Якщо користувач вибрав категорії по замовчуванню 
            self.sub_vupad_spusok.hide()       #    Ховаємо випадаючий список, якщо підкатегорій немає
                       
            self.table.hide()                  #    Ховаємо таблицю показу щойно введених даних
        
    def show_table(self, index):   #  Виводить на екран поле таблицю з результатами пошуку
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            self.table.hide()                  #    Ховаємо таблицю показу щойно введених даних
            return
        list_stovp_datatype = self.formyem_slovnuk(Table_main_product) # [('Artukyl', 'nvarchar', 30), ('Nazva_tov', 'nvarchar', 100), ('Description', 'nvarchar', -1), ('Kilkist', 'int', None), ('Price', 'decimal', None)]
        korteg_table_name = self.ekzemp_category.get_name_table_by_tag(Table_tag, self.cat_tag) # по cat_tag шукаємо назву відпов таблиці, вертає кортеж типу: [('hardware.Storage_detail',)]
        self.table_name_depend =  korteg_table_name[0][0]  # беремо 1-ий елемент кортежу -  hardware.Storage_det
        list_stovp_datatype2 = self.formyem_slovnuk(self.table_name_depend)   # [('socket', 'nvarchar', 30), ('cores', 'int', None), ('threads', 'int', None), ('frequency', 'decimal', None), ('watt', 'int', None)]
        list_stovpciv_full = list_stovp_datatype + list_stovp_datatype2  # Обєднуємо списки отримані з таблиці Products і з таблиці залежної, напр, Memory, Storage,....
        
        list_ukr_namestovp = []            # цей список передав в шабку-заголовок таблиці
        for stovpec, datatype, size in list_stovpciv_full: # Формується словник dict_stovp_type_size[stovpec] + наповнюєт. текст укр момою при формі вводу
            korteg_ukr_namestovp = self.ekzemp_category.get_display_ukrtext(Table_translate, stovpec) # за вказан імям stovpec на анг отримуєм укр читабел текст при полі вводу даних звертаючись до таблиці бд
            ukr_namestovp = korteg_ukr_namestovp[0][0]    # беремо 1-ий елемент кортежу 
            list_ukr_namestovp.append(ukr_namestovp)  # формую список з україн назв 
                   
        self.table.setColumnCount(len(list_ukr_namestovp))   # Встановлюємо кількість колонок
        self.table.setHorizontalHeaderLabels(list_ukr_namestovp) # зверт до обєкту таблиці і встановл назви стовпців
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setMinimumSectionSize(100) # наприклад, 100 пікселів
        self.table.show()
        
    def formyem_slovnuk(self, table_name):    #  За вказан імям таблиці видає список Не всіх [(стовпців, тип_даних, відвед_кілкість_символ)]
        list_stovpciv_type = self.ekzemp_category.get_neccess_stovpci_and_type(table_name)
        return  list_stovpciv_type
       
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

class InsertTovar(QMainWindow):    #   Реалізує вкладку  - "Склад" -  "Внесення товару" 
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
        self.table_name_depend = None # Це імя залежної таблиці від табл Products, наприклад це може бути табл: Memory, Storage, Proccessor,..
        self.cat_tag = None   #  Це тег взятий з табл: Categories, щоби знати яку вибирати табл: Memory_det, Processor_det, ....
        self.dict_stovp_type_size = {}   # пустий словник типу: назва_стовпця : об'єкт QLineEdit, тип_даних, size 
        self.cat_id = None      # id вибраної КАТЕГОРІЇ    з табл Categories, яке користув вибрав в main випадаючому списку, наприклад: Процесори, Диски,....
        self.subcat_id = None   # id вибраної ПІДкатегорії з табл Categories, яке користув вибрав в sub випадаючому списку, наприклад: Intel Core, AMD Ryzen
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
        for cat_id, cat_name, cat_tag in category: # category = [(3, 'Процесори', 'cpu'), (7, 'Накопичувачі', 'storage'), (12, 'Оперативна память', 'ram'), (15, 'Материнська плата', 'mainboard')]
            self.vupad_spusok.addItem(cat_name, (cat_id, cat_tag))   #  addItem(видимий_текст, (приховані_дані, приховані_дані))
        self.vupad_spusok.currentIndexChanged.connect(self.show_sub_vupad_spusok)  # Коли корист вибирає якийсь елем у випадаючому списку, показуємо sub список під головн випад списком
        left_panel_ins_data.addWidget(self.vupad_spusok)  # Випадаюч список додаємо до лівої панелі
       
        self.sub_vupad_spusok = QComboBox()   # -------  Створюємо sub випадаючий список відразу, але ховаємо його --------
        self.sub_vupad_spusok.hide()
        self.sub_vupad_spusok.currentIndexChanged.connect(self.show_forma_vvody_danux)  # Коли корист вибирає якийсь елем у sub списку - показуємо форму вводу даних і таблицю виводу останіх введених даних користув
        left_panel_ins_data.addWidget(self.sub_vupad_spusok)   #  Випадаюч sub список додаємо до лівої панелі

        # ---------------------  Контейнер форми для введення даних в бд ----------------------------------------------
        self.forma_vvody = QWidget()   # Батьківський віджет для форми вводу інфи в бд
        self.forma_vvody.hide()
        self.text_forma_vvody = QFormLayout(self.forma_vvody)  # QFormLayout - клас який вирівн віджети у 2 стовпці: зліва - надпис, справа - поле вводу
        left_panel_ins_data.addWidget(self.forma_vvody)  # Форму вводу додаємо до лівої панелі
        
        self.btn_addto_sklad = QPushButton("ДОДАТИ НА СКЛАД")    # ------------------ Кнопка під формою ---------------------------
        self.btn_addto_sklad.hide()
        self.btn_addto_sklad.clicked.connect(self.receive_users_data_check_empty)  # При нажаті на кнопку отримуєм дані від користув, перевіряєм їх на правильність, на пусті поля
        left_panel_ins_data.addWidget(self.btn_addto_sklad)   # Кнопку додаемо до лівої панелі
        left_panel_ins_data.addStretch() # Притиснути все вгору
        # -----------------------------------------  ПРАВА ПАНЕЛЬ (Попередній перегляд залишків в таблиці) -----------------------------------------------
        right_panel_table = QVBoxLayout()
        self.ostani_vvedena = QLabel("📋 ОСТАННІ ВВЕДЕННЯ")   # Створює віджет (елемент інтерфейсу), який відображає текст 
        right_panel_table.addWidget(self.ostani_vvedena)
        self.ostani_vvedena.hide()
        self.table = QTableWidget()  # Создает виджет таблиці виводу останньої введеної інфи користувачем
        self.table.hide()
        right_panel_table.addWidget(self.table)
        
        # Додаємо панелі в головний лейаут
        layout.addLayout(left_panel_ins_data, 2)  # 1 частина ширини
        layout.addLayout(right_panel_table, 4) # 2 частини ширини
    
    def show_sub_vupad_spusok(self):  # Показує sub випадаючий список, після того як корист вибере щось з основного випад. списку
        self.sub_vupad_spusok.blockSignals(True)  # Тимчасово вимикаємо сигнали, щоб форма вводу не вискакувала завчасно при додавані елементів до sub випад списку
        self.cat_id, self.cat_tag = self.vupad_spusok.currentData()  # currentData(): Метод, который вертає прихов дані, а саме cat_id з vupad_spusok.addItem(cat_name, cat_id)
        sub_category = self.ekzemp_category.get_subcategory_by_id(self.cat_id) # за вказаним id виводимо id і підкатегоріїї, які є дітьми від категорії з цим id
        if sub_category:   #  Якщо користувач вибрав любу з підкатегорій окрім категорії по замовчуванню 
            self.sub_vupad_spusok.clear()    #  Очищуємо віджет перед оновленням 
            self.sub_vupad_spusok.addItem("Виберіть підкатегорію товара", 0)   # Додаємо дефолтний елемент першим до випадаючого списку
            for cat_id, cat_name in sub_category: # sub_category = [('SSD SATA',), ('SSD M2 Nvme',), ('SSD SAS',), ('HDD',)]
                self.sub_vupad_spusok.addItem(cat_name, cat_id)  # Додаємо до sub випадаючого списку елементи
            self.sub_vupad_spusok.setCurrentIndex(0)   # Форма вводу з'явиться лише тоді, коли ви перемкнетеся з "Виберіть підкатегорію товара" на реальний товар
            self.sub_vupad_spusok.blockSignals(False) # Вмикаємо сигнали назад
            self.btn_addto_sklad.hide()        #    Без цього рядка докінця не ховає кнопку при обрані підменю по замовченю
            self.forma_vvody.hide()            # Ховаємо форму, якщо вона була відкрита раніше для іншого товару
            self.table.hide()                  # Очищаємо таблицю показу щойно введених даних
            self.ostani_vvedena.hide()
            self.sub_vupad_spusok.show()
        else:       #  Якщо користувач вибрав категорії по замовчуванню 
            self.sub_vupad_spusok.hide()       #    Ховаємо випадаючий список, якщо підкатегорій немає
            self.forma_vvody.hide()            #    Ховаємо форму вводу, якщо підкатегорій немає
            self.table.hide()                  #    Ховаємо таблицю показу щойно введених даних
            self.ostani_vvedena.hide()
            self.btn_addto_sklad.hide()        #    Ховаємо кнопку під формою, якщо підкатегорій немає
       
    def show_forma_vvody_danux(self, index):   #  Виводить на екран форму вводу і таблицю виводу останіх введ даних при виборі ярїсь опції в підменю
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            self.forma_vvody.hide()
            self.table.hide()                  #    Ховаємо таблицю показу щойно введених даних
            self.btn_addto_sklad.hide()
            self.ostani_vvedena.hide()         #    Ховаємо текстову надпись
            return
        while self.text_forma_vvody.count():  # Доки кількість елементів у макеті більша за нуль
            item = self.text_forma_vvody.takeAt(0)  # Видаляє посилання на перший елемент (з індексом 0) з вашого макета (layout)
            if item.widget():
                item.widget().deleteLater()    #   Чи є цей елемент віджетом, якщо так то Видали цей об'єкт
        self.subcat_id = self.sub_vupad_spusok.currentData()   # id вибраного елемента з табл Categories в sub випадаючому списку
        
        list_stovp_datatype = self.formyem_slovnuk(Table_main_product) # [('Artukyl', 'nvarchar', 30), ('Nazva_tov', 'nvarchar', 100), ('Description', 'nvarchar', -1), ('Kilkist', 'int', None), ('Price', 'decimal', None)]
        korteg_table_name = self.ekzemp_category.get_name_table_by_tag(Table_tag, self.cat_tag) # по cat_tag шукаємо назву відпов таблиці, вертає кортеж типу: [('hardware.Storage_detail',)]
        self.table_name_depend =  korteg_table_name[0][0]  # беремо 1-ий елемент кортежу -  hardware.Storage_det
        list_stovp_datatype2 = self.formyem_slovnuk(self.table_name_depend)   # [('socket', 'nvarchar', 30), ('cores', 'int', None), ('threads', 'int', None), ('frequency', 'decimal', None), ('watt', 'int', None)]
        self.dict_stovp_type_size = {}   # Створюємо словник типу: назва_стовпця : об'єкт QLineEdit, тип_даних, розмір_або_точність    
        list_stovpciv_full = list_stovp_datatype + list_stovp_datatype2  # Обєднуємо списки отримані з таблиці Products і з таблиці залежної, напр, Memory, Storage,....
        
        self.dict_stovp_type_size.clear()  # очищаємо словник, якщо буде наприклад оновлення форми
        list_ukr_namestovp = []            # цей список передав в шабку-заголовок таблиці
        for stovpec, datatype, size in list_stovpciv_full: # Формується словник dict_stovp_type_size[stovpec] + наповнюєт. текст укр момою при формі вводу
            pole_vvody =  QLineEdit()   #  создаем однорядкове поле вводу даних
            korteg_ukr_namestovp = self.ekzemp_category.get_display_ukrtext(Table_translate, stovpec) # за вказан імям stovpec на анг отримуєм укр читабел текст при полі вводу даних звертаючись до таблиці бд
            ukr_namestovp = korteg_ukr_namestovp[0][0]    # беремо 1-ий елемент кортежу 
            list_ukr_namestovp.append(ukr_namestovp)  # формую список з україн назв 
            InputValidator.check_entered_data(pole_vvody, datatype, size)  # Виклик клас (декоратор методу) для накладання обмежень при вводі даних користув в форму вводу
            self.dict_stovp_type_size[stovpec] = ( pole_vvody, datatype, size)  #    Формується словник dict_stovp_type_size[stovpec] типу:  <PyQt6.QtWidgets.QLineEdit object at 0x00000162CB4898B0>, 'nvarchar', 30)      
            self.text_forma_vvody.addRow(f"{ukr_namestovp}:",  pole_vvody)  # Створ новий рядок у формі: назва - поле вводу
        self.table.setColumnCount(len(list_ukr_namestovp))   # Встановлюємо кількість колонок
        self.table.setHorizontalHeaderLabels(list_ukr_namestovp) # зверт до обєкту таблиці і встановл назви стовпців
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setMinimumSectionSize(100) # наприклад, 100 пікселів
        self.forma_vvody.show()
        self.ostani_vvedena.show()
        self.table.show()
        self.btn_addto_sklad.show()

    def formyem_slovnuk(self, table_name):    #  За вказан імям таблиці видає список Не всіх [(стовпців, тип_даних, відвед_кілкість_символ)]
        list_stovpciv_type = self.ekzemp_category.get_neccess_stovpci_and_type(table_name)
        return  list_stovpciv_type
    
    def receive_users_data_check_empty(self):   # Отримує користув дані з форми, перевіряє на пусті поля,
        is_valid = True
        list_all_data_user = []   #  В цей список буде поміщено всі дані які ввів користувач в форму вводу
        for stovpec, (pole_vvody, datatype, size) in self.dict_stovp_type_size.items():
            users_data = pole_vvody.text().strip()   # Отримуємо дані які ввів користувач із кожного поля вводу
            if not users_data:   # Якщо користувач нічого не ввів
                is_valid = False
                break
            list_all_data_user.append(users_data) 
        if not is_valid:
            QMessageBox.warning(self, "Попередження", "Всі поля мають бути заповнені!") 
        else: 
            #QMessageBox.information(self, "Успіх", "Дані успішно занесені.")
            self.insert_in_tables(list_all_data_user)
             
    def insert_in_tables(self, list_users_data):
        list_korteg_stovpciv_bez_id = self.ekzemp_category.get_all_stovp_bez_identity_datetime(Table_main_product) # для головн таблиці отримуєм список стовпців, які підставляємо в INSERT
        list_stovp_bez_id_maintabl = ", ".join([f"[{item[0]}]" for item in list_korteg_stovpciv_bez_id])  # перетв з списку кортежів в список типу: [Category_catid], [Artukyl], [Nazva_tov], [Description], [Kilkist], [Price]
        list_korteg_all_stovp_depend_tabl = self.ekzemp_category.get_name_all_stovpciv_table(self.table_name_depend) # для залежн табл отримуємо список всіх стовпців
        list_all_stovp_depend_tabl = ", ".join([f"[{item[0]}]" for item in list_korteg_all_stovp_depend_tabl]) # перетв з списку кортежів в список типу: [memid], [mem_type], [capacity], [speed]
        kilk_stovp_main_tabl = len(list_korteg_stovpciv_bez_id)   #  Кількість стовпців головн таблиці які потрібно заповнити в запиті INSERT
        kilk_stovp_depend_tabl = len(list_korteg_all_stovp_depend_tabl)
        list_users_data.insert(0, self.subcat_id)     # Додаємо id на першу позиц., щоб вставити в табл Products
        list_dani_main_tabl = list_users_data[:kilk_stovp_main_tabl]  # Зріс, тобто весь список ділимо на список для головн табл
        list_dani_depend_tabl = list_users_data[kilk_stovp_main_tabl:] # Зріс, тобто список для залежн табл
        placeholders_depend = "@LastInsId, " + ", ".join(["?"] * (kilk_stovp_depend_tabl - 1))
        query = f"""SET NOCOUNT ON;  -- <--- без цього коду Python не сприймає ошибки через THROW
                        BEGIN TRY
                           BEGIN TRANSACTION; 
                               DECLARE @LastInsId INT; 
                               INSERT INTO {Table_main_product} ({list_stovp_bez_id_maintabl}) 
                                  VALUES ({', '.join(['?'] * kilk_stovp_main_tabl)});
                               SET @LastInsId = SCOPE_IDENTITY();
                               INSERT INTO {self.table_name_depend} ({list_all_stovp_depend_tabl}) 
                                  VALUES ({placeholders_depend});
                           COMMIT TRANSACTION;
                        END TRY
                        BEGIN CATCH
                           IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
                            THROW;     -- <--- ОБЯЗАТЕЛЬНО: перерве виконання і пробрасывает ошибку в Python
                        END CATCH"""
        params =  list_dani_main_tabl + list_dani_depend_tabl
        try:
            with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
                 cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
                 cursor.execute(query, params)     # Виконуємо запит через курсор
                 conn.commit()
            # --------------- Вставка введених даних в таблицу відображення на екранв справа, це не вставка в табл бд -----------------------     
            kilk_radkiv = self.table.rowCount()   #  возвращает общее количество строк, существующих в таблице на данный момент
            self.table.insertRow(kilk_radkiv)  # физически создаем новую пустую строку в таблице QTableWidget
            for nomer_col, data in enumerate(list_users_data[1:]):   # (0, Артикул) (1, Назва товару) (2, Опис) ,...... і пропуск id тому 1:
                item_contain = QTableWidgetItem(str(data))  # Кожне значення завертаємо в спеціальний контейнер, бо інакше не можна закинути текст в табл
                self.table.setItem(kilk_radkiv, nomer_col, item_contain)  # кладем созданный «контейнер» в конкретную ячейку: індекс_нов_строки, номер_колонки, само упаковане значення
            self.table.scrollToBottom()    # Опционально: прокрутка к новой записи

            QMessageBox.information(self, "Успіх", "Дані успішно занесені в бд.")
            for stovpec in self.dict_stovp_type_size:    #  Очистка всіх полів вводу після успішного весення в бд
                pole_vvody = self.dict_stovp_type_size[stovpec][0]   #
                pole_vvody.clear()
                 # автоматично викличеться __exit__ для закриття з'єднання.  
        except pyodbc.Error as e:
            # Этот блок ловить ошибку, которую пробросил THROW из SQL
            QMessageBox.critical(self, "Помилка", f" Помилка бд при виконанні запиту: {e}")
        
 
      
     