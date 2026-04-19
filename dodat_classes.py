from PyQt6.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, QDate, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from decimal import Decimal
import datetime

class TableManager:   #  Клас-помічник, створює таблицю відображення даних на екрані
    @staticmethod  # статич метод який нічого не міняє всередині класу TableManager, він просто бере вхідні дані та видає результат
    def fill_table(table, rows):   # Головн Статичн метод Оркестратор - по створеню і заповненю таблиці відобр даних
        table.setSortingEnabled(False)   # Вимикаємо сортування на час заповнення, щоб програма не "гальмувала"
        table.setRowCount(len(rows))     # Устанавливаем количество строк
        for row_index, row_data in enumerate(rows): #   0 ('SAS-SG-360', 'Диск SAS Seagate 360 ', '2 SFF', 5, Decimal('87.00'), datetime.datetime(2026, 3, 31, 17, 16, 17, 570000), 'SAS-2', 360, 6000) 1 () 2 (),....
           for col_index, value in enumerate(row_data): #  0 NVME-WD-720  1 Диск NVME Western Digital 720  2 PCIe 40  3 11  4 231.00 5 2026-03-31 04:43:06.980000
              komirka = TableManager._create_table_komirka(value)   #  Використовуємо окремий внутр метод для створення об'єкта комірки для таблиці
              table.setItem(row_index, col_index, komirka) # Розміщуємо створений об'єкт комірки у конкретну клітинку таблиці
        TableManager._prepare_table_ui(table)

    @staticmethod  # статич метод який нічого не міняє всередині класу TableManager, він просто бере вхідні дані та видає результат
    def _create_table_komirka(value):  # Внутр метод по створені та форматуванні комірки для таблиці відображення даних на екрані
       komirka = QTableWidgetItem()  #  Створ порожню (елемент) комірку для таблиці
       if isinstance(value, (int, float, Decimal)):        # чи є значення числом 
           dec_val = float(value) if isinstance(value, Decimal) else value  # Перетвор Decimal в Float
           komirka.setData(Qt.ItemDataRole.EditRole, dec_val)  #  записуємо дані "всередину" комірки так, щоб таблиця розуміла їхній справжній тип (число, дата тощо), а не просто бачила в них набір символів
       elif isinstance(value, (datetime.date, datetime.datetime)):       # чи є значення датою 
           date = QDate(value.year, value.month, value.day)   # створюємо об'єкт дати у форматі, який «розуміє» бібліотека
           komirka.setData(Qt.ItemDataRole.EditRole, date)  
       else:    # Якщо в базі щось є (is not None) — перетвори це на текст. А якщо там порожньо — покажи просто порожній рядок
           komirka.setData(Qt.ItemDataRole.EditRole, str(value) if value is not None else "") 
       return komirka 

    @staticmethod   # статич метод який нічого не міняє всередині класу TableManager, він просто бере вхідні дані та видає результат
    def _prepare_table_ui(table):    # Внутр метод , налаштовує візуальний вигляд таблиці
        table.setSortingEnabled(True)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSortIndicatorShown(True)
        header.setMinimumSectionSize(100)

class DialogWindow:   #  Клас-помічник формує діалогове вікно про помилку, увагу, повідомлення
    @staticmethod   # статич метод який нічого не міняє всередині класу DialogWindow
    def form_dialog_wind(title_text, tilo_text, icon_type): # Формує діалогове вікно виводу помилок, повідомлень
        msg = QMessageBox()   #  Створ обєкт спец класу для виводу діалог вікна
        msg.setWindowTitle(title_text)
        msg.setText(tilo_text)
        msg.setIcon(icon_type)   # Тип іконки: чи помилка чи Увага
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()   # Показуємо вікно

class InputValidator:  # Клас-помічник
    @staticmethod   #  Декоратор, дозволяє викликати метод apply без створення екземпляра класу (просто InputValidator.check_entered_data(...))
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