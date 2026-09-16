import os
import sys
import time
current_dir = os.path.dirname(os.path.abspath(__file__))  # визнач шлях до папки в якій лежить поточний файл скрипту
parent_dir = os.path.dirname(current_dir)   # Це шлях до папки reestrat2
if parent_dir not in sys.path:  # sys.path - це спец список папок
    sys.path.append(parent_dir)  # Додаємо батьківську папку в sys.path, щоб Python бачив conn_to_db.py
# --- Точка входу для запуску тесту ---
from conn_to_db import WorkDB, ZaputuSkladu # імпортуємо клас поробі із бд
from constants import Table_skladu
if __name__ == "__main__":
    # Оскільки текстовий файл зазвичай лежить в колі проекту,
    # піднімемося на рівень вище, щоб знайти його поруч з папкою reestrat2
    # Або вкажи тут прямий абсолютний шлях до твого файлу, наприклад: "C:/data/warehouses.txt"
    BASE_PROJECT_DIR = os.path.dirname(parent_dir)
    TXT_FILE_PATH = os.path.join(current_dir, "dani_to_table.txt")  # обєднуємо шлях до папки і імя файлу
    print(f'TXT_FILE_PATH={TXT_FILE_PATH}')
    #ekzemp_sklad = ZaputuSkladu(Table_skladu)  # Створ екземпляр класу для роботи зі складами а саме даними про них: назва, адреса, тип
    #list_korteg_stovpciv_bez_id = ekzemp_sklad.get_all_stovp_bez_identity_datetime() # для таблиці Skladu отримуєм список стовпців, які підставляємо в INSERT
    #list_stovp_bez_id = ", ".join([f"[{item[0]}]" for item in list_korteg_stovpciv_bez_id])  # перетв з списку кортежів в список типу: [Category_catid], [Artukyl], [Nazva_tov], [Description], [Kilkist], [Price]
    #kilk_stovp = len(list_korteg_stovpciv_bez_id)   #  Кількість стовпців головн таблиці які потрібно заповнити в запиті INSERT
    #data = ("Оптима Скаут", "Оптовий склад", "Волочийськ", "вул. Б. Хмельницького 93", 1)
    #result = ekzemp_sklad.insert_in_tables(list_stovp_bez_id, kilk_stovp, data);
    #if result:
    #    print("Radok dodano v bd")
    #else:
    #    print(f"Radok ne dodano v bd, error: {ekzemp_sklad.error_zaputy}")    

    # Перевіряємо, чи існує файл перед початком циклу
    if not os.path.exists(TXT_FILE_PATH):  # перевір чи існує файл/папка за вказаною адресою
        print(f"Помилка: Файл не знайдено за шляхом: {TXT_FILE_PATH}")
        sys.exit()
    # Відкриваємо файл для порядкового читання
    with open(TXT_FILE_PATH, "r", encoding="utf-8") as file: # відкрив файл у режимі читання і створ потокову зміну file через яку ми будемо читати вміст
         for line in file:
             clean_line = line.strip()   # відрізаємо від line всі невидимі непотрібні символи   --- БудХаб, Склад готової продукції, Полтава, вул. Лесі Українки 111, 0
             if not clean_line:
                 continue  # Пропускаємо порожні рядки і повертаємося на початок циклу
             raw_parts = clean_line.split(",")   # Розбиваємо рядок з файлу за комою ['ВекторАрт', ' Лабораторія провірки якості', ' Суми', ' вул. Промислова 67', ' 1']
             parts = []  #  ['СвітГруп', 'Мобільний склад', 'Черкаси', 'вул. Головна 89', '1']
             for part in raw_parts:
                 parts.append(part.strip())
                 print(parts)    
             if len(parts) == 5:
                 name, sklad_type, city, address, is_active = parts
                 data = (name, sklad_type, city, address, int(is_active))  # Формуємо кортеж даних для поточного рядка, Приводимо IsActive до числа (int)
    
               
                # Виконуємо запис через твій метод
    #            result = ekzemp_sklad.insert_in_tables(
    #                list_stovp_bez_id, kilk_stovp, data
    #            )

    #            if result:
    #                print(f"Рядок {line_number} додано в БД: {name}")
    #            else:
    #                print(
    #                    f"Рядок {line_number} НЕ додано, помилка: {ekzemp_sklad.error_zaputy}"
    #                )

                # Робимо паузу 40 секунд перед наступним рядком файлу
    #            print("Очікування 40 секунд...")
    #            time.sleep(40)
    #        else:
    ##            print(
    #                f"Рядок {line_number} пропущено: Некоректна кількість елементів ({len(parts)} замість 5)"
    #            )

    #print("Обробку всього файлу завершено!")



