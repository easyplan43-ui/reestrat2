from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox, QWidget, QHBoxLayout, QComboBox, QTableWidget, QFormLayout, QLineEdit, QPushButton, QScrollArea
from PyQt6.QtWidgets import QVBoxLayout, QCheckBox
from PyQt6.QtCore import Qt, QDate, QRegularExpression, pyqtSignal # для спілкування обєктів між собою для сигналів і випад списків
from PyQt6.QtGui import QRegularExpressionValidator
from decimal import Decimal
import datetime
import sys
import os
from constants import SUBMENU_FILE

class FormaVvody(QWidget):  # клас по роботі з полем вводу і кнопкою "Внести" що залеж від нього
    data_submitted = pyqtSignal(dict)  #  Створюємо сигнал для надсилання словника від корист на ззовні, бо цей сигн працює тільки з даними типу dict
    def __init__(self): 
        super().__init__()
        self.layout = QVBoxLayout(self)           # головн layout для самого класу
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.prokrytka = QScrollArea()            # Створюємо область прокрутки
        self.prokrytka.setWidgetResizable(True)   # Щоб форма розтягувалася по ширині
        self.forma_vvody = QWidget()
        self.text_forma_vvody = QFormLayout(self.forma_vvody)  #  створюємо сітку для зручного розміщення елементів у форматі «label — input_field
        self.prokrytka.setWidget(self.forma_vvody)
        self.layout.addWidget(self.prokrytka)
        self.dict_input = {}  # Словник для доступу до полів вводу за назвою
         
    def setup_form(self, diction, ext_widgets = None):  # очищаємо старі назви полів вводу і динамічно будуємо нові назви полів вводу 
        # але якщо заданий в ext_widgets якийсь зовніш віджет, наприк випад список то виводимо його
        if ext_widgets is None:  # ext_widgets: словник виду {"Назва поля": об'єкт_віджета}
            ext_widgets = {}
       
        while self.text_forma_vvody.count():  # Очищаємо форму поки є елементи, якщо там вже щось було (про всяк випадок)
            item = self.text_forma_vvody.takeAt(0)      # Видаляє посилання на перший елемент (з індексом 0) з нашого органайзера text_forma_vvody
            widget = item.widget()  # дивимось в середину шуфляди, і дістаємо віджет(кнопка, вип список) який леж в серед цієї  шуфляди 
            if widget:           # якщо в серед  шуфляди лежить якийсь віджет 
                if widget in ext_widgets.values():   # Якщо цей віджет є серед зовнішніх
                    widget.setParent(None)   # ми його просто відключаємо від форми, але НЕ видаляємо з пам'яті , бо він нам ще знадобиться!
                else:   # Якщо цей віджет не є серед зовнішніх то: 
                    widget.deleteLater()   #   безпечно видаляє віджет із пам'яті, щоб він не залиш при переключені між
        
        self.dict_input = {}
        for key, inner_dict in diction.items():    #   inner_dict — це внутрішній словник {'type': 'varchar', 'size': 25}
            if key in ext_widgets:   # логіка для наприклад випад списку чи прапорця
                pole_vvody = ext_widgets[key]  # де pole_vvody типу: <dodat_classes.VupadSpusokManager object at 0x000002393BDDCE10> 
            else:    # Стандартна логіка для QLineEdit    
                datatype = inner_dict.get('type')      # Безпечно дістаємо тип та розмір (якщо size немає, поверне None)
                size = inner_dict.get('size')
                pidkazka = self.create_pidkazku_placehold(datatype, size)
                pole_vvody = QLineEdit()                     # Створюємо поле вводу
                pole_vvody.setPlaceholderText(pidkazka)      # Встановлюємо створену підказку всередину поля!
                InputValidator.check_entered_data(pole_vvody, datatype, size)   # Виклик клас (декоратор методу) для накладання обмежень при вводі даних користув в форму вводу
            
            if isinstance(pole_vvody, CheckBoxManager):  # Якщо це прапорець
                self.text_forma_vvody.addRow("", pole_vvody)    # додаємо його в макет БЕЗ лівого підпису (передаємо порожній рядок "")
            else:      # Для всіх інших віджетів (наприклад, QLineEdit) залишаємо стандартний підпис із двокрапкою                 
                self.text_forma_vvody.addRow(f"{key}:", pole_vvody)
            self.dict_input[key] = pole_vvody  # зберіг кожне поле у словнику щоб не втратити доступ до поля, це словник з ключем - назва поля  а значен - сам віджет QLineEdit
                   
        self.btn = QPushButton("Внести")
        self.btn.clicked.connect(self.obrobka_press_btn) # ------------------------------ СИГНАЛ --------------------------------------------
        self.text_forma_vvody.addRow("", self.btn)  # добавляємо невелику кнопку  у сітку форми QFormLayout, де "" - робить кнопку невеликою
       
    def obrobka_press_btn(self):    #  Цей метод викликається кнопкою, отримує дані та пускає їх далі
        users_data = self.receive_users_data_check_empty() # отримує дані які ввів користув після перевірки
        if users_data is None:   # напр, коли корист не ввів всі поля
            return    # зупиняємо роботу
        # ЯКЩО ДАНІ ОК — ПРАЦЮЄМО З НИМИ ТУТ
        self.data_submitted.emit(users_data)   # активуємо наш сигнал і передаємо словник users_data усім хто на нього підписався
        
        # Очищаємо поля вводу 
        for name, field in self.dict_input.items():
           if isinstance(field, VupadSpusokManager):
              field.vupad_spusok.setCurrentIndex(0) # Скидаємо випадаючий список на найперший елемент (зазвичай це індекс 0)
           elif isinstance(field, CheckBoxManager): 
               field.setChecked(True)                 #  Скидаємо прапорець в True 
           else:
              field.clear()     # Для звичайних полів QLineEdit просто очищаємо текст
               
    def receive_users_data_check_empty(self):   # Отримує користувацькі дані з форми вводу, перевіряє на пусті поля,
        list_empty_fields = []
        valid_dict = {}
        for name, field in self.dict_input.items(): # отрим дані від корист та фіксуємо пусті поля: де name = Назва точки, field = <PyQt6.QtWidgets.QLineEdit object at 0x000001C5B61477F0>  
            if isinstance(field, VupadSpusokManager): # якщо field належить до класу VupadSpusokManager
                text_val = field.get_curr_data()  # виклик метод класу VupadSpusokManager який повертає вибране корист значення в випад списку 
                if isinstance(text_val, list) and text_val:   # Якщо text_val є списком і він не пустий, беремо перший елемент
                    text_val = text_val[0]   # зі списку ['val'] беремо тільки 'val'
                if text_val is None:   # text_val типу 'Склад готової продукції'
                    text_val = ""   # Приводимо до порожнього рядка для уніфікації
            elif isinstance(field, CheckBoxManager): # якщо field належить до класу CheckBoxManager, це клас по роботі із прапорцями
                # Для чекбокса пустих значень не буває (він або True, або False)
                valid_dict[name] = field.get_value()  # зверт до методу класу CheckBoxManager щоб дізнатися стан прапорця True/False
                continue      # Одразу переходимо до наступного віджета, пропускаючи перевірку на порожнечу
            else:     
                text_val = field.text().strip()     # Звичайне поле QLineEdit
            
            if not text_val:   # Перевірка на порожнечу для текстових полів та випад списків
                list_empty_fields.append(name)  # де empty_fields = ['Опис', "Тип пам'яті"] - це назви тих полів які корист не заповнив
            else:    
                valid_dict[name] = text_val   # де text_val - це те значення, що корист ввів в поле вводу  
        
        if list_empty_fields:   # якщо є пості поля що незаповнив користувач
            QMessageBox.warning(self, "Попередження", "Всі поля мають бути заповнені!") 
            return None
        else:  # якщо немає пустих полів
            return valid_dict  #  повертає словн типу  {'Назва точки': 'tocka4', 'Тип точки': ['Роздрібний магазин'], 'Місто': 'Kahar', 'Адреса': 'shemelovska 4', 'Активний?': True}
            

    def create_pidkazku_placehold(self, datatype, size):  # Створює підказки для Placeholderiv, тобто в середині поля вводу
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

