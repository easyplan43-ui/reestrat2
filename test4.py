class Variab:
    def __init__(self, name_table, id):
        self.name_table = name_table
        self.id = id

    def meth1(self):
        # Метод вже має доступ до self.name_table, передавати його не треба
        print(f"Працюю з таблицею: {self.name_table}")

    def meth2(self, new_id):
        # Тут ми передаємо додатковий аргумент new_id
        print(f"Старий id: {self.id}, Новий id: {new_id}")

# В іншому класі або місці коду:
obj = Variab("table4", 1) # Створюємо екземпляр
obj.meth1()               # Виклик без аргументів (візьме "table4" з init)
obj.meth2(4)              # Виклик з одним аргументом (id)