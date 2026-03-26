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

class SelectCategory:  #  Вибирає категорії товарів з таблиці Categories
    def __init__(self, name_table):
        self.name_table = name_table
  
    def get_category_and_id(self):    #  Отримуємо назви категорії товару і її id і її tag щоб знати яку таблицю використ: чи Process_det чи Memory_det, ...
        query = f"SELECT Catid, Catname, tag FROM {self.name_table} WHERE Parentid IS NULL;"    
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query)     # Виконуємо запит через курсор
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.  
    
    def get_subcategory_by_id(self, id):   #  Отримуємо назви підкатегорій товару за вказаним id
        query = f"SELECT Catname FROM {self.name_table} WHERE Parentid = {id};"
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query)     # Виконуємо запит через курсор
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.          

    def get_name_all_stovpciv_table(self, table = None ):  # Отримуємо назви всіх стовпців в таблиці через звернення до системних таблиць sys
        if table:     # Якщо передали назву іншої таблиці — беремо її, якщо ні — беремо ту, що в __init__ в конструкторі
            table2 = table
        else:
            table2 = self.name_table
        query = f"SELECT name AS Column_Name FROM sys.columns WHERE object_id = OBJECT_ID('{table2}');" 
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query)     # Виконуємо запит через курсор
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.    

    def get_name_table_by_tag(self, table = None, tag_table = None):    #  Приймає тег і видає  назву таблиці, яка відпов цьому тегові
        if table:     # Якщо передали назву іншої таблиці — беремо її, якщо ні — беремо ту, що в __init__ в конструкторі
            table2 = table
        else:
            table2 = self.name_table 
        query = f"SELECT table_name FROM {table2} WHERE tag = ?";     
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query, (tag_table,))     # Виконуємо запит через курсор і передаємо tag_table  як кортеж  
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.           

    def get_display_ukrtext(self, table = None, eng_name_stovpec = None): # Видае читабильний укр. текст при вводі даних в форму, за вказаним eng name_stovpec
         if table:     # Якщо передали назву іншої таблиці — беремо її, якщо ні — беремо ту, що в __init__ в конструкторі
            table2 = table
         else:
            table2 = self.name_table 
         query = f"SELECT ukr_namestovp FROM {table2} WHERE eng_namestovp = ?";      
         with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query, (eng_name_stovpec,))     # Виконуємо запит через курсор і передаємо tag_table  як кортеж  
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.     

    def get_neccess_stovpci_and_type(self, table = None):    # по назві таблиці вертає назви не всіх стовпців, їх тип і max кількість символів яка відведена для даного стовпця
        # Не всіх стовпців, тобто виключаємо 1) id з властив identity, 2) datetime, 3) Foreign Keys
        if table:     # Якщо передали назву іншої таблиці — беремо її, якщо ні — беремо ту, що в __init__ в конструкторі
            table2 = table
        else:
            table2 = self.name_table 
        query = f"""SELECT COLUMN_NAME, DATA_TYPE,  COALESCE(CHARACTER_MAXIMUM_LENGTH, 
          COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'precision')) as [Length] FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE (TABLE_SCHEMA + '.' + TABLE_NAME) = '{table2}'
                       AND COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 0
                       AND DATA_TYPE NOT IN ('datetime', 'datetime2', 'timestamp')
                       AND COLUMN_NAME NOT IN (
                            SELECT KCU.COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU
                               JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC 
                               ON KCU.CONSTRAINT_NAME = TC.CONSTRAINT_NAME
                               AND KCU.TABLE_SCHEMA = TC.TABLE_SCHEMA
                               WHERE TC.CONSTRAINT_TYPE = 'FOREIGN KEY'
                               AND (TC.TABLE_SCHEMA + '.' + TC.TABLE_NAME) = '{table2}'); """
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query)     # Виконуємо запит через курсор і передаємо tag_table  як кортеж  
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання. 

    def get_all_stovp_bez_identity_datetime(self, table = None):  # Отримуємо назви всіх стовпців в таблиці крім тих, які з властив Identity id і datetime
        # Не всіх стовпців, тобто виключаємо 1) id з властив identity, 2) datetime 
        if table:     # Якщо передали назву іншої таблиці — беремо її, якщо ні — беремо ту, що в __init__ в конструкторі
            table2 = table
        else:
            table2 = self.name_table 
        query = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE (TABLE_SCHEMA + '.' + TABLE_NAME) = '{table2}'
                       AND COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 0
                       AND DATA_TYPE NOT IN ('datetime', 'datetime2', 'timestamp')"""
        with DBConnector() as conn:   # conn — це об'єкт Connection або труба двері до бд
            cursor = conn.cursor()    # Створюємо «посередника» між Python-кодом і базою даних
            cursor.execute(query)     # Виконуємо запит через курсор і передаємо tag_table  як кортеж  
            return cursor.fetchall()  # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів   
        # автоматично викличеться __exit__ для закриття з'єднання.                 