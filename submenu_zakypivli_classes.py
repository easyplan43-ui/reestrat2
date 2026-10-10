from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, QFrame, QHeaderView, QAbstractItemView,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout, QRadioButton,
                             QPushButton, QDateEdit, QApplication)
from PyQt6.QtCore import QDate
from check_functions import search_val_in_dict
from constants import *
from conn_to_db import ZaputuTypepoint, ZaputuSkladu, ZaputuAgentu  # клас для підключення до бд
from dodat_classes import DialogWindow, TablManager, WorkwithWidgets, VupadSpusokManager, DictManager, CellDataManag  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
from style import STOCK_STYLE
# Тільки класи для реалізації підменю "Склад". Незабудь новий створюваний клас відмітити в файлі: string_to_class
class BasicZakyp(QMainWindow):       #      Універс. Батьківський клас для Складу / Контрагенту
    def __init__(self, table_type, maintext_vupadspusky):  # сюда ми в дочір класах запихаємо назву таблиці яку нам потрібно: типи складів або типи агентів
        super().__init__()
        self.list_widgets = []
        self.data_komirka = CellDataManag()   # створюєм екземпл по роботі із коміркою виводу і вибору дати
        self.ekzemp_type_kontr = ZaputuTypepoint(table_type)   # Створ екземпляр класу для роботи з типами точок/контрагентів, передаючи назву таблиці
        QApplication.instance().setStyleSheet(STOCK_STYLE)   # Встановлюємо стиль із файлу стилів
        self.central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget) # Вертикальний розподіл: вгорі категорії, підкатегорії пошук, внизу - таблиця
        type_stovp = self.ekzemp_type_kontr.get_name_all_stovpciv_table() # дістаємо назви стовп таблиці, щоб  жорстко не прописувати їх в коді і передати їх через lambda
        self.ekzemp_vupad_spusok_typekontr = VupadSpusokManager(lambda *args: self.ekzemp_type_kontr.get_type_points(type_stovp[0][0], type_stovp[1][0]), maintext_vupadspusky) # Створ екземп класу по роботі з випад списками
        
    def form_secon_spus(self): # підготовка формування другого випад списку
        # Базова логіка підготовки: перевіряє індекс, повертає True, якщо індекс був 0 і форму сховано.
        index = self.ekzemp_vupad_spusok_typekontr.get_curr_index() # вивод текуч індекс/номер вибраного елементу в вип_списку - 0,1,2,3,....
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            WorkwithWidgets.hide_widgets(self.list_widgets) # Виклик Зовн статич метод з класу WorkwithWidgets, щоб сховати віджети
            return True  # заверш роботу бо корист вибрав категорію позамовченю
        else:  # Якщо користув обрав якусь реальну не дефолтну категорію
            return False

