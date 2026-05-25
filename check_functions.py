# В цьому файлі я створюю Статичні методи @staticmethod, щоб не створювати екземпляр класу
import os
import sys
def instead_path_create_meipass(relative_path):  # щоб не пропалдало зображення іконок призбиранні проекту з доп py-auto-exe
    """ Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    try:
        base_path = sys._MEIPASS    # PyInstaller создает временную папку и хранит путь в _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def search_val_in_dict(diction, key_to_search): # за вказаним key_to_search  шукає в словнику diction те саме key і виводить відпов value     
        if key_to_search is None:
            return None
        return diction.get(key_to_search.lower()) # .lower() додано для захисту від помилок регістру