class DialogWindow:   #  Клас-помічник формує діалогове вікно про помилку, увагу, повідомлення
    # щоб скористатися пиши в коді: DialogWindow.form_dialog_wind("Помилка", f"Файл формування підменю: {SUBMENU_FILE} не знайдено за шляхом:\n{conf_path}", QMessageBox.Icon.Critical)
    @staticmethod   # декоратор, що перетв метод в звичайну функцію
    def form_dialog_wind(title_text, tilo_text, icon_type): # Формує діалогове вікно виводу помилок, повідомлень
        msg = QMessageBox()   #  Створ обєкт спец класу для виводу діалог вікна
        msg.setWindowTitle(title_text)
        msg.setText(tilo_text)
        msg.setIcon(icon_type)   # Тип іконки: чи помилка чи Увага
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()   # Показуємо вікно

class WorkwithWidgets: # Клас помічник по роботі з кнопками, випадаючими списками, полями пошуку
    @staticmethod  # декоратор, що перетв метод в звичайну функцію
    def hide_widgets(list_widgets):  #  Ховає всі віджети, передані у списку list_widgets
        for widget in list_widgets:
            if widget is not None:  # щоб програма не "впала", якщо якийсь віджет ще не встиг ініціалізуватися
               widget.hide()

    @staticmethod  # декоратор, що перетв метод в звичайну функцію    
    def show_widgets(list_widgets):  #  Показує всі віджети, передані у списку list_widgets   
        for widget in list_widgets:
            if widget is not None:  # щоб програма не "впала", якщо якийсь віджет ще не встиг ініціалізуватися
               widget.show()   
   
