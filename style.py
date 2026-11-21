#  Як використати! Дві перших строки напаши на початку файлу, куди ти будеш вставляти стилі
# from PyQt6.QtWidgets import QApplication
# from style import STOCK_STYLE
# QApplication.instance().setStyleSheet(STOCK_STYLE)  а це вже напишеш в клас в def _init_ui(self): в якому буде цей стиль

# Цей стиль для кнопок, таблиць в меню Склад
STOCK_STYLE = """
            QMainWindow { background-color: #f4f4f9; }
            QLabel { font-size: 14px; color: #333; font-weight: bold; }
            QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; background: white; width: 100px;qproperty-maximumSize: 100px 16777215px;}
            QComboBox { padding: 5px; border: 1px solid #ccc; border-radius: 4px; background: white;}
            QPushButton { background-color: #a0b5ca; color: black; padding: 10px; font-weight: bold; border-radius: 4px; margin-right: 10px;}    /* по умолчанию */
            QPushButton:pressed { background-color: #717f8e;color: black; }       /* при нажатии */
            QPushButton:hover { background-color: #8d9eb0; }                     /* при наведении */
            QTableWidget { background-color: white; border: 1px solid #ddd; }
        """
# Як використати: 1)Оголошення - from style import SidebarButtonStyle; 2) Застоосув -  btn.setStyleSheet(SidebarButtonStyle.COMMON)
class SidebarButtonStyle():  #  Описує тільки стиль, шрифт, розмір, колір лівосторонньої бічної панелі Sidebar з кнопками  
    COMMON = """
        QPushButton {
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 15px;
            text-align: left;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #34495e;
        }
        QPushButton:checked {
            background-color: #3498db;
            font-weight: bold;
        }
    """

class SubmenuStyle:
    PANEL = "background-color: #ecf0f1; border-right: 1px solid #bdc3c7;"
    HEADER = "font-weight: bold; padding: 10px; background-color: #dcdde1;"
    ITEM = """
        QPushButton {
            text-align: left;
            padding: 8px 20px;
            border: none;
            background: transparent;
        }
        QPushButton:hover { background-color: #dcdde1; }
    """

class UserInfoBarStyle: # Стиль для строки вгорі екрану яка виводить інфу про користувача
    USER_INFO_BAR = """
        QLABEL { 
            background-color: #e1e1e1; 
            padding-left: 10px; 
            margin: 0px;               
            border-bottom: 1px solid #999;
            font-size: 11px;
            color: #333;
        }    
        """

