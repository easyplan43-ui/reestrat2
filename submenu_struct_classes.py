from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, QFrame, QHeaderView, QAbstractItemView,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout, QRadioButton,
                             QPushButton, QMessageBox, QApplication)
from PyQt6.QtGui import QFont, QColor
#from PyQt6.QtCore import pyqtSignal  # для спілкування обєктів між собою для сигналів і випад списків
from check_functions import search_val_in_dict
from constants import *
from conn_to_db import ZaputuTypepoint, ZaputuSkladu  # клас для підключення до бд
from dodat_classes import DialogWindow, TablManager, WorkwithWidgets, VupadSpusokManager, FormaVvody, DictManager  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
from style import STOCK_STYLE
# Тільки класи для реалізації підменю "Склад". Незабудь новий створюваний клас відмітити в файлі: string_to_class
class BasicUnion(QMainWindow):       #      Батьківський клас по Складу
    def __init__(self):
        super().__init__()
        self.ekzemp_typepoint = ZaputuTypepoint(Table_typepoint)   # Створюємо екземпляр класу для роботи з типами точок, передаючи назву таблиці
        self.ekzemp_sklad     = ZaputuSkladu(Table_skladu)    # Створюємо екземпляр класу для роботи із складами  

        self.dict_stovp_main = []
        self.list_widgets = []
        self.widg_to_hide = []     # Цей список я використ в методі prepare_form_sub_vupad_spus, де дочірні класи сюда перед різні віджети to hide
        self.pered_func_stovp = None  # для передачі назви методу, який зверт до бд і витягає назви потрібних стовп для кожного доч класу різні

        QApplication.instance().setStyleSheet(STOCK_STYLE)   # Встановлюємо стиль із файлу стилів
        self.central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget) # Вертикальний розподіл: вгорі категорії, підкатегорії пошук, внизу - таблиця

        self.ekzemp_vupad_spusok = VupadSpusokManager(self.ekzemp_typepoint.get_type_points, "Виберіть тип точки") # Створ екземп класу по роботі з випад списками
        self.ekzemp_table            = TablManager(sortyvatu = True)   # Створ екземп класу по роботі із таблицею відображення інфи на екрані
      
    def _get_spusok_stovp_transl(self, tablename):  # //tested// для конкр таблиці дістає список стовпців, які треба перек на україн і вивести в таблицю на екран
            if tablename is None:
                list_kort= self.pered_func_stovp() # дочір класи перед різні назви методів, щоб витягнути різні стовпці із бд типу: [('Артикул', 'artukyl', 'varchar', 25), ('Назва товару', 'nazva_tov', 'nvarchar', 50),
            else:
                list_kort = self.pered_func_stovp(tablename) # дочір класи перед різні назви методів, щоб витягнути різні стовпці із бд [("Тип пам'яті", 'mem_type', 'varchar', 50), ("Обє'м Гб", 'capacity', 'int', 10),
            return DictManager.form_dictionary(list_kort)  # зверт до статичного методу, щоб отрим словник зі списку кортежів
            # повертаємо словник типу : {'Артикул': ('artukyl', 'varchar', 25), 'Назва товару': ('nazva_tov', 'nvarchar', 50), 'Опис': ('description', 'nvarchar', 200),    

    def prepare_form_tabl_forma_vvody(self): # підготовка формування таблиці виводу інфи або форми вводу, в залежності від дочірн класу
        # Базова логіка підготовки: перевіряє індекс, повертає True, якщо індекс був 0 і форму сховано.
        index = self.ekzemp_vupad_spusok.get_curr_index() # вивод текуч індекс/номер вибраного елементу в вип_списку - 0,1,2,3,....
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            WorkwithWidgets.hide_widgets(self.list_widgets) # Виклик Зовн статич метод з класу WorkwithWidgets, щоб сховати віджети
            return True  # заверш роботу бо корист вибрав категорію позамовченю
        else:  # Якщо користув обрав якусь реальну не дефолтну категорію
            return False
            