class IncomeTovar(BasicZakyp):    #----------------  дочір клас Реалізує вкладку  - Склади і магазини ---------------------------- 
    def __init__(self):
        super().__init__(Table_typeagent, "Виберіть тип агента")   # Виконати спочатку все що є в конструкторі базового класу, тобто запускаєм констр базового класу спочатку
        self._init_ui() # виклик початк методу з базового класу  дає дизайн і вигляд кнопок, випадаючих списків
                       
    def _init_ui(self):
        self.search_layout     = QHBoxLayout()                     #  Створюємо Горизонт панель де розміщено категорія і пошук 
        self.ekzemp_agent      = ZaputuAgentu(Table_agentu)        #  Створюємо екземпляр класу для роботи із агентами 
        self.ekzemp_type_sklad = ZaputuTypepoint(Table_typepoint)  #  Створ екземпляр по роботі із типами контрагентів
        self.ekzemp_sklad      = ZaputuSkladu(Table_skladu)        #  Створюємо екземпляр класу для роботи із складами 
        
        self.ekzemp_vupad_spusok_agent     = VupadSpusokManager(self.ekzemp_agent.get_agent_short_details_by_categ, "Виберіть агента")    
        type_stovp = self.ekzemp_type_sklad.get_name_all_stovpciv_table() # дістаємо назви стовп таблиці, щоб  жорстко не прописувати їх в коді і передати їх через lambda
        self.ekzemp_vupad_spusok_typesklad = VupadSpusokManager(lambda *args: self.ekzemp_type_sklad.get_type_points(type_stovp[0][0], type_stovp[1][0]), "Виберіть тип точки") # Створ екземп класу по роботі з випад списками
        self.ekzemp_vupad_spusok_sklad = VupadSpusokManager(self.ekzemp_sklad.get_sklad_short_details_by_categ, "Виберіть склад") # Створ екземп класу по роботі з випад списками

        self.search_layout.addWidget(self.data_komirka)                      # екземпляри класів/віджети додаємо до панелі пошуку інформації
        self.search_layout.addWidget(self.ekzemp_vupad_spusok_typekontr)
        self.search_layout.addWidget(self.ekzemp_vupad_spusok_agent)
        self.search_layout.addWidget(self.ekzemp_vupad_spusok_typesklad)     
        self.search_layout.addWidget(self.ekzemp_vupad_spusok_sklad)
      
        self.search_layout.addSpacing(25)  # Відступ між sub випад списком  і полем пошуку
        self.search_layout.addStretch()  # Ця "пружина" штовхає випадаючі списки і кнопку Оновити вліво

        self.list_widgets = [self.ekzemp_vupad_spusok_agent,  self.ekzemp_vupad_spusok_typesklad, self.ekzemp_vupad_spusok_sklad] # Початк список віджетів, що тут додаш, то вже не треба буде редагувати цей список протягом цілого класу] # Початк список віджетів, що тут додаш, то вже не треба #буде редагувати цей список протягом цілого класу
        
        WorkwithWidgets.hide_widgets(self.list_widgets)  # Викликаємо служб статичн метод в класі WorkwithWidgets який приховує кнопки і поле Search і 
        self.main_layout.addLayout(self.search_layout)  # макет пошуку (горизонтальний) стає частиною основного вертикального макета
        
        self.main_layout.addStretch()  # Ця "пружина" штовхає головний макет вгору
         # ---------------------------------------------------------- Сигнали ------------------------------------------------------------------ 
        self.ekzemp_vupad_spusok_typekontr.changed.connect(self.form_secon_spus)  # Коли корист вибире якийсь елем у випад_списку- виводимо результат його вибору у другий вип список 
        self.ekzemp_vupad_spusok_agent.changed.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 0, next_ind = 1)) # Коли корист вибире якийсь елем у 2-му випад_списку- показуємо третій випад список
        self.ekzemp_vupad_spusok_typesklad.changed.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 1, next_ind = 2)) # Коли корист вибере якийсь елем у 3 вип списку - показуємо 4 вип список
       
     #   Цей метод є визначен в базовому класі, а тут ми вже його доповнюємо        
    def  form_secon_spus(self, index):    #  формування другого випад списку
            if super().form_secon_spus():   #  # Викликаємо спільний код з базового класу і якщо True то,
                WorkwithWidgets.hide_widgets(self.list_widgets)
                return # виходимо бо користув вибрав меню по замовченю у випад списку
            returned_val = self.ekzemp_vupad_spusok_typekontr.get_curr_data() # [4, 'Сервісний центр']
            if returned_val is not None:
                 cat_id = returned_val[0] # Беремо перший елемент — це ID з бази даних (число 10)
                 self.ekzemp_vupad_spusok_agent.add_items(cat_id)
            WorkwithWidgets.show_widgets([self.list_widgets[0]])  # Виклик статич метод в класі WorkwithWidgets, який показує віджети

    def  obrob_kaskad_vupad_spus(self, curr_ind, next_ind):   #  формування третій  випад списку    
         curr_vupad_spus = self.list_widgets[curr_ind]
         next_vupad_spus = self.list_widgets[next_ind] 
         if curr_vupad_spus.get_curr_index() == 0:    # Перевіряємо поточний індекс випад списку на якому зараз клацає оператор
            WorkwithWidgets.hide_widgets(self.list_widgets[next_ind:])  # Якщо обрано дефолтний рядок "Виберіть ...", ховаємо наступний випад список
            return
         returned_val = curr_vupad_spus.get_curr_data()  # Якщо вибрано реальне значення, беремо його ID
         if returned_val is not None:
             select_id = returned_val[0]
             next_vupad_spus.add_items(select_id)    # Заповнюємо наступний список, передаючи туди цей ID 
             WorkwithWidgets.show_widgets([next_vupad_spus])  # Виклик статич метод в класі WorkwithWidgets, який показує віджети   


             

       

