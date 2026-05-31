import sys, os   # doopracuy cey test
import unittest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
# Додаємо батьківську папку (reestrat2) у шляху пошуку Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dodat_classes import TablManager
def table_object():  #   Створюємо об'єкт класу для тестів, де потрібен self
    app = QApplication.instance()   # находимо ссылку на уже существующий объект главного приложения QApplication
    if app is None:    # Перевіряємо, чи QApplication вже створено, щоб не виникало конфліктів
        app = QApplication(sys.argv)   # Якщо додаток ще не створено — створюємо його віртуальну копію для тестів
    obj = TablManager()
    return obj    # повернення обєкту класу
 
def test_fill_table(ekz_table):
    simple_list = ['AM5-GB-B477', 'Материнська плата Gigabyte B477', 'micro ATX', 13, 57]
    ekz_table.fill_table(simple_list, bagatovum = False)
     # 3. Перевіряємо кількість рядків
    assert ekz_table.rowCount() == 1  # Перевірити що кількість рядків == 1

    for col_index, value in enumerate(simple_list):
       # Беремо комірку з 0-го рядка та поточного стовпця
       komirka = ekz_table.item(0, col_index)
    
       # 2. Витягуємо з неї чисті дані (число, дату чи текст)
       faktychne_znachennya = komirka.data(Qt.ItemDataRole.EditRole.value)
    
       # 3. Порівнюємо значення
       assert faktychne_znachennya == value
    print("🎉 Тест простого списку пройдено успішно!")

# --- 3. ЗАПУСК ТЕСТУ ---
if __name__ == '__main__':
    # Отримуємо об'єкт таблиці
    my_obj = table_object()   
    
    # Запускаємо нашу перевірку
    test_fill_table( my_obj)       
    
   



