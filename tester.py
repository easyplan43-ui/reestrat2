import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout

class VupadSpusokManager(QWidget):
    changed = pyqtSignal(object) 
    def __init__(self, peredana_func, default_item, parent=None):
        super().__init__(parent) 
        self.peredana_func = peredana_func      
        self.default_item = default_item 
        self.layout = QHBoxLayout(self)
        self.vupad_spusok = QComboBox()
        self.layout.addWidget(self.vupad_spusok)
        self.add_items()
        self.vupad_spusok.currentIndexChanged.connect(self._handle_change)   

    def _handle_change(self):  
        data = self.vupad_spusok.currentData()  
        self.changed.emit(data) 

    def add_items(self, *args):   
        self.vupad_spusok.blockSignals(True)  
        self.vupad_spusok.clear()   
        self.vupad_spusok.addItem(self.default_item, None)  # додаєм рядок підказку  
        
        # Виправлена безпечна логіка виклику через try-except
        try:
            data_list = self.peredana_func(*args)  # значення які вертає функція
        except TypeError:
            # Якщо функція очікує аргументи, які ще не передали — просто виходимо
            self.vupad_spusok.blockSignals(False)
            return
            
        if data_list: 
             for item in data_list:
                try:
                    if len(item) > 1:         
                        name = str(item[1])   
                    else:
                        name = str(item[0])
                except:
                    name = str(item)   
                self.vupad_spusok.addItem(name, list(item)) # додаємо новий рядок текст, прих дані
        self.vupad_spusok.blockSignals(False)  

    def get_curr_data(self): 
        return self.vupad_spusok.currentData()  

    def get_curr_string(self): 
        return self.vupad_spusok.currentText()

    def get_curr_index(self): 
        return self.vupad_spusok.currentIndex()

def type_tochok(): # Функція, яка повертає типи точок
    # Імітуємо реальні рядки з бази даних (ID, Назва українською, системний код)
    return [
        (1, "Головний Склад", "main_warehouse"),
        (2, "Роздрібний Магазин", "retail_shop"),     # список кортежів
        (3, "Транзитний Пункт", "transit_point"),
        (4, "Аварійний Резерв", "backup_stock")
    ]

class PracticeWindow(QMainWindow):  # ГОЛОВНЕ ВІКНО ДЛЯ ПРАКТИКИ
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Практика з VupadSpusokManager")
        self.resize(400, 200)

        # Створюємо головний віджет та вертикальний макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.info_label = QLabel("Тут звявиться інфо про вибір")
        self.main_layout.addWidget(self.info_label)
       
        self.manager_spusky = VupadSpusokManager(type_tochok, "Оберіть тип точки111")   # СТВОРЮЄМО ЕКЗЕМПЛЯР ВАШОГО МЕНЕДЖЕРА
        self.main_layout.addWidget(self.manager_spusky) # ОБОВ'ЯЗКОВО: Додаємо менеджер у макет вікна
        # підключаємо сигнал 
        self.manager_spusky.changed.connect(self.pokazatu_rezultat_vyboru) # connect - це звязок від сигналу до функції pokazatu_rezultat_vyboru
   
    def pokazatu_rezultat_vyboru(self, data):
        if self.manager_spusky.get_curr_index() == 0:    # Перевіряємо індекс (якщо 0 — обрано дефолтну підказку)
           self.info_label.setText("Ти скинув вибір. Обери реальну точку.")
           return
        text = self.manager_spusky.get_curr_string()

        # Оскільки data — це прихований list(item) з БД, ми можемо витягти будь-яке поле!
        db_id = data[0]         # Перший елемент кортежу (ID)
        ukr_name = data[1]      # Другий елемент (Назва)
        eng_name = data[2]      # Третій елемент (Код)
        text_for_user = ( f"<b>Ви обрали:</b>{text}"
                          f"ID в базі: {db_id}<br>"
                          f"Назва: {ukr_name}<br>"
                          f"English: {eng_name}"
                        )
        self.info_label.setText(text_for_user) # друкуємо текст
        
if __name__ == "__main__": 
    app = QApplication(sys.argv) #  ініціалізує графічну систему вашого комп'ютера
    window = PracticeWindow()
    window.show()
    sys.exit(app.exec()) # Запуск вічного циклу подій
    
