STOCK_STYLE = """
            QMainWindow { background-color: #f4f4f9; }
            QLabel { font-size: 14px; color: #333; font-weight: bold; }
            QLineEdit, QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; background: white; }
            QPushButton { background-color: #a0b5ca; color: black; padding: 10px; font-weight: bold; border-radius: 4px; }    /* по умолчанию */
            QPushButton:pressed { background-color: #717f8e;color: black; }       /* при нажатии */
            QPushButton:hover { background-color: #8d9eb0; }                     /* при наведении */
            QTableWidget { background-color: white; border: 1px solid #ddd; }
        """
#  Дві перших строки напаши на початку файлу, куди ти будеш вставляти стилі
# from PyQt6.QtWidgets import QApplication
# from style import STOCK_STYLE
# QApplication.instance().setStyleSheet(STOCK_STYLE)  а це вже напишеш в клас в def _init_ui(self): в якому буде цей стиль