class FileManager:
    @staticmethod  # декоратор, що перетв метод в звичайну функцію, яка просто бере вхідні дані та видає результат
    def return_path(): # Метод - вірт зміна вертає шлях в залеж від запуску проги, використовую суто для auto-py-to-exe при складані проекту
        if getattr(sys, 'frozen', False):   # запущена программа как обычный скрипт или как замороженный исполняемый файл (собранный через PyInstaller,
            return os.path.dirname(sys.executable)     # Це коли використано - auto-py-to-exe, бо він додає прапорець 'frozen' 
        else:
            return os.path.dirname(os.path.abspath(__file__))   # Це коли простий запуск Run або python main.py
   
class InputValidator:  # Клас-помічник, використ його у момент динамічного створення віджету,  QLineEdit() - поля вводу
    @staticmethod   #  Декоратор, дозволяє викликати метод без створення екземпляра класу (просто InputValidator.check_entered_data(...))
    def check_entered_data(widget, datatype, size):   # це звичайна функція, яку просто «сховали» всередину класу для кращої організації коду.
        pattern = ""  
        
        if datatype.upper() in ["INT", "INTEGER"]:   #  Переход в верхній регістр 
            pattern = rf"^\d{{0,{size}}}$"    # Тільки цифри, довжина від 0 до size
            
        elif datatype.upper() in ["DECIMAL", "NUMERIC"]:    # Цифри з однією крапкою, довжина до size
            # Примітка: спрощений паттерн, можна уточнити під (10,2)
            pattern = rf"^\d{{0,{size}}}(\.\d{{0,2}})?$"
            
        elif "NVARCHAR" in datatype.upper():
            # \w — букви та цифри, \s — пробіли. Спецсимволи (напр. @, #, $) заборонені.
            pattern = rf"^[a-zA-Zа-яА-ЯіІїЇєЄґҐ0-9\s.,\-]{{0,{size}}}$"

        elif "VARCHAR" in datatype.upper():
            # \w — букви та цифри, \s — пробіли. Спецсимволи (напр. @, #, $) заборонені.
            pattern = rf"^[a-zA-Z0-9\s\-]{{0,{size}}}$"    

        if pattern:   #   Якщо тип даних розпізнано і патерн сформовано:
            regex = QRegularExpression(pattern)   #   Створює об'єкт регулярного виразу Qt на основі обраного рядка.
            validator = QRegularExpressionValidator(regex, widget)   #  Створює сам об'єкт-валідатор, який буде фільтрувати введення «на льоту»
            widget.setValidator(validator)   #  Прив’язує валідатор до віджета, після чого користувач просто не зможе натиснути клавішу, яка порушує правило. 