class SkladandMarket(BasicUnion):    #----------------  дочір клас Реалізує вкладку  - "Склад" -  "Залишок товару" ---------------------------- 
    def __init__(self):
        super().__init__()   # Виконати спочатку все що є в конструкторі базового класу, тобто запускаєм констр базового класу спочатку
        self._init_ui() # виклик початк методу з базового класу  дає дизайн і вигляд кнопок, випадаючих списків
                       
    def _init_ui(self):
        self.search_layout    = QHBoxLayout()            #     Створюємо Горизонт панель де розміщено категорія і пошук 
        self.pered_func_stovp = self.ekzemp_sklad.get_all_stovp_bez_identity  # передаю назву метода який витяг назви стовп із бд
        
        self.search_layout.addWidget(self.ekzemp_vupad_spusok)      # Екземпляр Випадаючого списоку додаємо до панелі пошуку інформації
        self.search_layout.addSpacing(25)  # Відступ між sub випад списком  і полем пошуку
        self.search_layout.addStretch()  # Ця "пружина" штовхає випадаючі списки і кнопку Оновити вліво

        self.list_widgets = [self.ekzemp_table] # Початк список віджетів, що тут додаш, то вже не треба буде редагувати цей список протягом цілого класу
        
        WorkwithWidgets.hide_widgets(self.list_widgets)  # Викликаємо служб статичн метод в класі WorkwithWidgets який приховує кнопки і поле Search і 
        self.main_layout.addLayout(self.search_layout)  # макет пошуку (горизонтальний) стає частиною основного вертикального макета
        
        self.main_layout.addWidget(self.ekzemp_table, stretch=1)   #  stretch=1 означає "забрати все вільне місце"
        self.main_layout.addStretch()  # Ця "пружина" штовхає головний макет вгору

        self.ekzemp_vupad_spusok.changed.connect(self.prepare_form_tabl_forma_vvody)  # Коли корист вибире якийсь елем у випад_списку- виводимо таблицю 
         # ---------------------------------------------------------- Сигнали ------------------------------------------------------------------
       
     #   Цей метод є визначен в базовому класі, а тут ми вже його доповнюємо        
    def  prepare_form_tabl_forma_vvody(self):   #  Підготовка до формув табл, підгот укр назв стовпців,
            if super().prepare_form_tabl_forma_vvody():   #  # Викликаємо спільний код з базового класу і якщо True то,
                return # виходимо бо користув вибрав меню по замовченю у випад списку
            self.dict_stovp_main = self._get_spusok_stovp_transl(None)
            if self.dict_stovp_main: # Якщо є словник типу: {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}, 'Назва товару': {'name': 'nazva_tov', 'type': 'nvarchar', 'size': 50}
                list_ukr_namestovp = DictManager.get_list_by_key(self.dict_stovp_main, None, target = 'ukr')  # беремо назви стовпців українською
                if list_ukr_namestovp: # Якщо існує список укр стовп із 2-х табл типу: ['Артикул', 'Назва товару', 'Опис', 'Кількість', 'Ціна', 'Створено', "Роз'єм/Сокет", 'Чипсет', 'Форм-фактор', 'Кількість слотів']
                    rows = self.select_prod()   # беремо з бази сирий рядок типу: [('SAS-SG-360', 'Диск SAS Seagate 360 ', '2 SFF', 5, Decimal('87.00'), datetime.datetime(2026, 3, 31, 17, 16, 17, 570000), 'SAS-2', 360, 6000), і тд до кінця табл
                    if not rows:
                       self.ekzemp_table.clear_table()   # Все строки, которые были в таблице, мгновенно удаляются
                       DialogWindow.form_dialog_wind("Помилка", f"Не вдалося прочитати дані із таблиці: {Table_skladu}", QMessageBox.Icon.Warning)
                       return  # Виходимо з функції, бо немає даних з бази немає подальшого сенсу                         
                    self.ekzemp_table.set_headers(list_ukr_namestovp) # Встанов кількість стовпців і їх назви (шабку таблиці)
                    self.ekzemp_table.fill_table(rows, bagatovum=True)  #  Заповнення таблиці даними
                    WorkwithWidgets.show_widgets(self.list_widgets)  # Виклик статич метод в класі WorkwithWidgets, який показує віджети
                else: 
                    logger_db_conn.error(f"Не сформовано список українських назв стовпців")
                    DialogWindow.form_dialog_wind("Помилка", f"Не сформовано список українських назв стовпців", QMessageBox.Icon.Warning)
                    return []   
            else:    
                logger_db_conn.error(f"Не сформований словник для таблиці: {Table_main_product} або {self.table_name_depend}") 
                DialogWindow.form_dialog_wind("Помилка", f"Не сформований словник для таблиці: {Table_main_product} або {self.table_name_depend}", QMessageBox.Icon.Warning) 
                return []     

    def select_prod(self): # Підгот служб дані для SELECT, і зверт або до одного методу щоб зробити SELECT всього в таблицю відобр
           # або до іншого методу, щоб здійснити SELECT LIKE тобто пошук при нажаті на кнопку SEARCH
           users_value = self.ekzemp_vupad_spusok.get_curr_string() # вивод значення яке обрав корист зі випадаючого списку
           name_coloms = [item['name'] for item in self.dict_stovp_main.values()]
           name_coloms_right = ", ".join(name_coloms)   # без цього обєднання із комою не працює SELECT
           result = self.ekzemp_sklad.get_sklad_details_by_categ(name_coloms_right, users_value)
           return result
          

