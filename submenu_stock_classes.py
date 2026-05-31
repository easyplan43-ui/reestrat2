from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, QFrame, QHeaderView, QAbstractItemView,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout, QRadioButton,
                             QPushButton, QMessageBox, QApplication)
from PyQt6.QtGui import QFont, QColor
#from PyQt6.QtCore import pyqtSignal  # для спілкування обєктів між собою для сигналів і випад списків
from check_functions import search_val_in_dict
from constants import *
from conn_to_db import ZaputuCategoriesDB, ZaputuProductDB  # клас для підключення до бд
from dodat_classes import DialogWindow, TablManager, WorkwithWidgets, VupadSpusokManager, FormaVvody, DictManager  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
from style import STOCK_STYLE
# Тільки класи для реалізації підменю "Склад". Незабудь новий створюваний клас відмітити в файлі: string_to_class
class BasicSklad(QMainWindow):       #      Батьківський клас по Складу
    def __init__(self):
        super().__init__()
        self.ekzemp_category = ZaputuCategoriesDB(Table_category)   # Створюємо екземпляр класу для роботи з категоріями, передаючи назву таблиці
        self.ekzemp_product = ZaputuProductDB(Table_main_product)    # Створюємо екземпляр класу для роботи з товарами, передаючи назву таблиці   
       
        self.table_name_depend = None # Це імя залежної таблиці від табл Products, наприклад це може бути табл: Memory, Storage, Proccessor,..
        self.cat_tag = None   #  Це тег взятий з табл: Categories, щоби знати яку вибирати табл: Memory_det, Processor_det, ....
        self.sub_cat_id = None    # цю змінну я буду викор в запиті SELECT WHERE sub_cat_id = Category_catid
        self.dict_stovp_main = []    # Словник типу {'Artukyl': {'type': 'varchar', 'size': 25}, для головн табл
        self.dict_stovp_depend = []  # Словник типу {'stor_type': {'type': 'varchar', 'size': 15} для залежн табл 
        self.list_widgets = []
        self.widg_to_hide = None     # Це я використ в методі prepare_form_sub_vupad_spus, де дочірні класи сюда перед різні віджети to hide
        self.pered_func_stovp = None  # для передачі назви методу, який зверт до бд і витягає назви потрібних стовп для кожного доч класу різні

        QApplication.instance().setStyleSheet(STOCK_STYLE)   # Встановлюємо стиль із файлу стилів
        self.central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget) # Вертикальний розподіл: вгорі категорії, підкатегорії пошук, внизу - таблиця

        self.ekzemp_vupad_spusok     = VupadSpusokManager(self.ekzemp_category.get_category_and_id, "Виберіть категорію товара") # Створ екземп класу по роботі з випад списками
        self.ekzemp_sub_vupad_spusok = VupadSpusokManager(self.ekzemp_category.get_subcategory_by_id, "Виберіть підкатегорію товара")
        self.ekzemp_table            = TablManager(sortyvatu = True)   # Створ екземп класу по роботі із таблицею відображення інфи на екрані
        self.ekzemp_forma_vvody      =  FormaVvody()   # поле вводу разом із кнопкою, але сигнал для кнопки є в класі FormaVvody

        # ------------------------------------------------------- СИГНАЛИ --------------------------------------------------------------
        # метод get_userdata_from_form є підписаний на сигнал data_submitted із класу FormaVvody 
        self.ekzemp_forma_vvody.data_submitted.connect(self.get_userdata_from_form)  #  Коли у вікні форми вводу відбуд подія data_submitted, то запуск метод get_userdata_from_form
        self.ekzemp_vupad_spusok.changed.connect(self.prepare_form_sub_vupad_spus)  # Коли корист вибире якийсь елем у випад_списку, показуємо sub список під головн випад списком
        self.ekzemp_sub_vupad_spusok.changed.connect(self.prepare_form_tabl_forma_vvody)  # Коли корист вибирає якийсь елем у sub списку - виводимо таблицю    
               
    def _get_spusok_stovp_transl(self, tablename):  # //tested// для конкр таблиці дістає список стовпців, які треба перек на україн і вивести в таблицю на екран
        if tablename is None:
            list_kort= self.pered_func_stovp() # дочір класи перед різні назви методів, щоб витягнути різні стовпці із бд типу: [('Артикул', 'artukyl', 'varchar', 25), ('Назва товару', 'nazva_tov', 'nvarchar', 50),
        else:
            list_kort = self.pered_func_stovp(tablename) # дочір класи перед різні назви методів, щоб витягнути різні стовпці із бд [("Тип пам'яті", 'mem_type', 'varchar', 50), ("Обє'м Гб", 'capacity', 'int', 10),
        return DictManager.form_dictionary(list_kort)  # зверт до статичного методу, щоб отрим словник зі списку кортежів
        # повертаємо словник типу : {'Артикул': ('artukyl', 'varchar', 25), 'Назва товару': ('nazva_tov', 'nvarchar', 50), 'Опис': ('description', 'nvarchar', 200),

    def _get_ukr_dict_type(self, table_with_tag):  #  //not tested yet// Служб метод зясовує яка залежн таблиця і дістає назви, тип, size стовпців з 2-х таблиць 
        self.sub_cat_id = self.ekzemp_sub_vupad_spusok.get_curr_data()[0]    # коли ти вибир щось із підвипад списку появляє self.sub_cat_id
        list_korteg_tablname = self.ekzemp_category.get_tag_nametable(table_with_tag) # korteg_table_name = [('cpu', 'hardware.Proccess_det'), ('mainboard', 'hardware.Mainboard_det'), ('ram', 'hardware.Memory_det'), ('storage', 'hardware.Storage_det')] 
        if not list_korteg_tablname:
            return [], [] 
        dict_tabl = DictManager.form_dictionary(list_korteg_tablname) # виклик статичн метод який перетвор список_кортежів в dictionary {'cpu': 'hardware.Proccess_det', 'mainboard': 'hardware.Mainboard_det', 'ram': 'hardware.Memory_det', 'storage': 'hardware.Storage_det'}
        self.table_name_depend = search_val_in_dict(dict_tabl, self.cat_tag) # за вказаним тегом шукаємо назву таблиці з допом зовн функції з файлу check_functions
        if not self.table_name_depend:
            return [], []
        dict_stovp_main = self._get_spusok_stovp_transl(None)        #  {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}, 'Назва товару': {'name': 'nazva_tov', 'type': 'nvarchar', 'size': 50},
        dict_stovp_depend = self._get_spusok_stovp_transl(self.table_name_depend)     # {"Роз'єм/Сокет": {'name': 'socket', 'type': 'varchar', 'size': 30}, 'Кількість ядер': {'name': 'cores', 'type': 'int', 'size': 10}, 
        return dict_stovp_main, dict_stovp_depend 
    
    def _get_list_col_name(self, dict_main, dict_dep, target): # унів метод для обєднання даних з двох словників у список
       if target == 'key' or target == 'ukr':    # Якщо потрібні ключі (українські назви)
           return list(dict_main) + list(dict_dep) 
       elif target == 0:  #  - 0 (або 'eng')   -> збирає 0-й елемент кортежу (наприклад, 'artukyl')
           return [val[0] for val in dict_main.values()] + [val[0] for val in dict_dep.values()]
       elif target == 1:   #  - 1 (або 'type')  -> збирає 1-й елемент кортежу (наприклад, 'varchar') 
           return [val[1] for val in dict_main.values()] + [val[1] for val in dict_dep.values()]
       elif target ==2:    #  - 2 (або 'size')  -> збирає 2-й елемент кортежу (наприклад, 25)
           return [val[2] for val in dict_main.values()] + [val[2] for val in dict_dep.values()]
       else: 
           return []    

    def get_userdata_from_form(self, data_user): #  метод викликается автомат, коли у формі вводу натискають 'Внести' і дані перевірені і він отрим дані з форми вводу
       # Цей метод є ПІДПИСАНИМ на сигнал data_submitted із класу FormaVvody
        list_user_val = DictManager.get_list_from_val_dict(data_user) # виклик статич метод що вертає список даних які ввів користувач типу ['val1', 'val2', val3]
        self.prepare_to_insert(list_user_val)   # це передача  list_user_val через метод-заглушку peredacha_list на дочірній клас 

    def prepare_to_insert(self, list_users_data):  # тут це метод-заглушка, для отримання і передачі списку list_users_data на дочірн клас
        pass

    def prepare_form_sub_vupad_spus(self, data): # Підготовка до формування sub_vupad_spusok
        if data:    # Якщо вибрано реальний елемент (не дефолт)
            WorkwithWidgets.hide_widgets([self.widg_to_hide])
            cat_id, _, self.cat_tag, *_ = data  # 1 і 3 елем з data присвою cat_id, cat_tag, а все інше (скільки б там не було) піде в порожнечу _
            self.ekzemp_sub_vupad_spusok.add_items(cat_id)  # за cat_id виводимо id і назву sub_категорії  
            self.ekzemp_sub_vupad_spusok.show()
        else:  # Якщо вибрано дефолтний елемент 
            WorkwithWidgets.hide_widgets([self.ekzemp_sub_vupad_spusok] + self.list_widgets)  # Викликаємо служб статичн метод в класі WorkwithWidgets який приховує кнопки і поле Search і  

    def prepare_form_tabl_forma_vvody(self): # підготовка формування таблиці виводу інфи або форми вводу, в залежності від дочірн класу
        # Базова логіка підготовки: перевіряє індекс, повертає True, якщо індекс був 0 і форму сховано.
        index = self.ekzemp_sub_vupad_spusok.get_curr_index() # вивод текуч індекс/номер вибраного елементу в вип_списку - 0,1,2,3,....
        if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
            WorkwithWidgets.hide_widgets(self.list_widgets) # Виклик Зовн статич метод з класу WorkwithWidgets, щоб сховати віджети
            return True  # заверш роботу бо корист вибрав категорію позамовченю
        else:  # Якщо користув обрав якусь реальну не дефолтну категорію
            return False
            