class VupadSpusokManager(QWidget): # Створює наповнює випад списки
    changed = pyqtSignal(object) 
    def __init__(self, peredana_func, default_item, parent=None):
        super().__init__(parent) 
        self.peredana_func = peredana_func      # Зберігаємо посилання на функцію
        self.default_item = default_item 
        self.layout = QHBoxLayout(self)
        self.vupad_spusok = QComboBox()
        self.layout.addWidget(self.vupad_spusok)
        self.add_items()
        # Як тільки юзер клацне на інший рядок в вип_списку, негайно виконуй код у _handle_change
        self.vupad_spusok.currentIndexChanged.connect(self._handle_change)   # Підключаємо сигнал ПІСЛЯ першого заповнення

    def _handle_change(self):  # внутрішній «обробник», який спрацьовує, коли ти вибираєш новий пункт у випадаючому списку
        data = self.vupad_spusok.currentData()  # data типу: [3, 'Процесори', 'cpu'] або [5, 'AMD Ryzen']
        self.changed.emit(data) # Сигнал emit передає дані в той  метод який підключ до сигналу changed десь в зовн коді

    def add_items(self, *args):   # ПОЛІМОРФІЗМ працює як із статичними даними в памяті так і з SQL, добавл до випад списку дефолтний і нові значення
        self.vupad_spusok.blockSignals(True)  # виключ сигнал currentIndexChanged, щоб при clear або заповн не запускати інші функц які реагують
        self.vupad_spusok.clear()   # очистка перед завантаженням нових зн
        self.vupad_spusok.addItem(self.default_item, None)   
        if not args and self.peredana_func.__code__.co_argcount > 1:  #  і функція (peredana_func) очікує їх (більше ніж один обов'язковий self
           self.vupad_spusok.blockSignals(False)                      #  то виходим з методу не заповняючи вип список
           return
        try:
           data_list = self.peredana_func(*args)  # динам виклик функц посилання на яку збереж у peredana_func
           if data_list: # список кортежів [(7, 'Брокер'), (1, 'Клієнт'), (5, 'Комітент'), (4, 'Перевізник'),...
             for item in data_list:
                try:
                    if len(item) > 1:         # Оскільки pyodbc.Row веде себе як список, просто перевіряємо довжину
                        name = str(item[1])   # Якщо елементів більше 1, беремо саме другий (індекс 1):  'Брокер', 'Клієнт'
                    else:
                        name = str(item[0])
                except:
                    name = str(item)   # Якщо item не є списком або сталася інша помилка, просто перетворюємо весь об'єкт на рядок.
                self.vupad_spusok.addItem(name, list(item)) # name — те, що бачить користувач, list(item) — приховані дані (весь рядок БД),
        finally:
            self.vupad_spusok.blockSignals(False)  # знову вмикаємо сигнали віджета, щоб він знову став "живим" для користувача

    def get_curr_data(self): # вертає список типу: [11, 'HDD'], тобто те шо користув сам обрав в вип_списку і id саме із бази
        result = self.vupad_spusok.currentData()
        return result  

    def get_curr_string(self): # Повертає звичайний рядок
        return self.vupad_spusok.currentText()

    def get_curr_index(self): # вертає індекс/пор номер вибраного елемента в випад списку: 0,1,2,3,...
        return self.vupad_spusok.currentIndex()
        
