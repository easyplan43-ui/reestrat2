# Цей тест ще не дороблений
import sys
import os
import pytest
from unittest.mock import MagicMock, patch  # імпортуємо муляж
from PyQt6.QtWidgets import QApplication 
# Додаємо батьківську папку (reestrat2) у шляху пошуку Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Імпортуємо ваш клас BasicSklad з вашого файлу (модуля)
from submenu_stock_classes import BasicSklad    # Піди у файл submenu_stock_classes.py і знайди там клас BasicSklad

@pytest.fixture(scope="module")   # декоратор що створює тестове оточення перед запуском тестів, де scope - це область видимості 
def sklad_object():   #  Створюємо об'єкт класу для тестів, де потрібен self
    app = QApplication.instance()  # находимо ссылку на уже существующий объект главного приложения QApplication
    if app is None:   # Перевіряємо, чи QApplication вже створено, щоб не виникало конфліктів
        app = QApplication(sys.argv)  # Якщо додаток ще не створено — створюємо його віртуальну копію для тестів
        obj = BasicSklad()
    return obj  # повернення обєкту класу

# Мокаємо зовнішню функцію search_val_in_dict за місцем її використання/імпорту
@patch('reestrat2.submenu_stock_classes.search_val_in_dict')
def test_get_ukr_dict_type_success(mock_search_val, sklad_object):
    """Тест успішного сценарію, коли всі дані знайдені та повернуті."""
    table_with_tag = "tag55"            # Готуємо фейкові вхідні дані та налаштовуємо залежності 
    sklad_object.sub_cat_id = "10"     # id підкатегорії, який шукатиметься
    
    # Імітуємо об'єкт випадаючого списку та його метод get_curr_data() -> [42]
    sklad_object.ekzemp_sub_vupad_spusok = MagicMock() 
    sklad_object.ekzemp_sub_vupad_spusok.get_curr_data.return_value = [42]
        
    # Імітуємо об'єкт категорій та отримання списку таблиць
    sklad_object.ekzemp_category = MagicMock()
    fake_tables_list = [('cpu', 'hardware.Proccess_det'), ('ram', 'hardware.Memory_det')]
    sklad_object.ekzemp_category.get_tag_nametable.return_value = fake_tables_list
    
    # Налаштовуємо зовнішню функцію пошуку за тегом: вона повинна повернути назву таблиці
    mock_search_val.return_value = "hardware.Proccess_det"
    
    # Готуємо фейкові результати для стовпців (словники словників)
    fake_main_cols = {'Артикул': {"name": 'artukyl', "type": 'varchar', "size": 25}}
    fake_depend_cols = {"Роз'єм/Сокет": {"name": 'socket', "type": 'varchar', "size": 30}}
    
    # Мокаємо метод _get_spusok_stovp_transl, який ми тестували раніше
    # Використовуємо side_effect, щоб метод повертав різні дані для різних викликів!
    sklad_object._get_spusok_stovp_transl = MagicMock(side_effect=[fake_main_cols, fake_depend_cols])
    
    # === 2. Викликаємо метод, який тестуємо ===
    dict_stovp_main, dict_stovp_depend = sklad_object._get_ukr_dict_type(table_with_tag)
    
    # === 3. Перевірки (Asserts) ===
    
    # Перевіряємо, що sub_cat_id успішно збережено в атрибут класу
    assert sklad_object.sub_cat_id == 42
    
    # Перевіряємо, що назва знайденої таблиці збереглася в атрибут
    assert sklad_object.table_name_depend == "hardware.Proccess_det"
    
    # Перевіряємо фінальний результат роботи методу
    assert dict_stovp_main == fake_main_cols
    assert dict_stovp_depend == fake_depend_cols
    
    # Перевіряємо, що _get_spusok_stovp_transl викликався рівно 2 рази з правильними параметрами
    assert sklad_object._get_spusok_stovp_transl.call_count == 2
    sklad_object._get_spusok_stovp_transl.assert_any_call(None)
    sklad_object._get_spusok_stovp_transl.assert_any_call("hardware.Proccess_det")
   