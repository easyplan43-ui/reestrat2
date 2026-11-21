from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QComboBox, QLineEdit, QFrame, QHeaderView, QAbstractItemView,
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFormLayout, QRadioButton,
                             QPushButton, QDateEdit, QApplication, QMessageBox)
from PyQt6.QtCore import Qt
from check_functions import search_val_in_dict
from constants import *
from conn_to_db import ZaputuTypepoint, ZaputuSkladu, ZaputuAgentu, ZaputuCategoriesDB, ZaputuProductDB  # клас для підключення до бд
from dodat_classes import DialogWindow, TablManager, WorkwithWidgets, VupadSpusokManager, DictManager, CellDataManag, FormaVvody  #  звертаємося до статичних методів класів помічників, щоб не створ екземпляр класу
from registr_error import logger_db_conn   # регистрація помилок в файл
from style import STOCK_STYLE
# Тільки класи для реалізації підменю "Склад". Незабудь новий створюваний клас відмітити в файлі: string_to_class
class BasicZakyp(QMainWindow):       #      Універс. Батьківський клас для Складу / Контрагенту
    def __init__(self, table_type):  # сюда ми в дочір класах запихаємо назву таблиці яку нам потрібно: типи складів або типи агентів
        super().__init__()
        self.list_widgets = []
        self.cat_tag = None   #  Це тег взятий з табл: Categories, щоби знати яку вибирати табл: Memory_det, Processor_det, ....
        self.sub_cat_id = None    # цю змінну я буду викор в запиті SELECT WHERE sub_cat_id = Category_catid
        self.pered_func_stovp = None  # для передачі назви методу, який зверт до бд і витягає назви потрібних стовп для кожного доч класу різні
        self.dict_stovp_zalush = {} # Словник типу {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}, для таблиці Залишків
        self.dict_stovp_name = {}  # Словник типу {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}, для таблиці Цін
        QApplication.instance().setStyleSheet(STOCK_STYLE)   # Встановлюємо стиль із файлу стилів
        self.data_komirka = CellDataManag()   # створюєм екземпл по роботі із коміркою виводу і вибору дати накладної
        
        self.nomer_podat_nakl = QLineEdit()   # поле для вводу номера податкової накладної
        self.nomer_podat_nakl.setPlaceholderText("Введіть номер накладної")
        
        self.ekzemp_cat_prod = ZaputuCategoriesDB(Table_category)    # Створюємо екземпляр класу для роботи з категоріями товарів
        self.ekzemp_product = ZaputuProductDB(Table_main_product)    # Створюємо екземпляр класу для роботи з товарами  
        self.ekzemp_type_kontr = ZaputuTypepoint(table_type)         # Створ екземпляр класу для роботи з типами точок/контрагентів, передаючи назву таблиці
        self.ekzemp_vupad_spusok_catprod  = VupadSpusokManager(self.ekzemp_cat_prod.get_category_and_id, "Виберіть категорію товара") # Створ екземп класу по роботі з випад списками
        self.ekzemp_vupad_spusok_subcat   = VupadSpusokManager(self.ekzemp_cat_prod.get_subcategory_by_id, "Виберіть підкатегорію товара")  # не передаємо метод а наразі None передаємо, а дальше передамо назву потр методу 
        self.ekzemp_vupad_spusok_product  = VupadSpusokManager(self.ekzemp_product.get_product_short_detail, "Виберіть сам товар")
        self.ekzemp_forma_vvody           =  FormaVvody()   # поле вводу разом із кнопкою, але сигнал для кнопки є в класі FormaVvody
        self.ekzemp_table            = TablManager(sortyvatu = True)   # Створ екземп класу по роботі із таблицею відображення інфи на екрані
        
        self.central_widget = QWidget()  # Головний віджет
        self.setCentralWidget(self.central_widget)
        self.main_layout            = QVBoxLayout(self.central_widget) # Вертикальний розподіл: вгорі категорії, підкатегорії пошук, внизу - таблиця
        self.shapka_layout          = QHBoxLayout()        #  Створюємо Горизонт панель-шапка документа де розміщено вибір постачальн, складу, дата, ... 
        self.middle_layout          = QHBoxLayout()     # Найбільш центр макет: ділиться на ліву вводу і праву виводу
        self.left_inputmid_layout   = QVBoxLayout()     # Ліва центр панель вводу
        self.right_outputmid_layout = QVBoxLayout()     # Права центр панель виводу
        self.foot_layout            = QHBoxLayout()     # Нижня панель для кнопок
        self.foot_layout.addStretch() # пружина яка стягне все в цьому макеті --->

        self.main_layout.addLayout(self.shapka_layout)  # додаємо шапку до головного макету
        self.main_layout.addLayout(self.middle_layout)
        self.middle_layout.addLayout(self.left_inputmid_layout, 1)     # Додаємо ліву центр панель до Найбільш центр макет 
        self.middle_layout.addLayout(self.right_outputmid_layout, 2)   # Додаємо праву центр панель до Найбільш центр макет 
        self.main_layout.addLayout(self.foot_layout)  # додаємо нижній макет із кнопками до головного макету

    def _get_spusok_stovp_transl(self, tablename):  # //tested// для конкр таблиці дістає список стовпців, які треба перек на україн і вивести в таблицю на екран
            if tablename is None:
                list_kort= self.pered_func_stovp() # дочір класи перед різні назви методів, щоб витягнути різні стовпці із бд типу: [('Артикул', 'artukyl', 'varchar', 25), ('Назва товару', 'nazva_tov', 'nvarchar', 50),
            else:
                list_kort = self.pered_func_stovp(tablename) # дочір класи перед різні назви методів, щоб витягнути різні стовпці із бд [("Тип пам'яті", 'mem_type', 'varchar', 50), ("Обє'м Гб", 'capacity', 'int', 10),
            return DictManager.form_dictionary(list_kort)  # зверт до статичного методу, щоб отрим словник зі списку кортежів
            # повертаємо словник типу : {'Артикул': ('artukyl', 'varchar', 25), 'Назва товару': ('nazva_tov', 'nvarchar', 50), 'Опис': ('description', 'nvarchar', 200),    

