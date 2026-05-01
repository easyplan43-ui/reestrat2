from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, QGroupBox,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout, QRadioButton,
                             QPushButton, QHeaderView, QFrame, QAbstractItemView, QMessageBox)
from PyQt6.QtGui import QFont, QColor
from constants import *
from conn_to_db import ZaputuCategoriesDB, ZaputuProductDB  # клас для підключення до бд
from dodat_classes import InputValidator, DialogWindow, TableManager, WorkwithWidgets  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
class InsNewSklad(QMainWindow):    #   Реалізує вкладку  - "Адміністратору" -  "+ Новий склад" 
    def __init__(self):
        super().__init__()
        self.ekzemp_category = ZaputuCategoriesDB(Table_category)   # Створюємо екземпляр класу для роботи з категоріями, передаючи назву таблиці
        self.ekzemp_product = ZaputuProductDB(Table_main_product)    # Створюємо екземпляр класу для роботи з товарами, передаючи назву таблиці
        self.table_name_depend = None # Це імя залежної таблиці від табл Products, наприклад це може бути табл: Memory, Storage, Proccessor,..
        self.cat_tag = None   #  Це тег взятий з табл: Categories, щоби знати яку вибирати табл: Memory_det, Processor_det, ....
        self.dict_stovp_type_size = {}   # пустий словник типу: назва_стовпця : об'єкт QLineEdit, тип_даних, size 
        self.cat_id = None      # id вибраної КАТЕГОРІЇ    з табл Categories, яке користув вибрав в main випадаючому списку, наприклад: Процесори, Диски,....
        self.subcat_id = None   # id вибраної ПІДкатегорії з табл Categories, яке користув вибрав в sub випадаючому списку, наприклад: Intel Core, AMD Ryzen
        self.category = self.ekzemp_category.get_category_and_id()   # отримуєм назви категорій і її id з таблиці типу: [(3, 'Процесори'), (7, 'Накопичувачі'), (12, 'Оперативна память'), (15, 'Материнська плата')]
       
        if not self.category:
            return  # Виходимо з функції, щоб не дійшло до циклу for
        
        self._init_ui() # метод дає дизайн і вигляд кнопок, випадаючих списків і форми вводу

    def _init_ui(self):
        self.setStyleSheet("""
               QMainWindow { background-color: #f4f4f9; }
               QLabel { font-size: 14px; color: #333; font-weight: bold; }
               QLineEdit, QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; background: white; }
               QPushButton { background-color: #2c3e50; color: white; padding: 10px; font-weight: bold; border-radius: 4px; }
               QPushButton:hover { background-color: #34495e; }
               QTableWidget { background-color: white; border: 1px solid #ddd; }
        """)
        
        central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget) # Горизонтальний розподіл: Форма | Таблиця
        left_panel_ins_data = QVBoxLayout()       # ---------------- ЛІВА ПАНЕЛЬ (Введення даних + випадаючий список) -----------------
                
        right_panel_table = QVBoxLayout()  # тут буде таблиця яка відобр останні введення
        
        self.vupad_spusok = QComboBox()   # Створюємо ---- «Головн випадаючий список»  
        self.sub_vupad_spusok = QComboBox()   # Створюємо sub випадаючий список 
        self.forma_vvody = QWidget()   # Батьківський віджет для форми вводу інфи в бд
        self.text_forma_vvody = QFormLayout(self.forma_vvody)  # QFormLayout - клас який вирівн віджети у 2 стовпці: зліва - надпис, справа - поле вводу
        self.btn_addto_sklad = QPushButton("ДОДАТИ НА СКЛАД")    # ------------------ Кнопка під формою -------
        self.ostani_vvedena = QLabel("📋 ОСТАННІ ВВЕДЕННЯ")   # Створює віджет (елемент інтерфейсу), який відображає текст 
        self.table = QTableWidget()  # Создает виджет таблиці виводу останньої введеної інфи користувачем
       
        self.vupad_spusok.clear()    #  Очищуємо віджет перед оновленням (щоб категорії не дублювалися)
        self.vupad_spusok.addItem("Виберіть категорію товара", (0, None))   # Додаємо дефолтний елемент першим до випадаючого списку
        
        for cat_id, cat_name, cat_tag in self.category: # category = [(3, 'Процесори', 'cpu'), (7, 'Накопичувачі', 'storage'), (12, 'Оперативна память', 'ram'), (15, 'Материнська плата', 'mainboard')]
            self.vupad_spusok.addItem(cat_name, (cat_id, cat_tag))   #  addItem(видимий_текст, (приховані_дані, приховані_дані))
        
        left_panel_ins_data.addWidget(QLabel("📦 КАТЕГОРІЯ"))  # Створює віджет (елемент інтерфейсу), який відображає текст або зображення. 
        left_panel_ins_data.addWidget(self.vupad_spusok)  # Випадаюч список додаємо до лівої панелі
        left_panel_ins_data.addWidget(self.sub_vupad_spusok)   #  Випадаюч sub список додаємо до лівої панелі
        left_panel_ins_data.addWidget(self.forma_vvody)  # Форму вводу додаємо  лівої панелі
        left_panel_ins_data.addWidget(self.btn_addto_sklad)   # Кнопку додаемо до лівої панелі
        left_panel_ins_data.addStretch() # Притиснути все вгору
        
        right_panel_table.addWidget(self.ostani_vvedena)  # текст останні введення додаємо
        right_panel_table.addWidget(self.table)       
        WorkwithWidgets.hide_widgets([self.sub_vupad_spusok, self.forma_vvody, self.btn_addto_sklad, self.ostani_vvedena, self.table])
             
        # Додаємо панелі в головний лейаут
        layout.addLayout(left_panel_ins_data, 2)  # 1 частина ширини
        layout.addLayout(right_panel_table, 4) # 2 частини ширини
             # ---------------------------- Привязка сигналів до функцій   ---------------------------------
        self.vupad_spusok.currentIndexChanged.connect(self.show_sub_vupad_spusok)  # Коли корист вибирає якийсь елем у випадаючому списку, показуємо sub список під головн випад списком
        self.sub_vupad_spusok.currentIndexChanged.connect(self.show_forma_vvody_danux)  # Коли корист вибирає якийсь елем у sub списку - показуємо форму вводу даних і таблицю виводу останіх введених даних користув
        self.btn_addto_sklad.clicked.connect(self.receive_users_data_check_empty)  # При нажаті на кнопку отримуєм дані від користув, перевіряєм їх на правильність, на пусті поля

    def _create_pole_vvody(self, pidkazka, datatype, size):   # Створює однорядкове поле вводу даних
        pole_vvody =  QLineEdit()   #  создаем однорядкове поле вводу даних   
        pole_vvody.setPlaceholderText(pidkazka) # Підказку беремо і запихаємо всередину поля вводу
        InputValidator.check_entered_data(pole_vvody, datatype, size)  # Виклик клас (декоратор методу) для накладання обмежень при вводі даних користув в форму вводу
        return pole_vvody

    def _create_pidkazku_placehold(self, datatype, size):  # Створює підказки для Placeholderiv, тобто в середині поля вводу
        if datatype == 'decimal':   # Це блок підказок в полі вводу 
            max_digits = size - 2
            pidkazka = f"Напр.: {'9' * max_digits}.99"
        elif datatype in ('varchar', 'nvarchar'): 
            pidkazka = f"Макс к-ть симв.: {size}"  
        elif datatype == "int":
            pidkazka = f"Тільки цілі числа, напр. 1234"    
        else: 
            return ""    
        return pidkazka    

    def _form_spusok_ukr_stovp(self, list_stovpciv_full):   # формує список  list_ukr_namestovp - українських назв для англ стовпців в таблиці
        self.dict_stovp_type_size = {}   # Створюємо словник типу: назва_стовпця : об'єкт QLineEdit, тип_даних, розмір_або_точність 
        self.dict_stovp_type_size.clear()  # очищаємо словник, якщо буде наприклад оновлення форми
        list_ukr_namestovp = []            # цей список передав в шабку-заголовок таблиці
        for stovpec, datatype, size in list_stovpciv_full: # Формується словник dict_stovp_type_size[stovpec] + наповнюєт. текст укр момою при формі вводу
            pidkazka = self._create_pidkazku_placehold(datatype, size) # Виклик служб метод, який створює підказки для Placeholderiv
            pole_vvody = self._create_pole_vvody(pidkazka, datatype, size)  # Виклик служб метод, який створює однорядкове поле вводу даних
            korteg_ukr_namestovp = self.ekzemp_category.get_display_ukrtext(Table_translate, stovpec) # за вказан імям stovpec на анг отримуєм укр читабел текст при полі вводу даних звертаючись до таблиці бд
            if not korteg_ukr_namestovp:
                return  # Виходимо з функції, щоб не дійшло до циклу for
            ukr_namestovp = korteg_ukr_namestovp[0][0]    # беремо 1-ий елемент кортежу 
            list_ukr_namestovp.append(ukr_namestovp)  # формую список з україн назв 
            self.dict_stovp_type_size[stovpec] = (pole_vvody, datatype, size)  #    Формується словник dict_stovp_type_size[stovpec] типу:  <PyQt6.QtWidgets.QLineEdit object at 0x00000162CB4898B0>, 'nvarchar', 30)      
            self.text_forma_vvody.addRow(f"{ukr_namestovp}:",  pole_vvody)  # Створ новий рядок у формі: назва - поле вводу
        return list_ukr_namestovp   

    def show_sub_vupad_spusok(self):  # Показує sub випадаючий список, після того як корист вибере щось з основного випад. списку
        self.cat_id, self.cat_tag = self.vupad_spusok.currentData()  # currentData(): Метод, который вертає прихов дані, а саме cat_id з vupad_spusok.addItem(cat_name, cat_id)
        sub_categories = self.ekzemp_category.get_subcategory_by_id(self.cat_id) # за вказаним id виводимо id і підкатегоріїї, які є дітьми від категорії з цим id
        list_widgets = [self.btn_addto_sklad, self.forma_vvody, self.table, self.ostani_vvedena]
        WorkwithWidgets.forming_sub_vupad_spusok(self.sub_vupad_spusok, list_widgets, sub_categories)  # Виклик статич методу з класу WorkwithWidgets, що 
                 
    def show_forma_vvody_danux(self, index):   #  Виводить на екран форму вводу і таблицю виводу останіх введ даних при виборі ярїсь опції в підменю
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            WorkwithWidgets.hide_widgets([self.btn_addto_sklad, self.forma_vvody, self.table, self.ostani_vvedena]) # Виклик Зовн статич метод з класу WorkwithWidgets, щоб сховати віджети
            return
        while self.text_forma_vvody.count():  # Доки кількість елементів у макеті більша за нуль
            item = self.text_forma_vvody.takeAt(0)  # Видаляє посилання на перший елемент (з індексом 0) з вашого макета (layout)
            if item.widget():   # перевіряє, чи є цей елемент віджетом (кнопкою чи полем вводу), а не просто порожнім простором
                item.widget().deleteLater()    #   безпечно видаляє віджет із пам'яті, щоб він не залиш при переключені між категоріями.
        self.table.setRowCount(0)       # Повністю очищає всі рядки з даними в таблиці, при виборі корист іншої категорії
        self.table.setColumnCount(0)    # (Опціонально) очищає колонки, якщо їх набір теж змінюється в таблиці, при виборі корист іншої категорії  
        self.subcat_id = self.sub_vupad_spusok.currentData()   # id вибраного елемента з табл Categories в sub випадаючому списку
        
        list_stovp_datatype = self.ekzemp_product.get_neccess_stovpci_and_type(Table_main_product)   # [('Artukyl', 'nvarchar', 30), ('Nazva_tov', 'nvarchar', 100), ('Description', 'nvarchar', -1), ('Kilkist', 'int', None), ('Price', 'decimal', None)]
        korteg_table_name = self.ekzemp_category.get_name_table_by_tag(Table_tag, self.cat_tag) # по cat_tag шукаємо назву відпов залежн таблиці, вертає кортеж типу: [('hardware.Storage_detail',)]
        if not korteg_table_name:
            return  # Виходимо з функції, щоб не дійшло до циклу for
        self.table_name_depend =  korteg_table_name[0][0]  # беремо 1-ий елемент кортежу -  hardware.Storage_det
        list_stovp_datatype2 = self.ekzemp_product.get_neccess_stovpci_and_type(self.table_name_depend)
        list_stovpciv_full = list_stovp_datatype + list_stovp_datatype2  # Обєднуємо списки отримані з таблиці Products і з таблиці залежної, напр, Memory, Storage,....
        list_ukr_namestovp = self._form_spusok_ukr_stovp(list_stovpciv_full)
        TableManager.setup_headers(self.table, list_ukr_namestovp) # Звертаємся до зовн статичн класу з методом який налаштовує назви колонок
        WorkwithWidgets.show_widgets([self.forma_vvody, self.ostani_vvedena, self.table, self.btn_addto_sklad]) # показуємо віджети
       
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
            self.prepare_to_insert(list_all_data_user)
  