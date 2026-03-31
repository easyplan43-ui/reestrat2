import pyodbc

# 1. Подготовка данных (собираем плоский список для временной таблицы)
# Допустим, у вас есть список анкет, где каждая анкета — это один длинный список
# data_to_insert = [row1, row2, row3, ...]
data_to_insert = [list_dani_main_tabl + list_dani_depend_tabl for _ in range(100)] 

# Считаем общее кол-во колонок (основная + зависимая)
total_columns = kilk_stovp_main_tabl + len(list_all_stovp_depend_tabl.split(','))
placeholders = ", ".join(["?"] * total_columns)

conn = pyodbc.connect(your_conn_str)
cursor = conn.cursor()
cursor.fast_executemany = True

try:
    # 2. Создаем временную таблицу в памяти SQL Server
    # Типы данных (INT, VARCHAR) должны соответствовать вашим реальным колонкам
    cursor.execute(f"CREATE TABLE #TempData ({list_stovp_bez_id_maintabl}, {list_all_stovp_depend_tabl})")

    # 3. Записываем ВСЕ данные порциями во временную таблицу
    chunk_size = 1000
    for i in range(0, len(data_to_insert), chunk_size):
        chunk = data_to_insert[i : i + chunk_size]
        cursor.executemany(f"INSERT INTO #TempData VALUES ({placeholders})", chunk)

    # 4. ГЛАВНЫЙ ШАГ: Перенос данных из #TempData в реальные таблицы со связью
    # Используем OUTPUT, чтобы поймать новые ID из MainTable и сразу вставить в DependTable
    transfer_sql = f"""
    BEGIN TRANSACTION;
    BEGIN TRY
        -- Таблица для хранения соответствия (Старый уникальный признак -> Новый ID)
        -- Здесь 'UniqueCol' — это колонка, которая уникальна для каждой анкеты (напр. артикул или имя)
        DECLARE @InsertedRows TABLE (PrimaryID INT, RowIndex INT);

        -- 1. Вставляем в основную таблицу
        INSERT INTO {Table_main_product} ({list_stovp_bez_id_maintabl})
        OUTPUT INSERTED.ID, 0 -- Здесь логика связи может зависеть от ваших полей
        SELECT {list_stovp_bez_id_maintabl} FROM #TempData;

        -- 2. Вставляем в зависимую таблицу (логика зависит от того, как вы связываете строки)
        -- Если у вас нет явного ключа связи в данных, проще всего делать это через курсор или 
        -- предварительно сгенерированный ID в Python.
        
        INSERT INTO {self.table_name_depend} ({list_all_stovp_depend_tabl})
        SELECT {list_all_stovp_depend_tabl} FROM #TempData;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
    """
    
    # Если связь сложная, проще всего вставить Main, а потом Depend, используя общий ключ (например, артикул)
    cursor.execute(transfer_sql)
    conn.commit()

finally:
    cursor.close()
    conn.close()
