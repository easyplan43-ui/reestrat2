from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, 
                             QHBoxLayout, QLabel, QTableWidget, QFormLayout,
                             QPushButton, QMessageBox, QApplication)
from constants import *
from conn_to_db import ZaputuTypepoint  # клас для підключення до бд
from dodat_classes import FormaVvody, TablManager, WorkwithWidgets, VupadSpusokManager, DictManager, DialogWindow, CheckBoxManager  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
from style import STOCK_STYLE
class InsNewSklad(QMainWindow):    #   Реалізує вкладку  - "Адміністратору" -  "+ Новий склад" 
    def __init__(self):
        super().__init__()
        self.ekzemp_typepoint = ZaputuTypepoint(Table_typepoint)   # Створюємо екземпляр класу для роботи з типами точок, передаючи назву таблиці
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
        # метод get_userdata_from_form є підписаний на сигнал data_submitted із класу FormaVvody 
        self.ekzemp_forma_vvody.data_submitted.connect(self.get_userdata_from_form) 
        #self.ekzemp_vupad_spusok.changed.connect(self.prepare_form_tabl_forma_vvody)  # Коли корист вибирає якийсь елем у випадаючому списку, показуємо sub список під головн випад списком

    def get_userdata_from_form(self, data_user): #  метод викликается автомат, коли у формі вводу натискають 'Внести' і дані перевірені і він отрим дані з форми вводу
        # Цей метод є ПІДПИСАНИМ на сигнал data_submitted із класу FormaVvody
        print(data_user)     #  де data_user = {'Назва точки': 'tocka33', 'Тип точки': ['Сервісний центр'], 'Місто': 'Lwow', 'Адреса': 'dancevica 4', 'Активний?': False}
       
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
       