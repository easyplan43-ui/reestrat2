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
    
    def __enter__(self):     #     Устанавливает соединение с базой данных, при удаче вертає обєкт, при неудаче - None
        try:
            self.connection = pyodbc.connect(self.connection_string, timeout = 4)   # Ссылка на объект соединения (connection), ето "труба" к базе данных.
            return self.connection  # Повертає обєкт зєднання
        except pyodbc.Error as ex:
            sqlstate = ex.args[0] if ex.args else None    # получаем стандартизированный 5-символьный код ошибки, который сообщает база данных
            if sqlstate == '28000':
                QMessageBox.critical(None, "Помилка аутентификації", f" Проверьте логин и пароль. Детали:  {ex}")
                logger_db_conn.error(f"Помилка аутентификації при підключені к серверу SQL. Детали: {ex}")         # logger з файлу ragistr_error
            else:
                QMessageBox.critical(None, "Помилка зєднання", f"Не удалось подключиться к серверу SQL. Детали: {ex}")
                logger_db_conn.error(f"Не удалось подключиться к серверу SQL. Детали: {ex}")         # logger з файлу ragistr_error
            return None    
        
    def __exit__(self, exc_type, exc_val, exc_tb): # Магич метод автоматически вызывается при выходе из блока with, гарантируя корректное закрытие ресурсов 
        if self.connection:
            self.connection.close()

