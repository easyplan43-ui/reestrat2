# changes 18:10 i made
from PyQt6.QtWidgets import QMessageBox
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
        # де self.dict_name_btns_submenu[category] = {'Залишки товарів': 'ZalushTovary', 'Переміщення': 'Peremichena', 'Інвентаризація': 'Inventariz', 'Списання': 'Spusanja', 'Оприбуткування': 'Oprubytkyv', 'Внесення товару': 'InsertTovar'}
        self.main_wind.submenu.show()  # Показуємо віджет на екрані
        
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
    
  
   