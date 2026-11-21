import os
import sys
import re #  для розділення слів де пробілів два і більше
current_dir = os.path.dirname(os.path.abspath(__file__))  # повертає шлях до папки в якій лежить поточний файл скрипту, тобто /testu_for_metodiv
if os.path.dirname(current_dir) not in sys.path: # Якщо в систем списку папок немає шляху до БАТЬК папки (reestrat2), то додаємо його, щоб працювали імпорти
    sys.path.append(os.path.dirname(current_dir)) 
# --- Точка входу для запуску тесту ---
from conn_to_db import ZaputuProductDB # імпортуємо клас поробі із бд
from constants import Table_main_product
if __name__ == "__main__":
    TXT_FILE_PATH = os.path.join(current_dir, "outer_artukyls.txt")  # обєднуємо шлях до папки і імя файлу
   
    # Перевіряємо, чи існує файл перед початком циклу
    if not os.path.exists(TXT_FILE_PATH):  # перевір чи існує файл/папка за вказаною адресою
        print(f"Помилка: Файл не знайдено за шляхом: {TXT_FILE_PATH}")
        sys.exit()
    # Відкриваємо файл для порядкового читання
    with open(TXT_FILE_PATH, "r", encoding="utf-8") as file: # відкрив файл у режимі читання і створ потокову зміну вказівник - file через яку ми будемо читати вміст
          artukyl_list = file.read().split()
    ekzemp_product = ZaputuProductDB(Table_main_product)
    all_ids = ekzemp_product.select_all_id()
   
    list_id = []   # Перетворюємо в список із списка кортежів які нам вернула бд
    for id_db in all_ids: 
        list_id.append(id_db[0])
    if (len(artukyl_list) < len(list_id) ):  # Якщо кількість елем із файлу є меншою ніж кільк id із бд
        print("Artukyls ne e dostatno dla vsix tovariv iz bd")
        sys.exit()    
    id_artuk = list(zip(artukyl_list, list_id))   # робимо список кортежів типу [('artuk', id), ('artuk', id), ...]
    if (ekzemp_product.update_zartukyl(id_artuk)):
        print("Усі зовнішні артикули успішно записані в базу даних!")
    else:
         print(f"Помилка під час оновлення: {ekzemp_product.error_zaputy}")
         
    
  

