# changes 18:10 i made
from PyQt6.QtWidgets import QLabel, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from constants import NAME_BUTTONS, SUBMENU_FILE
from registr_error import logger_configfile_conn
import os
import sys
from string_to_class import *   # типу конфіг файл де є відповідність між строкою і реальним іменем класу 
import json # для читання даних про назви кнопок submenu із json файла
class Controller():   # Класс-контроллер для управления логикой переключения. Он связывает сигналы кнопок с переключением страниц в QStackedWidget.
    def __init__(self, main_window):     # параметр main_window позволяет передать ссылку на главное окно 
        self.main_wind = main_window
        self.dict_name_btns_submenu = self.load_name_btns_from_json()   # виклик функцію по загрузці назв кнопок submenu із json файла 'submenu_buttons.json'
        self.setup_connections()
     
    def setup_connections(self):         # Cвязывает нажатие кнопки в боковой панели с вызовом функции, которая отображает подменю.
        self.main_wind.sidebar.btn_sales.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Sales"]))
        self.main_wind.sidebar.btn_purchases.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Purchases"]))
        self.main_wind.sidebar.btn_stock.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Stock"]))
        self.main_wind.sidebar.btn_person.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Person"]))
        self.main_wind.sidebar.btn_salary.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Salary"]))
        self.main_wind.sidebar.btn_reports.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Reports"]))
        self.main_wind.sidebar.btn_settings.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Settings"]))
        self.main_wind.sidebar.btn_admin.clicked.connect(lambda: self.show_submenu(NAME_BUTTONS["Admin"]))  
        self.main_wind.sidebar.btn_exit.clicked.connect(lambda: self.exit_program())   
        self.main_wind.submenu.hide_left_btn.clicked.connect(lambda: self.main_wind.submenu.hide())     

    def show_submenu(self, category):    #  Показує динамічне підменю
        self.category = category      # Зберігаємо в екземпляр класу
        self.main_wind.submenu.create_dynamic_submenu(self.dict_name_btns_submenu[category])   #  Виклик функцію створення динамічних підменю із 'submenu_buttons.json'
        self.main_wind.submenu.show()
        
        # При нажаті на кнопку під під-меню відкривається вкладка в головному вікні
        for btn in self.main_wind.submenu.sub_buttons:
            btn.clicked.connect(self.add_tab)   # Привязуємо нажаття на кнопку із функц добавлення нової вкладки в основ вікно

    def add_tab(self):              # Добавляє вкладки в основ робочу область, но предотвращает открытие нескольких одинаковых окон
        btn_text = self.main_wind.sender().text()     #  определяем текст кнопки submenu, на которую нажал пользователь, наприклад  - Особисті картки
        for i in range(self.main_wind.vkladku_in_mainwind.count()):         #  Пробегаем по всем уже открытым вкладкам
            if self.main_wind.vkladku_in_mainwind.tabText(i) == btn_text:   # Если вкладка с таким названием уже существует
                self.main_wind.vkladku_in_mainwind.setCurrentIndex(i)       # Программа просто переключается на неё (setCurrentIndex) и прекращает выполнение метода, чтобы не открывать копию
                return
        str_class_to_submenubtn = self.dict_name_btns_submenu[self.category].get(btn_text, QLabel)   #  Получаем нужный класс из словаря. Если его нет — берем заглушку (QLabel)
        real_class_to_submenubtn = Str_to_classname.get(str_class_to_submenubtn)   # Шукаємо реальний клас у нашому словнику з файлу string_to_class
        #  print(real_class_to_submenubtn)  -  <class 'submenu_classes.ZalushTovary'> ,  <class 'submenu_classes.Peremichena'>
        if real_class_to_submenubtn == QLabel:                     #  Если такой вкладки нет
            new_tab = QLabel(f"Контент для {btn_text}")       #  создается новый виджет метка QLabel
            new_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)    #  Встановлюємо вирівнювання вмісту всередині віджета new_tab по центру
        else:
            new_tab = real_class_to_submenubtn() # Создаем экземпляр класу class_to_submenubtn, тобто відкриваємо вкладку
        self.main_wind.vkladku_in_mainwind.addTab(new_tab, btn_text)   # Додає віджет new_tab як нову вкладку до контейнера. Текст на самому «ярлику» вкладки буде взято зі змінної btn_text
        self.main_wind.vkladku_in_mainwind.setCurrentWidget(new_tab)  # Робить цю нову вкладку активною, щоб користувач відразу побачив її вміст після створення

    def exit_program(self):  # Закриваем прогу при нажатии на кнопку Вихід
        self.main_wind.close()

    def load_name_btns_from_json(self):   # вертає у вигляді словника прочитані дані з json файлу а саме імена кнопок підменю
        if getattr(sys, 'frozen', False):   # запущена программа как обычный скрипт или как замороженный исполняемый файл (собранный через PyInstaller,
            base_path = os.path.dirname(sys.executable)     # Если программа скомпилирована
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))   # Если запуск из исходного кода де __file__: переменная, содержащая путь к текущему файлу
        config_path = os.path.join(base_path, SUBMENU_FILE)   # Створюєм абсолютный путь к файлу конфигурации 'users_roles.yaml' 
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f) # Вертає прочитані дані із файлу, які перетворені у словник або список
        except FileNotFoundError:
           msg = QMessageBox()
           msg.setIcon(QMessageBox.Icon.Critical)
           msg.setWindowTitle("Помилка")
           msg.setText(f"Файл формування підменю не знайдено за шляхом:\n{config_path}")
           msg.exec()
           logger_configfile_conn.error(f"Файл формування підменю не знайдено за шляхом: {config_path}")   # logger_main_conn з файлу ragistr_er
           sys.exit(1)    # закриваємо саму прогу
        except Exception as e:
           msg = QMessageBox()
           msg.setIcon(QMessageBox.Icon.Warning)
           msg.setWindowTitle("Помилка JSON")
           msg.setText(f"Помилка у структурі файлу формування підменю: {e}")
           msg.exec()
           logger_configfile_conn.error(f"Помилка у структурі файлу формування підменю: {e}")   # logger_main_conn з файлу ragistr_error
           sys.exit(1)    # закриваємо саму прогу
       
    def save_name_btns_in_json(self):    # Динамічно зберігаємо/оновлюємо назви кнопок submenu через інтерфейс самої програми і зберіг ці зміни в json файлі
        if getattr(sys, 'frozen', False):   # запущена программа как обычный скрипт или как замороженный исполняемый файл (собранный через PyInstaller,
            base_path = os.path.dirname(sys.executable)     # Если программа скомпилирована
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))   # Если запуск из исходного кода де __file__: переменная, содержащая путь к текущему файлу
        config_path = os.path.join(base_path, SUBMENU_FILE)   # Створюєм абсолютный путь к файлу конфигурации 'users_roles.yaml' 
        try:
           with open(config_path, 'w', encoding='utf-8') as f:
             # indent=4 робить файл "красивим" для читання людиною
             json.dump(self.dict_name_btns_submenu, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
           msg = QMessageBox()
           msg.setIcon(QMessageBox.Icon.Critical)
           msg.setWindowTitle("Помилка")
           msg.setText(f"Файл формування підменю не знайдено за шляхом:\n{config_path}")
           msg.exec()
           logger_configfile_conn.error(f"Файл формування підменю не знайдено за шляхом: {config_path}")   # logger_main_conn з файлу ragistr_erro
           sys.exit(1)    # закриваємо саму прогу
        except Exception as e:
           msg = QMessageBox()
           msg.setIcon(QMessageBox.Icon.Warning)
           msg.setWindowTitle("Помилка JSON")
           msg.setText(f"Помилка у структурі файлу формування підменю: {e}")
           msg.exec()
           logger_configfile_conn.error(f"Помилка у структурі файлу формування підменю: {e}")   # logger_main_conn з файлу ragistr_erro
           sys.exit(1)    # закриваємо саму прогу
    
    def edit_navigation_item(self, category, index, new_value):  # змінює назви кнопок submenu через інтерфейс проги а саме кнопку Администратору
       # category: ключ (наприклад, 'Sales'),  index: порядковий номер елемента в списку, new_value: нова назва пункту
       if category in self.dict_name_btns_submenu:
          self.dict_name_btns_submenu[category][index] = new_value
          self.save_name_btns_in_json()      # Записує зміни стосовно submenu кнопок у JSON-файл
          #self.main.refresh_ui() # Метод у MainWindow для оновлення тексту кнопок

    def open_edit_dialog(self, category, index):  # Відкриває діалогове вікно для зміни назви підменю
       # Отримуємо поточний текст за ключем та індексом
       current_text = self.dict_name_btns_submenu[category][index]
       #print(self.name_btns_submenu[category][index])
       # Відкриваємо вікно введення
       text, ok = QInputDialog.getText(self.main, 'Редагування', f'Змінити "{current_text}" на:', text=current_text)
       # Якщо натиснуто OK і текст не порожній
       if ok and text.strip():
          self.edit_navigation_item(category, index, text.strip())