class TablManager(QTableWidget):  # Клас по роботі із таблицями, її шабками, заповнення даними із бд, вкл/викл сортуванння по стовпцях     
    def __init__(self, sortyvatu = False):   
        self.sortyvatu = sortyvatu    # де sortyvatu - це флажок який каже чи таблицю можна сортувати чи ні 
        super().__init__() # виклик конструкт батьківського класу із методу __init__ дочір класу, бо хочу доповнити функціонал батька тут у нащад
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setSortingEnabled(self.sortyvatu)
            
             # Цей метод викликається з методу fill_table, а не ззовні
    def create_komirka(self, value):  # метод по створені та форматуванні комірки для таблиці відображення даних на екрані
       komirka = QTableWidgetItem()  #  Створ порожню (елемент) комірку для таблиці
       komirka.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # заборон редагування, дозволяємо лише: активність (Enabled) та виділення (Selectable) 
       if isinstance(value, (int, float, Decimal)):        # чи є значення числом 
           dec_val = float(value) if isinstance(value, Decimal) else value  # Перетвор Decimal в Float
           komirka.setData(Qt.ItemDataRole.EditRole, dec_val)  #  записуємо дані "всередину" комірки так, щоб таблиця розуміла їхній справжній тип (число, дата тощо), а не просто бачила в них набір символів
       elif isinstance(value, (datetime.date, datetime.datetime)):       # чи є значення датою 
           date = QDate(value.year, value.month, value.day)   # створюємо об'єкт дати у форматі, який «розуміє» бібліотека
           komirka.setData(Qt.ItemDataRole.EditRole, date)  
       else:    # Якщо в базі щось є (is not None) — перетвори це на текст. А якщо там порожньо — покажи просто порожній рядок
           komirka.setData(Qt.ItemDataRole.EditRole, str(value) if value is not None else "") 
       return komirka 
    
    def fill_table(self, rows, bagatovum =  True):   # Заповнює таблицю відобр даних, rows може бути як простим списком так і списком кортежів/списків
        self.setSortingEnabled(False)   # Вимикаємо сортування на час заповнення, щоб програма не "гальмувала"
        if bagatovum: # Коли на вх поступ список кортежів/списків, тобто [(),(),()] або [[],[],[]]
           self.setRowCount(len(rows))     # Твердо встановлюємо количество строк
           for row_index, row_data in enumerate(rows): #   0 ('SAS-SG-360', 'Диск SAS Seagate 360 ', '2 SFF', 5, Decimal('87.00'), datetime.datetime(2026, 3, 31, 17, 16, 17, 570000), 'SAS-2', 360, 6000) 1 () 2 (),....
              for col_index, value in enumerate(row_data): #  0 NVME-WD-720  1 Диск NVME Western Digital 720  2 PCIe 40  3 11  4 231.00 5 2026-03-31 04:43:06.980000
                 komirka = self.create_komirka(value)   #  Використовуємо метод для створення об'єкта комірки для таблиці
                 self.setItem(row_index, col_index, komirka) # Розміщуємо створений об'єкт комірки у конкретну клітинку таблиці
        else:         # Коли на вх поступає одновимір список, тобто [, , , , ] 
           start_row = self.rowCount()         # Дізнаємося поточну кількість рядків яка вже є в таблиці бд, а під час першого виклику буде = 0
           self.setRowCount(start_row + 1)     # Додаємо рівно одне порожнє місце внизу
           for col_index, value in enumerate(rows): # де col_index = 0,1,2,3,.. value - значення яке ввів корист
               komirka = self.create_komirka(value)
               self.setItem(start_row, col_index, komirka)
        if self.sortyvatu:
           self.setSortingEnabled(True) 
        
    def set_headers(self, stovpci):    # Налаштовує колонки та їх назви - шабка таблиці 
        self.setColumnCount(len(stovpci))   # Встановлюємо кількість колонок
        self.setHorizontalHeaderLabels(stovpci) # зверт до обєкту таблиці і встановл назви стовпців
        stovpci = self.horizontalHeader() # звертаємось до верхнього рядка (заголовка) в таблиці з назвами стовпців
        stovpci.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        stovpci.setMinimumSectionSize(100) # наприклад, 100 пікселів      

    def clear_table(self):     # Робить повне очищення таблиці 
        self.setRowCount(0)

