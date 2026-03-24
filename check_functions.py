import os
import sys
def instead_path_create_meipass(relative_path):  # щоб не пропалдало зображення іконок призбиранні проекту 
    """ Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    try:
        base_path = sys._MEIPASS    # PyInstaller создает временную папку и хранит путь в _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# цей код тобі знадобиться для розробки кнопки Адміністратору при редагуванні submenu
#def save_settings_inJSON(username, remember): # зберігаємо username в JSON файлі
#    """Зберігає або видаляє дані залежно від стану checkbox."""
#    if not os.path.exists(CONFIG_DIR):  # проверяет, существует ли папка по указанному пути CONFIG_DIR. Если путь не существует, условие становится истинным
#        os.makedirs(CONFIG_DIR) # рекурсивно создает директорию. В отличие от os.mkdir, эта функция создаст не только конечную папку, но и все недостающие родительские папки в пути
 #   data = {                                                     #   {   це пример содержимого з файла "config.json"
#        "username": username if remember else "",                #       "username": "asdsd",
#        "remember": remember                                     #       "remember": true 
 #   }                                                            #   }

class Check_entered_data():   # Провіряємо введені від корист дані по типам даних
    def __init__(self, raw_data):
        self.raw_data = raw_data
    
    def validate_varchar(new_value, max_value):
    # Разрешаем пустую строку (для удаления), англ. буквы, макс длина задана max_value
       if new_value == "":
           return True
       if len(new_value) == 0:
           return False
       pattern = fr"^[a-zA-Z0-9\s\.,!\?а-яА-ЯЦцЄєІіЇї]{{0,{max_value}}}+$"   
       return re.fullmatch(pattern, new_value) is not None  # Если строка яку ввів користувач полностью соответствует шаблону pattern, 
                                                         # fullmatch возвращает объект совпадения (match object), если соответствия нет, функция возвращает None

    def validate_dec_num(new_value, precision, scale):      # precision and scale це наприклад decimal(5,2)
       if new_value == "":
          return True
       pattern = rf"^\d{{0,{precision}}}(\.\d{{0,{scale}}})?$"
       return re.fullmatch(pattern, new_value) is not None     # используется для проверки того, соответствует ли вся строка целиком заданному регулярному выражению

    def validate_scrolledtext(event):  # провіряє довгий текст на ввід щоб у ньому не було таких символів "@#$%&^|\/"
       forbid_symb = "@#$%&^|/"
       # event.char содержит символ, который пытается ввести пользователь
       if event.char in forbid_symb:
          return "break"  # Останавливает дальнейшую обработку события (символ не появится)

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
