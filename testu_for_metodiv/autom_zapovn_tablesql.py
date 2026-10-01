import os
import sys
import time
import re #  для розділення слів де пробілів два і більше
current_dir = os.path.dirname(os.path.abspath(__file__))  # повертає шлях до папки в якій лежить поточний файл скрипту, тобто /testu_for_metodiv
if os.path.dirname(current_dir) not in sys.path: # Якщо в систем списку папок немає шляху до БАТЬК папки (reestrat2), то додаємо його, щоб працювали імпорти
    sys.path.append(os.path.dirname(current_dir)) 
# --- Точка входу для запуску тесту ---
from conn_to_db import WorkDB, ZaputuSkladu # імпортуємо клас поробі із бд
from constants import Table_agentu
if __name__ == "__main__":
    start_time = time.time() # фіксуємо час початку роботи програми
    # Оскільки текстовий файл зазвичай лежить в колі проекту,
    # піднімемося на рівень вище, щоб знайти його поруч з папкою reestrat2
    # Або вкажи тут прямий абсолютний шлях до твого файлу, наприклад: "C:/data/warehouses.txt"
    TXT_FILE_PATH = os.path.join(current_dir, "dani_to_table_agents.txt")  # обєднуємо шлях до папки і імя файлу
    ekzemp_sklad = ZaputuSkladu(Table_agentu)  # Створ екземпляр класу для роботи зі складами а саме даними про них: назва, адреса, тип
    list_korteg_stovpciv_bez_id = ekzemp_sklad.get_all_stovp_bez_identity_datetime() # для таблиці Skladu отримуєм список стовпців, які підставляємо в INSERT
    list_stovp_bez_id = ", ".join([f"[{item[0]}]" for item in list_korteg_stovpciv_bez_id])  # перетв з списку кортежів в список типу: [Category_catid], [Artukyl], [Nazva_tov], [Description], [Kilkist], [Price]
    print(list_stovp_bez_id)
    kilk_stovp = len(list_korteg_stovpciv_bez_id)   #  Кількість стовпців головн таблиці які потрібно заповнити в запиті INSERT
    
    # Перевіряємо, чи існує файл перед початком циклу
    if not os.path.exists(TXT_FILE_PATH):  # перевір чи існує файл/папка за вказаною адресою
        print(f"Помилка: Файл не знайдено за шляхом: {TXT_FILE_PATH}")
        sys.exit()
    # Відкриваємо файл для порядкового читання
    inserted_string = 0 # лічильник рахує к-ть вставлених рядків в бд
    with open(TXT_FILE_PATH, "r", encoding="utf-8") as file: # відкрив файл у режимі читання і створ потокову зміну вказівник - file через яку ми будемо читати вміст
         for line in file:  # зчитуємо файл по одному рядку
             clean_line = line.strip()   # очищаємо краї рядка line від  непотр символів   --- БудХаб, Склад готової продукції, Полтава, вул. Лесі Українки 111, 0
             if not clean_line:
                 continue  # Пропускаємо порожні рядки і повертаємося на початок циклу
             #raw_parts = re.split(r'\s{2,}', clean_line) # Розбиваємо рядок з файлу там де є 2 і більше пробілів
             raw_parts = clean_line.split(",")   # Розбиваємо рядок з файлу за комою ['ВекторАрт', ' Лабораторія провірки якості', ' Суми', ' вул. Промислова 67', ' 1']
             parts = []  #  ['СвітГруп', 'Мобільний склад', 'Черкаси', 'вул. Головна 89', '1']
             for part in raw_parts:
                 parts.append(part.strip()) # знов очищаємо кожен елемент рядка після splity, бо можуть бути пробіли
             if len(parts) == 6:
                 col1, col2, col3, col4, col5, col6 = parts
                 data = (col1, int(col2), col3, col4, col5, col6)  # Формуємо кортеж даних для поточного рядка, Приводимо IsActive до числа (int)
                 result = ekzemp_sklad.insert_in_tables(list_stovp_bez_id, kilk_stovp, data) # запис в бд через метод із обєкта класа ekzemp_sklad
                 if result:
                     inserted_string = inserted_string + 1 
                     print(f'Radok {inserted_string} dodano v bd')
                 else:
                     print(f"Radok ne dodano v bd, error: {ekzemp_sklad.error_zaputy}")    
                 # Робимо паузу 30 секунд перед наступним рядком файлу
                 print("Очікування 30 секунд...")
                 time.sleep(30)   # повністю зупиняємо виконання проги на 40 сек
             else:
                 print(f"Некоректна кількість елементів замість 5")
    print("Обробку всього файлу завершено!")
    end_time = time.time()  # фіксуємо час завершення проги
    total_time = int(end_time - start_time)      # загал час роботи проги у секундах
    hours, zal_secon = divmod(total_time, 3600)  # Переводимо секунди в години та хвилини
    minutes, seconds = divmod(zal_secon, 60)
    print(f"All inserted string: {inserted_string} za {hours} hours and {minutes} minutes")  # Виводимо фінальний звіт