class  WorkDB:   # Базовий клас, працює із бд, надсилає запити до бд і отримує дані або [], робить логування в файл, можливо пізніше зроби його АБСТРАКТНИМ
    def __init__(self, name_table):
       self._name_table = name_table    # _name_table - private, внутр логіка класу, не чіпати ззовні  

    def execute_query(self, query, params=None):  # метод виконує запит до бд через try 
        with DBConnector() as conn:    # conn — це об'єкт Connection або труба двері до бд
            if not conn:
                return []     # ПОВЕРТАЄМО ПОРОЖНІЙ СПИСОК, ЯКЩО НЕМАЄ З'ЄДНАННЯ
            try:     
                with conn.cursor() as cursor:    # Створюємо посередника між Python-кодом і базою даних і курсор буде гарант закрит після отрим даних
                    cursor.execute(query, params or ())    # Виконуємо запит через курсор
                    return cursor.fetchall()               # Збирає всі знайдені рядки з бази даних і повертає їх у вигляді списку: кортежів  
            except Exception as ex:
                logger_db_conn.error(f"Не вдалося виконати запит до: {self._name_table} . Детали: {ex}")         # logger з файлу ragistr_error
                return []      # ПОВЕРТАЄМО ПОРОЖНІЙ СПИСОК ПРИ ПОМИЛЦІ ЗАПИТУ
    
    def _get_target_table(self, table): # Допоміжний внутр. метод для вибору таблиці (якась нова передана таблиця або та що по дефолту)
        return table if table else self._name_table  # Якщо передали назву іншої таблиці — беремо її, якщо ні — беремо ту, що в __init__ в конструкторі
    
    def get_name_all_stovpciv_table(self, table = None ):  # Отримуємо назви всіх стовпців в таблиці через звернення до системних таблиць sys
        target_table = self._get_target_table(table)
        query = f"SELECT name AS Column_Name FROM sys.columns WHERE object_id = OBJECT_ID('{target_table}');" 
        return self.execute_query(query)   

    def get_name_table_by_tag(self, table = None, tag_table = None):    #  Приймає тег і видає  назву таблиці, яка відпов цьому тегові
        target_table = self._get_target_table(table)  
        query = f"SELECT table_name FROM {target_table} WHERE tag = ?";  
        return self.execute_query(query, (tag_table,))   # Виконуємо запит через курсор і передаємо tag_table  як кортеж 
    
    def get_display_ukrtext(self, table = None, eng_name_stovpec = None): # Видае читабильний укр. текст при вводі даних в форму, за вказаним eng name_stovpec
        target_table = self._get_target_table(table) 
        query = f"SELECT ukr_namestovp FROM {target_table} WHERE eng_namestovp = ?";
        return self.execute_query(query, (eng_name_stovpec,))    # Виконуємо запит через курсор і передаємо eng_name_stovpec  як кортеж  
    
    def get_all_stovp_bez_identity(self, table = None):  # Отримуємо назви всіх стовпців в таблиці крім тих, які з властив Identity id і foreign keys
        target_table = self._get_target_table(table)
        query = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE (TABLE_SCHEMA + '.' + TABLE_NAME) = '{target_table}'
                       AND COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 0
                       AND COLUMN_NAME NOT IN (
                            SELECT KCU.COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU
                               JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC 
                               ON KCU.CONSTRAINT_NAME = TC.CONSTRAINT_NAME
                               AND KCU.TABLE_SCHEMA = TC.TABLE_SCHEMA
                               WHERE TC.CONSTRAINT_TYPE = 'FOREIGN KEY'
                               AND (TC.TABLE_SCHEMA + '.' + TC.TABLE_NAME) = '{target_table}'); """
        return self.execute_query(query)
    
    def get_foreignkey(self, table = None):    # Отримуємо 1) - назву стовпця з властивістью Foreign key і 2) - назву стовпця на який 1 стовпець зсилається
        target_table = self._get_target_table(table)
        query = f"""SELECT COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName,
                COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ReferencedColumnName
                FROM sys.foreign_keys AS f INNER JOIN 
                sys.foreign_key_columns AS fc 
                ON f.object_id = fc.constraint_object_id
                WHERE f.parent_object_id = OBJECT_ID('{target_table}')
                ORDER BY ColumnName;  """ 
        return self.execute_query(query) 

    def get_all_stovp_bez_identity_datetime(self, table = None):  # Отримуємо назви всіх стовпців в таблиці крім тих, які з властив Identity id і datetime
        target_table = self._get_target_table(table) 
        query = f"""SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE (TABLE_SCHEMA + '.' + TABLE_NAME) = '{target_table}'
                       AND COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 0
                       AND DATA_TYPE NOT IN ('datetime', 'datetime2', 'timestamp')"""
        return self.execute_query(query) 
 
    def get_neccess_stovpci_and_type(self, table = None):    # по назві таблиці вертає назви не всіх стовпців, їх тип і max кількість символів яка відведена для даного стовпця
        # Не всіх стовпців, тобто виключаємо 1) id з властив identity, 2) datetime, 3) Foreign Keys  
        target_table = self._get_target_table(table)
        query = f"""SELECT COLUMN_NAME, DATA_TYPE,  COALESCE(CHARACTER_MAXIMUM_LENGTH, 
          COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'precision')) as [Length] FROM INFORMATION_SCHEMA.COLUMNS 
                   WHERE (TABLE_SCHEMA + '.' + TABLE_NAME) = '{target_table}'
                       AND COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA + '.' + TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 0
                       AND DATA_TYPE NOT IN ('datetime', 'datetime2', 'timestamp')
                       AND COLUMN_NAME NOT IN (
                            SELECT KCU.COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU
                               JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC 
                               ON KCU.CONSTRAINT_NAME = TC.CONSTRAINT_NAME
                               AND KCU.TABLE_SCHEMA = TC.TABLE_SCHEMA
                               WHERE TC.CONSTRAINT_TYPE = 'FOREIGN KEY'
                               AND (TC.TABLE_SCHEMA + '.' + TC.TABLE_NAME) = '{target_table}'); """ 
        return self.execute_query(query)
        
class ZaputuCategoriesDB(WorkDB):   # наслідує клас WorkDB і містить методи із запитами які стосуються категорій до бд
    def get_category_and_id(self):    #  Отримуємо назви категорії товару і її id і її tag щоб знати яку таблицю використ: чи Process_det чи Memory_det, ...
        query = f"SELECT Catid, Catname, tag FROM {self._name_table} WHERE Parentid IS NULL;"
        return self.execute_query(query)  # звертаємося до методу класу WorkDB, щоб той повернув або cursor.fetchall() або []

    def get_subcategory_by_id(self, id):   #  Отримуємо назви підкатегорій товару за вказаним id
        query = f"SELECT Catid, Catname FROM {self._name_table} WHERE Parentid = ?;"
        return self.execute_query(query, (id,))    # звертаємося до методу класу WorkDB, щоб той повернув або cursor.fetchall() або [] 

class ZaputuProductDB(WorkDB):  # наслідує клас WorkDB і містить методи із запитами які виводять дані про продукт із двох таблиць JOIN  
    # Цей метод виводить всі характеристики продукта з двох таблиць WHERE за вибраною підкатегорією в sub випадаючому списку:
    def get_product_details(self, all_columns, depend_table, cortege_fk_prim_key, cortege_fk_prim_key_where, sub_cat_id):
        query = f"""SELECT {all_columns} FROM {self._name_table} AS m INNER JOIN 
               {depend_table} AS d ON m.{cortege_fk_prim_key[0][1]} = d.{cortege_fk_prim_key[0][0]} 
                WHERE m.{cortege_fk_prim_key_where[0][0]} = ?;"""
        return self.execute_query(query, (sub_cat_id,))
    
    # Цей метод виводить всі характеристики продукта з двох таблиць згідно тексту який ввів користув в полі пошуку
    def get_product_details_by_search(self, all_columns, depend_table, cortege_fk_prim_key, query_text):
        query = f"""SELECT {all_columns} FROM {self._name_table} AS m INNER JOIN 
                    {depend_table} AS d ON m.{cortege_fk_prim_key[0][1]} = d.{cortege_fk_prim_key[0][0]} 
                     WHERE m.Artukyl LIKE ?;"""
        param = f"%{query_text}%"                  # захист від SQL Injection
        return self.execute_query(query, (param,))
      
   

