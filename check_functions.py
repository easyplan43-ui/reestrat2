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
    
