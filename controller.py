# changes 18:10 i made
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from constants import NAME_BUTTONS, SUBMENU_FILE
from registr_error import logger_configfile_conn
from dodat_classes import DialogWindow, FileManager
import os
import sys
from string_to_class import *   # типу конфіг файл де є відповідність між строкою і реальним іменем класу 
import json # для читання даних про назви кнопок submenu із json файла
class Controller():   # Класс-контроллер для управления логикой переключения. Он связывает сигналы кнопок с переключением страниц в QStackedWidget.
    def __init__(self, main_window):     # параметр main_window позволяет передать ссылку на главное окно 
        self.main_wind = main_window
        self.dict_name_btns_submenu = self.load_name_btns_from_json()   # виклик функцію по загрузці назв кнопок submenu із json файла 'submenu_buttons.json'
        self.setup_connections()

    def _get_config_path(self):               #  Приватний метод для отримання шляху до файлу submenu_buttons.json
        base_path = FileManager.return_path()   # зверт до декоратора класу FileManager, як до звич функції, щоб отримати шлях який залеж від способу запуску проги
        return os.path.join(base_path, SUBMENU_FILE)  # Вертає абсолютный путь к файлу конфигурации 'users_roles.yaml'   
     
    def setup_connections(self):         # Cвязывает нажатие кнопки в боковой панели с вызовом функции, которая отображает подменю.
        sidebar_buttons = self.main_wind.sidebar.dict_side_btn  # Отримуємо посилання на словник кнопок, які створені в бок панелі, силка веде через обєкт головн вікна на обєкт бок панелі
        for key, btn in sidebar_buttons.items():    # Автоматично підключаємо всі кнопки, крім кнопки Exit
            if key != "Exit":
                btn.clicked.connect(lambda checked, k = key: self.show_submenu(k)) # при нажаті на кнопку виклик ф-ю show_submenu і в неї передаємо назву кнопки: Stock
            if "Exit" in sidebar_buttons:
               sidebar_buttons["Exit"].clicked.connect(lambda: self.exit_program()) 
        self.main_wind.submenu.hide_left_btn.clicked.connect(lambda: self.main_wind.submenu.hide())     

    def show_submenu(self, category):  #category зараз дорівнює "Stock", "Sales" тощо.
       # Отримуємо українську назву з NAME_BUTTONS (для "Stock" це буде "Склад")
       # Другий елемент кортежу NAME_BUTTONS[category][1] — це саме текст "Склад"
       ukr_category_name = NAME_BUTTONS.get(category) # де  ukr_category_name типу: Склад, Звіти
       print(ukr_category_name)
       # Безпечно шукаємо дані в JSON-словнику за українською назвою
       submenu_data = self.dict_name_btns_submenu.get(ukr_category_name) # де submenu_data це всі дані для кожного словника
       # Відображаємо підменю, якщо воно знайдене
       if submenu_data is not None:
          self.main_wind.submenu.create_dynamic_submenu(submenu_data)
          self.main_wind.submenu.show()
       else:
          self.main_wind.submenu.hide()
        
    def exit_program(self):  # Закриваем прогу при нажатии на кнопку Вихід
        self.main_wind.close()

    def load_name_btns_from_json(self):   # вертає у вигляді словника прочитані дані з json файлу: SUBMENU_FILE а саме імена кнопок підменю
        conf_path = self._get_config_path() # зверт до внутр служб методу який вертає шлях виду c:\Users\nikolay.lavrov.VIDEOSERV\Documents\GitHub\reestrat2\submenu_buttons.json
        try:
            with open(conf_path, 'r', encoding='utf-8') as f:
                return  json.load(f) # Вертає прочитані дані із файлу submenu_buttons.json, які перетворені у словник або список - вміст всього файлу
        except FileNotFoundError:
           DialogWindow.form_dialog_wind("Помилка", f"Файл формування підменю: {SUBMENU_FILE} не знайдено за шляхом:\n{conf_path}", QMessageBox.Icon.Critical)
           logger_configfile_conn.error(f"Файл формування підменю: {SUBMENU_FILE} не знайдено за шляхом: {conf_path}")   # logger_main_conn з файлу ragistr_er
           sys.exit(1)    # закриваємо саму прогу
        except Exception as e:
           DialogWindow.form_dialog_wind("Помилка", f"Помилка у структурі файлу: {SUBMENU_FILE} формування підменю.", QMessageBox.Icon.Warning)
           logger_configfile_conn.error(f"Помилка у структурі файлу: {SUBMENU_FILE} формування підменю: {e}")   # logger_main_conn з файлу ragistr_error
           sys.exit(1)    # закриваємо саму прогу
    
  
   