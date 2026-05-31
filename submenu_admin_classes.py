from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, 
                             QHBoxLayout, QLabel, QTableWidget, QFormLayout,
                             QPushButton, QMessageBox, QApplication)
from constants import *
from conn_to_db import ZaputuTypepoint, ZaputuSkladu  # клас для підключення до бд
from dodat_classes import FormaVvody, TablManager, WorkwithWidgets, VupadSpusokManager, DictManager, DialogWindow, CheckBoxManager  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
from style import STOCK_STYLE
class InsNewSklad(QMainWindow):    #   Реалізує вкладку  - "Адміністратору" -  "+ Новий склад" 
    def __init__(self):
        super().__init__()
        self.ekzemp_typepoint = ZaputuTypepoint(Table_typepoint)   # Створюємо екземпляр класу для роботи з типами точок, передаючи назву таблиці
        self.ekzemp_skladu    = ZaputuSkladu(Table_skladu)  # Створ екземпляр класу для роботи зі складами а саме даними про них: назва, адреса, тип
        self.list_widgets = []
        self._init_ui() # метод дає дизайн і вигляд кнопок, випадаючих списків і форми вводу

    def _init_ui(self):
        QApplication.instance().setStyleSheet(STOCK_STYLE)
       
        central_widget = QWidget()  # Головний контейнер, який може містити інші елементи
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget) # Горизонтальний розподіл: Форма | Таблиця
        left_panel_ins_data = QVBoxLayout()       # ---------------- ЛІВА ПАНЕЛЬ (Введення даних + випадаючий список) -----------------
                
        right_panel_table = QVBoxLayout()  # тут буде таблиця яка відобр останні введення
        
        self.ekzemp_vupad_spusok = VupadSpusokManager(self.ekzemp_typepoint.get_type_points, "Виберіть тип точки") # Створ екземп класу по роботі з випад списками
        self.ekzemp_checkbox     = CheckBoxManager("Активний") # Створ екземп класу по роботі із прапорцями
        self.ekzemp_table        = TablManager(sortyvatu = False)   # Створ екземп класу по роботі із таблицею відображення інфи на екрані
        self.ekzemp_forma_vvody  = FormaVvody()   # поле вводу разом із кнопкою, але сигнал для кнопки є в класі FormaVvody
        self.ostani_vvedena = QLabel("📋 ОСТАННІ ВВЕДЕННЯ")   # Створює віджет (елемент інтерфейсу), який відображає текст 
        
        left_panel_ins_data.addWidget(self.ekzemp_forma_vvody)  # Випадаюч список
        left_panel_ins_data.addStretch() # Притиснути все вгору
        
        #right_panel_table.addWidget(self.ostani_vvedena)  # текст останні введення додаємо
        #right_panel_table.addWidget(self.ekzemp_table)  
        self.list_widgets = [self.ekzemp_forma_vvody] # Початк список віджетів, що тут додаш, то вже не треба буде редагувати цей список протягом цілого класу      
        #WorkwithWidgets.hide_widgets([self.ekzemp_forma_vvody, self.ostani_vvedena, self.ekzemp_table])
             
        # Додаємо панелі в головний лейаут
        main_layout.addLayout(left_panel_ins_data, 2)  # 1 частина ширини
        main_layout.addLayout(right_panel_table, 4) # 2 частини ширини
        self.prepare_form_tabl_forma_vvody() #  динамічно будуємо і наповнюємо нашу форму з БД
        
        # -------------------------------------------------- СИГНАЛИ --------------------------------------------------------------
        # метод get_userdata_from_form є ПІДПИСАНИЙ на сигнал data_submitted із класу FormaVvody 
        self.ekzemp_forma_vvody.data_submitted.connect(self.get_userdata_from_form) 
       
    def get_userdata_from_form(self, data_user): #  метод викликается автомат, коли у формі вводу натискають 'Внести' і дані перевірені і він отрим дані з форми вводу
        # Цей метод є ПІДПИСАНИМ на сигнал data_submitted із класу FormaVvody
        list_user_val = DictManager.get_list_from_val_dict(data_user) # виклик статич метод що вертає список даних які ввів користувач типу ['val1', 'val2', val3]
        self.prepare_to_insert(list_user_val)   # підготовка до INSERT і сам INSERT і передача йому  list_user_val  
         
    def prepare_form_tabl_forma_vvody(self): # підготовка формування таблиці виводу інфи або форми вводу, в залежності від дочірн класу
        list_kort= self.ekzemp_typepoint.get_neccess_stovpci_and_typejoin(Table_skladu)  # [('Назва точки', 'nvarchar', 50), ('Тип точки', 'nvarchar', 15), ('Місто', 'nvarchar', 20), ('Адреса', 'nvarchar', 50), ('Активний?', 'bit', 1)]
        if list_kort:
           dict_tabl = DictManager.form_dictionary(list_kort)  # {'Назва точки': {'type': 'nvarchar', 'size': 50}, 'Тип точки': {'type': 'nvarchar', 'size': 15},
           if dict_tabl:        # створ словник із ключем: "Тип точки" для випад списку і  "Активний?" для прапорця
               extern_wid_dict = {"Тип точки": self.ekzemp_vupad_spusok, "Активний?": self.ekzemp_checkbox} 
               self.ekzemp_forma_vvody.setup_form(dict_tabl, ext_widgets=extern_wid_dict)   #  формуємо форму вводу із випад списком
               #WorkwithWidgets.show_widgets(self.list_widgets)  # Виклик статич метод в класі WorkwithWidgets, який показує віджети
           else: 
               logger_db_conn.error(f"Не вдалося сформувати обєднаний словник стовпців для таблиці: {Table_skladu}")
               DialogWindow.form_dialog_wind("Помилка", f"Не вдалося сформувати обєднаний словник стовпців для таблиці: {Table_skladu}", QMessageBox.Icon.Warning)
               return 
        else:
            logger_db_conn.error(f"Не сформований список кортежів для таблиці: {Table_skladu}")
            DialogWindow.form_dialog_wind("Помилка", f"Не сформований словник для таблиці: {Table_skladu}", QMessageBox.Icon.Warning)
            return 
        
    def prepare_to_insert(self, list_users_data):
        list_korteg_stovpciv_bez_id = self.ekzemp_skladu.get_all_stovp_bez_identity_datetime() # для таблиці Skladu отримуєм список стовпців, які підставляємо в INSERT
        list_stovp_bez_id = ", ".join([f"[{item[0]}]" for item in list_korteg_stovpciv_bez_id])  # перетв з списку кортежів в список типу: [Category_catid], [Artukyl], [Nazva_tov], [Description], [Kilkist], [Price]
        kilk_stovp = len(list_korteg_stovpciv_bez_id)   #  Кількість стовпців головн таблиці які потрібно заповнити в запиті INSERT
        result = self.ekzemp_skladu.insert_in_tables(list_stovp_bez_id, kilk_stovp, list_users_data) 
        if result:  #  Якщо вставка даних в 2 таблиці пройшла успішно
             QMessageBox.information(self, "Успіх", "Дані успішно занесені в бд.")
        else:  #  Якщо дані не вставлені в бд   
             ex = self.ekzemp_skladu.error_zaputy  # звертаюсь до атрибута класу WorkDB, щоб отримати код поилки з exceptiona в методі execute_query_insert
             QMessageBox.critical(self, "Помилка", f" Помилка бд при виконанні запиту: {ex}") 
              