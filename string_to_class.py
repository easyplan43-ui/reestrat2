#    Це  Словник-фабрика, конфіг файл дає відповідність між рядком і назвою класом (самими класами) взятими з файлу  submenu_classes
#   без цього файлу в класі Controller() в методі def add_tab(self) вираз  new_tab = real_class_to_submenubtn() давав помилку
from submenu_stock_classes import ZalushTovary, InsertTovar, Peremichena
from submenu_admin_classes import InsNewSklad, InsNewAgent
from submenu_struct_classes import SkladandMarket, Contragents
from PyQt6.QtWidgets import QLabel
Str_to_classname = {     
   "ZalushTovary"  : ZalushTovary,
   "Peremichena"   : Peremichena,
   "InsertTovar"   : InsertTovar,
   "InsNewSklad"   : InsNewSklad,
   "InsNewAgent"   : InsNewAgent, 
   "SkladandMarket": SkladandMarket,
   "Contragents"   : Contragents,
    "QLabel": QLabel  # Якщо використовуєте QLabel як заглушку
}