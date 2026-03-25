import os
import sys
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QValidator
import re   #  вбудований модуль re (Regular Expressions)
def instead_path_create_meipass(relative_path):  # щоб не пропалдало зображення іконок призбиранні проекту 
    """ Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    try:
        base_path = sys._MEIPASS    # PyInstaller создает временную папку и хранит путь в _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Check_entered_data2(QValidator):   # Провіряємо введені від корист дані по типам даних
    def __init__(self, datatype, max_size, parent = None):
        super().__init__(parent)
        self.datatype = datatype
        self.max_size = max_size if max_size != -1 else 32767 # коли користувач нічого не вказав в полі вводу то використ розмір size
        self.text_pattern = fr"^[a-zA-Z0-9\s\.,!\?а-яА-ЯЦцЄєІіЇї]{{0,{self.max_size}}}+$"
        self.decimal_pattern = r"^-?\d*[.,]?\d*$"    # Патерн для Decimal (числа з крапкою/комою)
        self.int_pattern = r"^-?\d*$"   # Патерн для Int (тільки цифри та мінус)
    
    def validate(self, string, position):     # position - текуща позиція курсора в полі вводу
        if string == "-":     # Дозволяємо мінус на початку
            return QValidator.Intermediate, string, position  # введенный текст пока не является полностью корректным, но может стать таковым даль
        if "nvarchar" in self.datatype or "varchar" in self.datatype:      # Логіка  перевірки для NVARCHAR / VARCHAR
            if re.fullmatch(self.text_pattern, string):  # якщо весь рядок string співпаде із шаблоном 
                return QValidator.Acceptable, string, position  #  повернення кортежу з трьох значень: (стан_валідації, рядок, позиція_курсору)
        elif "int" in self.datatype:   # Логіка перевірки для INT
            if re.fullmatch(self.int_pattern, string):    # якщо весь рядок string співпаде із шаблоном 
                return QValidator.Acceptable, string, position  #  повернення кортежу з трьох значень: (стан_валідації, рядок, позиція_курсору) 
        elif "decimal" in self.datatype or "numerical" in self.datatype:
            if re.fullmatch(self.decimal_pattern, string):
                return QValidator.Acceptable, string, position
        return QValidator.Invalid, string, position    #  QValidator.Invalid - строка полностью недопустима    

class  Check_entered_data():
    def __init__(self, new_value):
        self.new_value = new_value
        
    #def validate_varchar(new_value, max_value):
    #   # Разрешаем пустую строку (для удаления), англ. буквы, макс длина задана max_value
    #   if new_value == "":
    #      return True
    #   if len(new_value) == 0:
    #      return False
    #   pattern = fr"^[a-zA-Z0-9\s\.,!\?а-яА-ЯЦцЄєІіЇї]{{0,{max_value}}}+$"   
    #   return re.fullmatch(pattern, new_value) is not None  # Если строка яку ввів користувач полностью соответствует шаблону pattern, 
                                                         # fullmatch возвращает объект совпадения (match object), если соответствия нет, функция возвращает None

    #def validate_dec_num(new_value, precision, scale):      # precision and scale це наприклад decimal(5,2)
    #   if new_value == "":
    #      return True
    #   pattern = rf"^\d{{0,{precision}}}(\.\d{{0,{scale}}})?$"
    #   return re.fullmatch(pattern, new_value) is not None     # используется для проверки того, соответствует ли вся строка целиком заданному регулярному выражению

    #def validate_scrolledtext(event):  # провіряє довгий текст на ввід щоб у ньому не було таких символів "@#$%&^|\/"
    #   forbid_symb = "@#$%&^|/"
    ##   # event.char содержит символ, который пытается ввести пользователь
    #   if event.char in forbid_symb:
    #      return "break"  # Останавливает дальнейшую обработку события (символ не появится)

    def validate_smallint(new_value):
        if new_value == "":          # Разрешаем пустое поле (чтобы можно было стирать символы)
           return True
        if new_value.isdigit() and len(new_value) <=5:             # Проверяем, состоит ли ввод только из цифр
            value = int(new_value)
            # Проверка диапазона положительного smallint (0 - 32767)
            if 0 <= value <= 32767:
                return True
        return False # Блокирует ввод, если условия не выполнены
   
    def validate_int(new_value):
        if new_value == "":                                # Разрешаем пустое поле (чтобы можно было стирать символы)
        #if new_value == "" or new_value is None:          # Разрешаем пустое поле (чтобы можно было стирать символы)
            return True
        if new_value.isdigit() and len(new_value) <= 10:             # Проверяем, состоит ли ввод только из цифр
           value = int(new_value)
           # Проверка диапазона положительного smallint (0 - 32767)
           if 0 <= value <= 2147483647:
              return True
        return False # Блокирует ввод, если условия не выполнены    

class InputValidator:
    @staticmethod
    def apply(widget, datatype, size):
        pattern = ""
        
        if datatype.upper() in ["INT", "INTEGER"]:
            # Тільки цифри, довжина від 0 до size
            pattern = rf"^\d{{0,{size}}}$"
            
        elif datatype.upper() in ["DECIMAL", "NUMERIC"]:
            # Цифри з однією крапкою, довжина до size
            # Примітка: спрощений паттерн, можна уточнити під (10,2)
            pattern = rf"^\d{{0,{size}}}(\.\d{{0,2}})?$"
            
        elif "CHAR" in datatype.upper():
            # Будь-які символи, але обмежена довжина
            pattern = rf"^.{{0,{size}}}$"
        
        if pattern:
            regex = QRegularExpression(pattern)
            validator = QRegularExpressionValidator(regex, widget)
            widget.setValidator(validator)    