class IncomeTovar(BasicZakyp):    #----------------  дочір клас Реалізує вкладку  - надходження товару ---------------------------- 
    def __init__(self):
        super().__init__(Table_typeagent)   # Виконати спочатку все що є в конструкторі базового класу, тобто запускаєм констр базового класу спочатку
        self._init_ui() # виклик початк методу з базового класу  дає дизайн і вигляд кнопок, випадаючих списків
                       
    def _init_ui(self):
        self.pered_func_stovp = self.ekzemp_product.get_neccess_stovpci_and_typejoin # передаю назву метода який витяг назви стовп із бд
        self.ekzemp_agent      = ZaputuAgentu(Table_agentu)        #  Створюємо екземпляр класу для роботи із агентами 
        self.ekzemp_type_sklad = ZaputuTypepoint(Table_typepoint)  #  Створ екземпляр по роботі із типами складів
        self.ekzemp_sklad      = ZaputuSkladu(Table_skladu)        #  Створюємо екземпляр класу для роботи із складами 
        self.ekzemp_type_price = ZaputuTypepoint(Table_typeprice)  #  Створ екземпляр по роботі із типами цін
        self.btn_cancel = QPushButton("Скасувати")
        self.btn_save   = QPushButton("Провести накладну")
        type_stovp = self.ekzemp_type_kontr.get_name_all_stovpciv_table() # дістаємо назви стовп таблиці, щоб  жорстко не прописувати їх в коді
        self.ekzemp_vupad_spusok_typekontr = VupadSpusokManager( # Створ екземп класу по роботі з типами контрагентів
                    lambda *args: self.ekzemp_type_kontr.get_type_points(  # де WHERE [{type_stovp[0][0]}] IN (2, 4) - це це необовязковий SQL додаток в методі get_type_points
                        type_stovp[0][0], type_stovp[1][0], filtr_kogo_pokaz=f"WHERE [{type_stovp[0][0]}] IN (2, 4)"  # тобто вибираємо тільки постачальників і перевізників у випад спис
                    ), "Виберіть тип агента")    # Створ екземп класу по роботі з випад списками
        self.ekzemp_vupad_spusok_agent     = VupadSpusokManager(self.ekzemp_agent.get_agent_short_details_by_categ, "Виберіть агента")    
        type_stovp2 = self.ekzemp_type_sklad.get_name_all_stovpciv_table() # дістаємо назви стовп таблиці, щоб  жорстко не прописувати їх в коді і передати їх через lambda
        self.ekzemp_vupad_spusok_typesklad = VupadSpusokManager(lambda *args: self.ekzemp_type_sklad.get_type_points(type_stovp2[0][0], type_stovp2[1][0]), "Виберіть тип точки") # Створ екземп класу по роботі з випад списками
        self.ekzemp_vupad_spusok_sklad = VupadSpusokManager(self.ekzemp_sklad.get_sklad_short_details_by_categ, "Виберіть склад") # Створ екземп класу по роботі з випад списками
        #type_stovp3 = self.ekzemp_type_price.get_name_all_stovpciv_table() # дістаємо назви стовп таблиці, щоб  жорстко не прописувати їх в коді 
        #self.ekzemp_vupad_spusok_typeprice = VupadSpusokManager( # Створ екземп класу по роботі з типами цін
        #            lambda *args: self.ekzemp_type_price.get_type_points( # де WHERE [{type_stovp[0][0]}] IN (2, 4) - це це необовязковий SQL додаток в методі get_type_points
        #                type_stovp3[0][0], type_stovp3[1][0], filtr_kogo_pokaz=f"WHERE [{type_stovp3[0][0]}] IN (2)"
        #            ),  "Виберіть тип ціни")

        self.shapka_layout.addWidget(self.data_komirka)                      # екземпляри класів/віджети додаємо до панелі пошуку інформації
        self.shapka_layout.addWidget(self.nomer_podat_nakl)
        self.shapka_layout.addWidget(self.ekzemp_vupad_spusok_typekontr)
        self.shapka_layout.addWidget(self.ekzemp_vupad_spusok_agent)
        self.shapka_layout.addWidget(self.ekzemp_vupad_spusok_typesklad)     
        self.shapka_layout.addWidget(self.ekzemp_vupad_spusok_sklad)

        self.left_inputmid_layout.addWidget(self.ekzemp_vupad_spusok_catprod)
        self.left_inputmid_layout.addWidget(self.ekzemp_vupad_spusok_subcat)
        #self.left_inputmid_layout.addWidget(self.ekzemp_vupad_spusok_product)
        #self.left_inputmid_layout.addWidget(self.ekzemp_vupad_spusok_typeprice)
        self.left_inputmid_layout.addWidget(self.ekzemp_forma_vvody)
        self.left_inputmid_layout.addStretch()

        self.right_outputmid_layout.addWidget(self.ekzemp_table)

        self.foot_layout.addWidget(self.btn_cancel)
        self.foot_layout.addWidget(self.btn_save)

        self.shapka_layout.addSpacing(20)  # Відступ між елементами в шапці
        self.shapka_layout.addStretch()  # Ця "пружина" штовхає все що є в цьому макеті вниз 
          # Початк список віджетів, що тут додаш, то вже не треба буде редагувати цей список протягом цілого класу 
        self.list_widgets = [self.ekzemp_vupad_spusok_typekontr,  # індекс [0]
                             self.ekzemp_vupad_spusok_agent,      # індекс [1]
                             self.ekzemp_vupad_spusok_typesklad,  # індекс [2]
                             self.ekzemp_vupad_spusok_sklad,      # індекс [3] 
                             self.ekzemp_vupad_spusok_catprod,    # індекс [4]
                             self.ekzemp_vupad_spusok_subcat,     # індекс [5] 
                             #self.ekzemp_vupad_spusok_product,    # індекс [6]
                             #self.ekzemp_vupad_spusok_typeprice,  # індекс [7] 
                             self.ekzemp_forma_vvody,             # індекс [6] 
                             self.ekzemp_table]                   # індекс [7] 
                                        
        WorkwithWidgets.hide_widgets(self.list_widgets[1:])  # Викликаємо служб статичн метод в класі WorkwithWidgets який приховує кнопки і поле Search і 
               
        #self.main_layout.addStretch()  # Ця "пружина" штовхає головний макет вгору
         # ---------------------------------------------------------- Сигнали ------------------------------------------------------------------ 
        # Коли юзер вибирає щось у випад списку то спрацьовує сигнал signal_select_val і передає вибране значення у ф-ю obrob_kaskad_vupad_spus
        self.ekzemp_vupad_spusok_typekontr.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 0, next_ind = 1))  
        self.ekzemp_vupad_spusok_agent.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 1, next_ind = 2))  
        self.ekzemp_vupad_spusok_typesklad.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 2, next_ind = 3)) 
        self.ekzemp_vupad_spusok_sklad.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 3, next_ind = 4))  
        self.ekzemp_vupad_spusok_catprod.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 4, next_ind = 5))  
        self.ekzemp_vupad_spusok_subcat.signal_select_val.connect(self.prepare_form_tabl_forma_vvody)
        #self.ekzemp_vupad_spusok_subcat.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 5, next_ind = 6))
        #self.ekzemp_vupad_spusok_product.signal_select_val.connect(lambda *args: self.obrob_kaskad_vupad_spus(curr_ind = 6, next_ind = 7)) 
        #self.ekzemp_vupad_spusok_typeprice.signal_select_val.connect(self.prepare_form_tabl_forma_vvody)
        self.ekzemp_forma_vvody.signal_dict.connect(self.get_userdata_from_form)  # тут спрац сигнал signal_dict і перед значен у ф-ю get_userdata_from_form
                
    def  obrob_kaskad_vupad_spus(self, curr_ind, next_ind):   #  каскадне одне за другим виклик і обробка тільки ВИПАДАЮЧ СПИСКІВ від 1-го до останього   
         curr_vupad_spus = self.list_widgets[curr_ind]
         next_vupad_spus = self.list_widgets[next_ind] 
         potoch_index = curr_vupad_spus.get_curr_index() # виводить індекс вибраного тексту в випад списку користувачем
         if potoch_index == -1: # Коли оператор клацнув на текст в випад списку і він став пустим і оператор наразі нічого не ввів
             return
         if potoch_index == 0:     # Якщо обрано дефолтний рядок "Виберіть ...", ховаємо наступний випад список
            WorkwithWidgets.hide_widgets(self.list_widgets[next_ind:]) # ховаємо наступний випад список
            return
         returned_val = curr_vupad_spus.get_curr_data()  # Якщо вибрано реальне значення, беремо його ID із бд
         if returned_val is not None:
             select_id = returned_val[0]   # Беремо перший елемент — це ID з бази даних, це не є поряд індекс в випад списку
             next_vupad_spus.add_items(select_id)    # Заповнюємо наступний список, передаючи туди цей ID 
             WorkwithWidgets.show_widgets([next_vupad_spus])  # Виклик статич метод в класі WorkwithWidgets, який показує віджети   
             self._find_cat_tag(curr_ind, returned_val)  # щоб для випад спис із категоріями товарів встановити self.cat_tag

    def _find_cat_tag(self, curr_ind, data):
         if curr_ind == 4: # якщо це випад список із категорією товарів, який має дати нам щей додатково cat_tag, наприклад cpu 
              if len(data) > 2: # якщо є дані типу [3, 'Процесори', 'cpu'] 
                  self.cat_tag = data[2] 

    def _zapovn_ekzemp_danumu(self, sub_cat_id): # Заповнює екземпляр даними із бд згідно вказаного id
         self.ekzemp_vupad_spusok_product.add_items(sub_cat_id)
         return self.ekzemp_vupad_spusok_product # повертає вже заповнений екземпляр даними із бд
           
    def prepare_form_tabl_forma_vvody(self): # підготовка формування таблиці виводу інфи або форми вводу, в залежності від дочірн класу
            index = self.ekzemp_vupad_spusok_subcat.get_curr_index() # вивод текуч індекс/номер вибраного елементу в вип_списку - 0,1,2,3,....
            if index == -1: # Коли оператор клацнув на текст в випад списку і він став пустим і оператор наразі нічого не ввів
                return
            if  index == 0:   # Якщо обрано "Оберіть підкатегорію..." (індекс 0), ховаємо форму ввода
                WorkwithWidgets.hide_widgets(self.list_widgets[6:]) # Виклик Зовн статич метод з класу WorkwithWidgets, щоб сховати віджети
                return True  # заверш роботу бо корист вибрав категорію позамовченю
            else:  # Якщо користув обрав якусь реальну не дефолтну категорію
                self.sub_cat_id = self.ekzemp_vupad_spusok_subcat.get_curr_data()[0]  # беремо id підкатегорії товару із бази
                
                # звертаємося до обох табл Prices і Zalushku щоб витягнути назви стовпців
                dict_temp_stov_nam = self._get_spusok_stovp_transl(Table_main_product) # дістаємо назви полів Імя_Продукту, Артикул
                # Беремо тільки Назву Товара із цілого словника назв стовпців
                for (i, (key, val)) in enumerate(dict_temp_stov_nam.items()): # дістаємо пару (ключ, значення) і прикріплюємо порядковий ном.
                     if i == 1:  # Якщо ми дійшли до словника із ключем - Назва_товару то
                         self.dict_stovp_name[key] = val  # записуємо в нього значення 
                         break
                self.dict_stovp_zalush = self._get_spusok_stovp_transl(Table_nakladdet) # дістаємо назви полів Кількість, Ціна
                if self.dict_stovp_name and self.dict_stovp_zalush: # Якщо є словники типу: {'Тип диска': {'type': 'varchar', 'size': 15}, "Обє'м Тб": {'type': 'int', 'size': 10}, 'Швидкість Мб/c': {'type': 'int', 'size': 10}}
                    gener_dict = DictManager.union_dicts(self.dict_stovp_name, self.dict_stovp_zalush)   # обєднуємо словники  в один з допом базового методу
                    if gener_dict:  # Якщо вдалося обєднати 2 словн в один: 
                        self.ekzemp_forma_vvody.setup_form(gener_dict, ext_widgets ={next(iter(self.dict_stovp_name)): self._zapovn_ekzemp_danumu(self.sub_cat_id)})  #  формуємо форму вводу тільки з полями вводу, без всяких випад списків
                        WorkwithWidgets.show_widgets(self.list_widgets)  # Виклик статич метод в класі WorkwithWidgets, який показує віджети
                    else: 
                        logger_db_conn.error(f"Не вдалося сформувати обєднаний словник стовпців")
                        DialogWindow.form_dialog_wind("Помилка", f"Не вдалося сформувати обєднаний словник стовпців", QMessageBox.Icon.Warning)
                        return []     
                else:    
                    logger_db_conn.error(f"Не сформований словник для таблиці: {Table_ostatku} або {Table_price}") 
                    DialogWindow.form_dialog_wind("Помилка", f"Не сформований словник для таблиці: {Table_ostatku} або {Table_price}", QMessageBox.Icon.Warning) 
                    return [] 

    def show_recent_date(self, users_data):  # Виводить дані які вводить корист щоразу у таблицю виводу на екран
            list_ukr_namestovp = DictManager.get_list_by_key(self.dict_stovp_name, self.dict_stovp_zalush, target = 'ukr')  # беремо назви стовпців в обох словниках і склад список укр назв стовпців
            if list_ukr_namestovp: # Якщо існує список укр стовп із 2-х табл типу: ['Артикул', 'Назва товару', 'Опис', 'Кількість', 'Ціна', 'Створено', "Роз'єм/Сокет", 'Чипсет', 'Форм-фактор', 'Кількість слотів']
                if not users_data: # Якщо немає 
                    self.ekzemp_table.clear_table()   # Все строки, которые были в таблице, мгновенно удаляются
                    DialogWindow.form_dialog_wind("Помилка", f"Не вдалося прочитати дані із таблиці: {Table_ostatku}", QMessageBox.Icon.Warning)
                    return  # Виходимо з функції, бо немає даних з бази немає подальшого сенсу                         
                self.ekzemp_table.set_headers(list_ukr_namestovp) # Встанов кількість стовпців і їх назви (шабку таблиці)
                #id_db = users_data[0][0]   # беремо id продукту із бд
                #name = users_data[0][1]    # беремо назву продукту із бд
                #rozpak_spus = [id_db] + [name] + users_data[1:] # робимо список із назви продукту і кількість і ціна
                self.ekzemp_table.fill_table(users_data, bagatovum=False)  #  Заповнення таблиці даними, False тому що простий список
                #ostan_radok = self.ekzemp_table.rowCount() - 1   #  дістаємо номер нового нижнього рядка
                #first_komir = self.ekzemp_table.item(ostan_radok, 0) # дістаємо клітинку де відображається назва товару
                #first_komir.setData(Qt.ItemDataRole.UserRole, id_db)
                WorkwithWidgets.show_widgets(self.list_widgets)  # Виклик статич метод в класі WorkwithWidgets, який показує віджети
            else: 
                logger_db_conn.error(f"Не сформовано список українських назв стовпців")
                DialogWindow.form_dialog_wind("Помилка", f"Не сформовано список українських назв стовпців", QMessageBox.Icon.Warning)
                return [] 
                  
    def get_userdata_from_form(self, data_user): #  метод викликается автомат, коли у формі вводу натискають 'Внести' і дані перевірені і він отрим дані з форми вводу
               # Цей метод є ПІДПИСАНИМ на сигнал signal_dict із класу FormaVvody
                list_user_val = DictManager.get_list_from_val_dict(data_user) # виклик статич метод що вертає список даних які ввів користувач типу ['val1', 'val2', val3]
                #self.prepare_to_insert(list_user_val)   # це передача  list_user_val через метод-заглушку peredacha_list на дочірній клас         
                self.show_recent_date(list_user_val)

             

       