class ZalushTovary(BasicSklad):    #----------------  дочір клас Реалізує вкладку  - "Склад" -  "Залишок товару" ---------------------------- 
    def __init__(self):
        super().__init__()   # Виконати спочатку все що є в конструкторі базового касу 
        self._init_ui() # виклик початк методу з базового класу  дає дизайн і вигляд кнопок, випадаючих списків
                       
    def _init_ui(self):
        search_layout    = QHBoxLayout()  #     Створюємо Горизонт панель де розміщено категорія і пошук 
        #self.update_btn       = QPushButton("Оновити")    #    Створюємо кнопку Оновити дані з бд  
        #self.search_input     = QLineEdit()    #  Це поле пошуку чогось / поле вводу 
        #self.search_btn       = QPushButton("Пошук")     # --------------- Кнопка пошуку ----------
        self.widg_to_hide = self.ekzemp_table # в базов класі методу prepare_form_sub_vupad_spus, кажемо сховати self.ekzemp_table
        self.pered_func_stovp = self.ekzemp_product.get_all_stovp_bez_identity  # передаю назву метода який витяг назви стовп із бд
        search_layout.addWidget(self.ekzemp_vupad_spusok)      # Екземпляр Випадаючого списоку додаємо до панелі пошуку інформації
        search_layout.addWidget(self.ekzemp_sub_vupad_spusok)   #  Sub Випадаюч список додаємо до панелі пошуку інформації
        search_layout.addSpacing(25)  # Відступ між sub випад списком  і полем пошуку
        search_layout.addStretch()  # Ця "пружина" штовхає випадаючі списки і кнопку Оновити вліво

        self.list_widgets = [self.ekzemp_table] # Початк список віджетів, що тут додаш, то вже не треба буде редагувати цей список протягом цілого класу
        WorkwithWidgets.hide_widgets([self.ekzemp_sub_vupad_spusok] + self.list_widgets)  # Викликаємо служб статичн метод в класі WorkwithWidgets який приховує кнопки і поле Search і 

        self.main_layout.addLayout(search_layout)  # макет пошуку (горизонтальний) стає частиною основного вертикального макета
        self.main_layout.addWidget(self.ekzemp_table, stretch=1)   #  stretch=1 означає "забрати все вільне місце"
        self.main_layout.addStretch()  # Ця "пружина" штовхає головний макет вгору

    #   Цей метод є визначен в базовому класі, а тут ми вже його доповнюємо        
    def  prepare_form_tabl_forma_vvody(self):   #  Підготовка до формув табл, підгот укр назв стовпців,
        if super().prepare_form_tabl_forma_vvody():   #  # Викликаємо спільний код з базового класу і якщо True то,
            return # виходимо бо користув вибрав меню по замовченю у випад списку
        self.dict_stovp_main, self.dict_stovp_depend = self._get_ukr_dict_type(Table_tag)
        if self.dict_stovp_main and self.dict_stovp_depend: # Якщо є словники типу: {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}, 'Назва товару': {'name': 'nazva_tov', 'type': 'nvarchar', 'size': 50}
            list_ukr_namestovp = self._get_list_col_name(self.dict_stovp_main, self.dict_stovp_depend, 'key')  # беремо назви стовпців в обох словник і склад список укр назв стовпців
            if list_ukr_namestovp: # Якщо існує список укр стовп із 2-х табл типу: ['Артикул', 'Назва товару', 'Опис', 'Кількість', 'Ціна', 'Створено', "Роз'єм/Сокет", 'Чипсет', 'Форм-фактор', 'Кількість слотів']
                rows = self.select_prod()   # беремо з бази сирий рядок типу: [('SAS-SG-360', 'Диск SAS Seagate 360 ', '2 SFF', 5, Decimal('87.00'), datetime.datetime(2026, 3, 31, 17, 16, 17, 570000), 'SAS-2', 360, 6000), і тд до кінця табл
                if not rows:
                   self.ekzemp_table.clear_table()   # Все строки, которые были в таблице, мгновенно удаляются
                   DialogWindow.form_dialog_wind("Помилка", f"Не вдалося прочитати дані із таблиці: {self.table_name_depend}", QMessageBox.Icon.Warning)
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

    def select_prod(self):  # Підгот служб дані для SELECT і виклик метод, який виводить з обох таблиць: main і depend інфу в таблицу на екрані
        cortege_fk_prim_key = self.ekzemp_category.get_foreignkey(self.table_name_depend)  # отримуємо 1 - назву стовп з власт foreign key, 2- назву стовпця на який цей foreign key ссилається типу [('storid', 'Prodid')]
        cortege_fk_prim_key_where = self.ekzemp_category.get_foreignkey(Table_main_product) # з головн табл отримуємо назву стовпця з власт foreign key
        if not cortege_fk_prim_key or not cortege_fk_prim_key_where:    # Якщо не дістали Foreign Key з бд то:
            logger_db_conn.error(f"Не вдалося отримати ключі для JOIN або WHERE в таблиці: {self.table_name_depend}")
            return []
        col_main = [f"m.{col_name['name']}" for col_name in self.dict_stovp_main.values()]       # Поєднуємо m зі стовпцями головної табл
        col_depend = [f"d.{col_name['name']}" for col_name in self.dict_stovp_depend.values()]   # Поєднуємо d зі стовпцями залежної табл
        all_columns = ", ".join(col_main + col_depend) 
        # Нижче - Виклик метода класу ZaputuProductDB, який виводить всі характеристики продукта з двох таблиць WHERE за вибраною підкатегорією в sub випадаючому списку 
        result = self.ekzemp_product.get_product_details(all_columns, self.table_name_depend, cortege_fk_prim_key, cortege_fk_prim_key_where, self.sub_cat_id)
        return result
    
