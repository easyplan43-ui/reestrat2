import pyodbc
from PyQt6.QtWidgets import QMessageBox
from constants import *      # Для загрузки переменных і констант из .файла
from registr_error import logger_db_conn

class DBConnector:   
    def __init__(self):   # self — это ссылка на конкретный экземпляр (объект) класса, который создается в данный момент.
        self.connection_string = (
           f"DRIVER={{ODBC Driver 18 for SQL Server}};"  
           #f"DRIVER={{SQL Server}};"  # Это «встроенный» старий драйвер, который присутствует в любой версии Windows по умолчанию.
           f"SERVER={sql_server};"
           f"DATABASE={database};"
           f"Trusted_Connection=yes;"
           f"Encrypt=yes;"
           f"TrustServerCertificate=yes;"  # Обязательно, если сертификат самоподписанный
        )
        self.connection = None
    
    def __enter__(self):     #     Устанавливает соединение с базой данных
        try:
            self.connection = pyodbc.connect(self.connection_string, timeout = 4)   # Ссылка на объект соединения (connection), ето "труба" к базе данных.
            return self.connection  # Повертає обєкт зєднання
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]  # получаем стандартизированный 5-символьный код ошибки, который сообщает база данных
            if sqlstate == '28000':
                QMessageBox.critical(self, "Ошибка аутентификации", f" Проверьте логин и пароль. Детали:  {ex}")
                logger_db_conn.error(f"Не удалось подключиться к серверу SQL. Детали: {ex}")         # logger з файлу ragistr_error
            else:
                QMessageBox.critical(self, "Помилка зєднання", f"Не удалось подключиться к серверу SQL. Детали: {ex}")
                logger_db_conn.error(f"Не удалось подключиться к серверу SQL. Детали: {ex}")         # logger з файлу ragistr_error
            raise     # Если убрать raise, программа продолжит выполнение следующей строки кода, как будто ошибки не было 

    def __exit__(self, exc_type, exc_val, exc_tb): # Магич метод автоматически вызывается при выходе из блока with, гарантируя корректное закрытие ресурсов 
        if self.connection:
            self.connection.close()

class SelectCategory:
    def __init__(self, name_table):
        self.name_table = name_table

    def get_category(self):
        query = f"SELECT Catname FROM {self.name_table} WHERE Parentid IS NULL;"    
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query)     # Виконуємо запит через курсор
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.  

        

#ekzemp_category = SelectCategory('hardware.Categories')  # Створюємо екземпляр класу, передаючи назву таблиці
#category = ekzemp_category.get_category()
#list_categor = [item[0] for item in category]  # Перетворюємо з списка кортежів в список
#print (list_categor)
#if category:
   # for categ in category:
   #     print(f"Знайдена категорія: {categ}")
#else:        
   # print("Корінняві категорії не знайдені.")
       