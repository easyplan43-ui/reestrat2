import os
import sys
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
import re   #  вбудований модуль re (Regular Expressions)
def instead_path_create_meipass(relative_path):  # щоб не пропалдало зображення іконок призбиранні проекту 
    """ Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    try:
        base_path = sys._MEIPASS    # PyInstaller создает временную папку и хранит путь в _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InputValidator:  # це звичайна функція check_entered_data, яку просто «сховали» всередину класу для кращої організації коду.
    @staticmethod   #  Декоратор, дозволяє викликати метод apply без створення екземпляра класу (просто InputValidator.check_entered_data(...))
    def check_entered_data(widget, datatype, size):   # використ декоратор оскільки цей метод не потребує доступу до самого класу ні до конкр обєкта
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