class InsertTovar(BasicSklad):     #----------------  дочір клас Реалізує вкладку  - "Склад" -  "Внесення товару" -------------------------------------------
    def __init__(self):
        super().__init__()    # Виконати спочатку все що є в конструкторі базового касу
        self._init_ui()       # метод дає дизайн і вигляд кнопок, випадаючих списків і форми вводу

    def _init_ui(self):
        self.cat_id = None      # id вибраної КАТЕГОРІЇ    з табл Categories, яке користув вибрав в main випадаючому списку, наприклад: Процесори, Диски,....
        self.widg_to_hide = self.ekzemp_forma_vvody # в базов класі методу prepare_form_sub_vupad_spus, кажемо сховати форму вводу + кнопка до неї
        self.pered_func_stovp = self.ekzemp_product.get_neccess_stovpci_and_typejoin # передаю назву метода який витяг назви стовп із бд
        horuz_layout = QHBoxLayout() # Горизонтальний розподіл: Форма | Таблиця
        left_panel_ins_data = QVBoxLayout()       # ---------------- ЛІВА ПАНЕЛЬ (Введення даних + випадаючий список) -----------------
        right_panel_table = QVBoxLayout()  # тут буде таблиця яка відобр останні введення
        #self.ostani_vvedena = QLabel("📋 ОСТАННІ ВВЕДЕННЯ")   # Створює віджет (елемент інтерфейсу), який відображає текст 
               
        left_panel_ins_data.addWidget(QLabel("📦 КАТЕГОРІЯ"))  # Створює віджет (елемент інтерфейсу), який відображає текст або зображення. 
        left_panel_ins_data.addWidget(self.ekzemp_vupad_spusok)  # Екземп Випадаюч список додаємо до лівої панелі
        left_panel_ins_data.addWidget(self.ekzemp_sub_vupad_spusok)   #  Випадаюч sub список додаємо до лівої панелі
        left_panel_ins_data.addWidget(self.ekzemp_forma_vvody)  # Форму вводу додаємо  лівої панелі
        left_panel_ins_data.addStretch() # Притиснути все вгору

        # right_panel_table.addWidget(self.ostani_vvedena)  # текст останні введення додаємо
        right_panel_table.addWidget(self.ekzemp_table, stretch=1)     #  stretch=1 означає "забрати все вільне місце"
         
        self.list_widgets = [self.ekzemp_forma_vvody, self.ekzemp_table] # Початк список віджетів, що тут додаш, то вже не треба буде редагувати цей список протягом цілого класу 
        WorkwithWidgets.hide_widgets([self.ekzemp_sub_vupad_spusok] + self.list_widgets)# # self.btn_addto_sklad, self.ostani_vvedena, self.table])
             
        # Додаємо панелі в головний лейаут
        horuz_layout.addLayout(left_panel_ins_data, 2)  # 1 частина ширини
        horuz_layout.addLayout(right_panel_table, 4) # 2 частини ширини

        self.main_layout.addLayout(horuz_layout)  # горизон макет з формою вводу і таблицею стає частиною основного вертикального макета
        self.main_layout.addStretch()  # Ця "пружина" штовхає головний макет вгору
       
    #   Цей метод є визначен в базовому класі, а тут ми вже його доповнюємо        
    def prepare_form_tabl_forma_vvody(self):   #  Підготовка до формув форми вводу
        if super().prepare_form_tabl_forma_vvody():   #  # Викликаємо спільний код з базового класу і якщо True то,
            return # виходимо бо користув вибрав меню по замовченю у випад списку
        self.dict_stovp_main, self.dict_stovp_depend = self._get_ukr_dict_type(Table_tag) #  {'Артикул': {'type': 'varchar', 'size': 25}, 'Назва товару': {'type': 'nvarchar', 'size': 50},
        if self.dict_stovp_main and self.dict_stovp_depend: # Якщо є словники типу: {'Тип диска': {'type': 'varchar', 'size': 15}, "Обє'м Тб": {'type': 'int', 'size': 10}, 'Швидкість Мб/c': {'type': 'int', 'size': 10}}
           gener_dict = DictManager.union_dicts(self.dict_stovp_main, self.dict_stovp_depend)   # обєднуємо словники  в один з допом базового методу
           if gener_dict:  # Якщо вдалося обєднати 2 словн в один: 
              self.ekzemp_forma_vvody.setup_form(gener_dict, ext_widgets = None)  #  формуємо форму вводу тільки з полями вводу, без всяких випад списків
              WorkwithWidgets.show_widgets(self.list_widgets)  # Виклик статич метод в класі WorkwithWidgets, який показує віджети
           else: 
                logger_db_conn.error(f"Не вдалося сформувати обєднаний словник стовпців")
                DialogWindow.form_dialog_wind("Помилка", f"Не вдалося сформувати обєднаний словник стовпців", QMessageBox.Icon.Warning)
                return []     
        else:    
            logger_db_conn.error(f"Не сформований словник для таблиці: {Table_main_product} або {self.table_name_depend}") 
            DialogWindow.form_dialog_wind("Помилка", f"Не сформований словник для таблиці: {Table_main_product} або {self.table_name_depend}", QMessageBox.Icon.Warning) 
            return [] 
    
    #   Цей метод є визначен в базовому класі, а тут ми вже його доповнюємо 
    def prepare_to_insert(self, list_users_data):
        list_korteg_stovpciv_bez_id = self.ekzemp_category.get_all_stovp_bez_identity_datetime(Table_main_product) # для головн таблиці отримуєм список стовпців, які підставляємо в INSERT
        list_stovp_bez_id_maintabl = ", ".join([f"[{item[0]}]" for item in list_korteg_stovpciv_bez_id])  # перетв з списку кортежів в список типу: [Category_catid], [Artukyl], [Nazva_tov], [Description], [Kilkist], [Price]
        list_korteg_all_stovp_depend_tabl = self.ekzemp_category.get_name_all_stovpciv_table(self.table_name_depend) # для залежн табл отримуємо список всіх стовпців
        list_all_stovp_depend_tabl = ", ".join([f"[{item[0]}]" for item in list_korteg_all_stovp_depend_tabl]) # перетв з списку кортежів в список типу: [memid], [mem_type], [capacity], [speed]
        kilk_stovp_main_tabl = len(list_korteg_stovpciv_bez_id)   #  Кількість стовпців головн таблиці які потрібно заповнити в запиті INSERT
        kilk_stovp_depend_tabl = len(list_korteg_all_stovp_depend_tabl)
        #list_users_data.insert(0, self.sub_cat_id)     # Додаємо id на першу позиц., щоб вставити в табл Products
        list_dani_main_tabl = list_users_data[:kilk_stovp_main_tabl]  # Зріс, тобто весь список ділимо на список для головн табл
        list_dani_depend_tabl = list_users_data[kilk_stovp_main_tabl:] # Зріс, тобто список для залежн табл
        placeholders_depend = "@LastInsId, " + ", ".join(["?"] * (kilk_stovp_depend_tabl - 1))
        params =  list_dani_main_tabl + list_dani_depend_tabl  # це значення які ввів користувач типу: ['AM5-GB-B477', 'Материнська плата Gigabyte B477', 'з потужною відеокартою', '18', '26', 'AM5', 'AMD D 7354', 'ATX', '3']
        # Нижче - виклик методу який вставл дані в бд з класу ZaputuProductDB
        result = self.ekzemp_product.insert_in_tables(self.table_name_depend, list_stovp_bez_id_maintabl, kilk_stovp_main_tabl, list_all_stovp_depend_tabl, placeholders_depend, [self.sub_cat_id] + params) 
        if result:  #  Якщо вставка даних в 2 таблиці пройшла успішно
             QMessageBox.information(self, "Успіх", "Дані успішно занесені в бд.")
             self.show_recent_date(params)  # метод який показує введенні дані користув в таблиці справа
        else:  #  Якщо дані не вставлені в бд   
             ex = self.ekzemp_product.error_zaputy  # звертаюсь до атрибута класу WorkDB, щоб отримати код поилки з exceptiona в методі execute_query_insert
             QMessageBox.critical(self, "Помилка", f" Помилка бд при виконанні запиту: {ex}") 
       
    def show_recent_date(self, users_data):  # Виводить дані які вводить корист щоразу у таблицю виводу
        list_ukr_namestovp = self._get_list_col_name(self.dict_stovp_main, self.dict_stovp_depend, 'key')  # беремо назви стовпців в обох словник і склад список укр назв стовпців
        if list_ukr_namestovp: # Якщо існує список укр стовп із 2-х табл типу: ['Артикул', 'Назва товару', 'Опис', 'Кількість', 'Ціна', 'Створено', "Роз'єм/Сокет", 'Чипсет', 'Форм-фактор', 'Кількість слотів']
            if not users_data:
                self.ekzemp_table.clear_table()   # Все строки, которые были в таблице, мгновенно удаляются
                DialogWindow.form_dialog_wind("Помилка", f"Не вдалося прочитати дані із таблиці: {self.table_name_depend}", QMessageBox.Icon.Warning)
                return  # Виходимо з функції, бо немає даних з бази немає подальшого сенсу                         
            self.ekzemp_table.set_headers(list_ukr_namestovp) # Встанов кількість стовпців і їх назви (шабку таблиці)
            self.ekzemp_table.fill_table(users_data, bagatovum=False)  #  Заповнення таблиці даними, False тому що простий список
            WorkwithWidgets.show_widgets(self.list_widgets)  # Виклик статич метод в класі WorkwithWidgets, який показує віджети
        else: 
            logger_db_conn.error(f"Не сформовано список українських назв стовпців")
            DialogWindow.form_dialog_wind("Помилка", f"Не сформовано список українських назв стовпців", QMessageBox.Icon.Warning)
            return [] 
  
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