
import sys
import os
import pytest
from unittest.mock import MagicMock, patch  # імпортуємо муляж
from PyQt6.QtWidgets import QApplication 
# Додаємо батьківську папку (reestrat2) у шляху пошуку Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Імпортуємо ваш клас BasicSklad з вашого файлу (модуля)
from submenu_stock_classes import BasicSklad    # Піди у файл submenu_stock_classes.py і знайди там клас BasicSklad# ----------------------------------- Фікстура для ініціалізації Qt-середовища та створення обєкту класу ---------------------------------------------------

#  а цей обєкт класу буде спільний для всіх функцій тестування які йдуть внизу 
@pytest.fixture(scope="module")   # декоратор що створює тестове оточення перед запуском тестів, де scope - це область видимості 
def sklad_object():   #  Створюємо об'єкт класу для тестів, де потрібен self
    app = QApplication.instance()  # находимо ссылку на уже существующий объект главного приложения QApplication
    if app is None:   # Перевіряємо, чи QApplication вже створено, щоб не виникало конфліктів
        app = QApplication(sys.argv)  # Якщо додаток ще не створено — створюємо його віртуальну копію для тестів
        obj = BasicSklad()
    return obj  # повернення обєкту класу

# ---------------------------------------- test for методу _get_spusok_stovp_transl класу BasicSklad ------------------------------------------------------------------------
def test_get_spusok_stovp_transl_with_one(sklad_object):    #  Тест гілки `if tablename == None`.
    fake_db_result = [('Артикул', 'artukyl', 'varchar', 25)]     # Готуємо фейкові вхідні дані, які нібито повернула база даних -  список кортежів
    sklad_object.pered_func_stovp = MagicMock(return_value = fake_db_result)  # замість реального запиту до БД, метод pered_func_stovp просто повернув наш fake_db_result 
    result = sklad_object._get_spusok_stovp_transl(None)  #   Викликаємо наш метод який тестуємо де табл = None
    expected_dict = {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}}  # дані які має наш метод повернути
    assert result == expected_dict    # Провірка результ виконання методу із очікуваним результатом
    sklad_object.pered_func_stovp.assert_called_once_with() # Перевіряємо, що метод викликався БЕЗ аргументів

def test_get_spusok_stovp_transl_with_tablename(sklad_object):   #  Тест гілки else коли tablename == передано назву залеж_табл`
    fake_db_result = [('Артикул', 'artukyl', 'varchar', 25)]     # Готуємо фейкові дані, які нібито повернула база даних -  список кортежів
    sklad_object.pered_func_stovp = MagicMock(return_value=fake_db_result) # видає fake_db_result як реальний резул і присв його до pered_func_stovp
    result = sklad_object._get_spusok_stovp_transl("Users")    # Викликаємо метод з конкретною таблицею
    expected_dict = {'Артикул': {'name': 'artukyl', 'type': 'varchar', 'size': 25}}   # дані які має наш метод повернути 
    assert result == expected_dict   # Провірка результ виконання методу із очікуваним результатом
    sklad_object.pered_func_stovp.assert_called_once_with("Users")  # Перевіряємо, що в базу полетіла саме правильна назва таблиці