class DictManager:   # Клас-помічник по роботі із
    @staticmethod  # він статич бо не корист ніякими методами і атрибутами класу     //tested//
    def form_dictionary(list_kortegiv): # Універ метод, перетвор список кортежів різної кількості елем в словник
        table_dict = {} 
        for row in list_kortegiv:
            if len(row) == 4: # для випадку: [('Артикул', 'Artukyl', 'varchar', 25), ('Назва_тов', 'Nazva_tov', 'nvarchar', 50), ('Description', '
                ukr_name, name, tup, size = row  # розпаковка кортежу
                table_dict[ukr_name] = {"name": name, "type": tup, "size": size}  # table_dict[ukr_name] = {'name': 'artukyl', 'type': 'varchar', 'size': 25}
            elif len(row) == 3:   # для випадку: [('Artukyl', 'varchar', 25), ('Nazva_tov', 'nvarchar', 50), ('Description', 'nvarchar', 200), ('Kilkist', 'int', 10), ('Price', 'decimal', 5)]
               name, tup, size = row     # розпаковка кортежу
               table_dict[name] = {"type": tup, "size": size}
            elif len(row) == 2:  # для випадку: [('key', 'value'), ('key', 'value'),...] 
               key, value = row     # розпаковка кортежу
               table_dict[key] = value   
            elif len(row) == 1:  # на виході дасть {'Artukyl': '', 'Nazva_tov': '', 'Description': '',
               key = row[0]   
               table_dict[key] = ""   # порожній рядок
            else:    # На випадок, якщо прилетить кортеж іншої довжини напр:  [('Artukyl', 'varchar', 25, 'NOT NULL', 'DEFAULT')] - 5 елементів  
               table_dict[row[0]] = row[1:] # якщо прил таке із 5 елем то буде таке: table_dict['Artukyl'] = ('varchar', 25, 'NOT NULL', 'DEFAULT'))
        return  table_dict  
    
    @staticmethod   
    def union_dicts(diction1, diction2):    # Обєднує два словники в один
            return diction1 | diction2 
    
    @staticmethod    
    def get_list_from_val_dict(data_dict):  # отрим словник типу {key:value, key2:value2} збирає в ньому всі value/value2,.. і створ зних список [value1, value2, ...]
        list_val = []
        for value in data_dict.values(): # values() - дай мені самі дані зі словника типу {key:value, key2:value2}
            list_val.append(value) 
        return  list_val   # повертає словник [value1, value2, ...]
    
    @staticmethod
    #  ось так вигляд виклик: DictManager.get_list_by_key(self.dict_tabl, None, target = 'ukr') - якщо немає другого словника
    def get_list_by_key(dict_main, dict_dep, target): # служб унів метод на вхід прймає 1/2 словники типу  {'Артикул': {'type': 'varchar', 'size': 25}, 'Назва товару': {'type': 'nvarchar', 'size': 50},
        # якщо два то обєднує іх в один словн, потім витягує із обєдн/одинар словника значення які я вказую в парам target і всі ці значення складає в новий список 
       if dict_dep is None:   # Якщо другий словник не передали, робимо його порожнім словником
           dict_dep = {}
       if target == 'key' or target == 'ukr':    # Якщо потрібні ключі (українські назви)
           return list(dict_main) + list(dict_dep) 
       elif target == 0 or target == 'eng':  #  - 0 (або 'eng')   -> збирає 0-й елемент кортежу (наприклад, 'artukyl')
           return [val[0] for val in dict_main.values()] + [val[0] for val in dict_dep.values()]
       elif target == 1 or target == 'type':   #  - 1 (або 'type')  -> збирає 1-й елемент кортежу (наприклад, 'varchar') 
           return [val[1] for val in dict_main.values()] + [val[1] for val in dict_dep.values()]
       elif target ==2 or target == 'size':    #  - 2 (або 'size')  -> збирає 2-й елемент кортежу (наприклад, 25)
           return [val[2] for val in dict_main.values()] + [val[2] for val in dict_dep.values()]
       else: 
           return []  
       
    @staticmethod
    # Для укр_назви_стовпця видати - анл_назву стовпця, де param - це укр_назва_стовпця
    def get_eng_name_stov(diction, param):  # поверт name із словн типу {'назва_стовп':{'name':'eng_name', 'type': ' ', 'size': ' '}, де param == key 
        search_param = str(param).strip().lower()    # Приводим входящий параметр к нижнему регистру и убираем лишние пробелы
        for key, eng_name in diction.items():  # Проходим по словарю метаданных
            if search_param == str(key).strip().lower():  # якщо укр_назва_стовпця == назві key із словника
                return eng_name['name']  # повертає анг_назву_стовпця
        return  None   # Если ничего не нашли   

class CheckBoxManager(QCheckBox): # Клас реалізує прапорець
    def __init__(self, text="", checked_default = True, parent = None):   # text ="" відобраз праворуч від квадратика прапорця
        super().__init__(text, parent) # беремо оригін конструктор QCheckBox і запускаємо його, передавши йому text та parent
        self.setChecked(checked_default)  # Налаштовуємо початковий стан (за замовчуванням увімкнений)
        self.setStyleSheet("font-size: 12px;") 
    
    def get_value(self):   #  Повертає стан прапорця  True/False
        return self.isChecked() 
   



