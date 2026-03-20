class TableManager:
    def __init__(self, table):
        self.table = table
    def process_table(self):
        """Метод, принимающий только таблицу."""
        print(f"Обработка таблицы: {self.table}")
        return len(self.table)

    def process_with_var(self, var1):
        """Метод, принимающий таблицу и переменную."""
        print(f"Обработка таблицы {self.table} с параметром: {var1}")
        return f"{self.table}_{var1}"

# --- Пример вызова ---
data = [1, 2, 3]
manager = TableManager(data)

# 1. Вызов метода с одним аргументом
manager.process_table()

# 2. Вызов метода с двумя аргументами
manager.process_with_var("v1")