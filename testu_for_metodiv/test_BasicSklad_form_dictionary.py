import sys
import os
import pytest
# Додаємо батьківську папку (reestrat2) у шляху пошуку Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Імпортуємо ваш клас BasicSklad з вашого файлу (модуля)
from submenu_stock_classes import BasicSklad    # Піди у файл submenu_stock_classes.py і знайди там клас BasicSklad
# --------------------------- test for @staticmethod  _form_dictionary класу BasicSklad --------------------------------------------------
# -------------- метод є статичним тому не потребує створення обєкту класу  
def test_form_dictionary_four_elements():     # Тест для кортежів із 4-х елементів
    input_data = [('Артикул', 'artukyl', 'varchar', 25), ('Цена', 'price', 'decimal', 5)]
    return_value = {'Артикул': {"name": 'artukyl', "type": 'varchar', "size": 25}, 'Цена':{"name": 'price', "type": 'decimal', "size": 5}}  
    assert BasicSklad._form_dictionary(input_data) == return_value   # Тестуємо @staticmethod _form_dictionary
 
def test_form_dictionary_three_elements():    #  Тест для кортежів із 3-х елементів
    input_data = [('artukyl', 'varchar', 25), ('price', 'decimal', 5)]
    return_value = {'artukyl': {"type": 'varchar', "size": 25}, 'price': {"type": 'decimal', "size": 5}}
    assert BasicSklad._form_dictionary(input_data) == return_value

def test_form_dictionary_two_elements():      #  Тест для кортежів із 2-х елементів
    input_data = [('key1', 'value1'), ('key2', 'value2')]
    return_value = {'key1': 'value1', 'key2': 'value2'}   #  Це те що ви очікуємо коли метод виконається і поверне ось такий результат
    assert BasicSklad._form_dictionary(input_data) == return_value

def test_form_dictionary_one_element():        #  Тест для кортежів із 1-х елемента
    input_data = [('artukyl',), ('nazva_tov',)]
    return_value = {'artukyl': '', 'nazva_tov': ''}
    assert BasicSklad._form_dictionary(input_data) == return_value

def test_form_dictionary_empty_list():  #   Тест для випадку, коли на вхід приходить порожній список []
    input_data = []
    return_value ={}   # Метод має безпечно повернути порожній словник
    assert BasicSklad._form_dictionary(input_data) == return_value
