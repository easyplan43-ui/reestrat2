import os
sql_server = 'sqlserv03'  # this is virtual WSFC name, consists from sqlserv03/04
database = 'vpn_serv01' 
DOMAIN_CONTROLLERS = 'cd01.videoservaillance.com'
domain = "VIDEOSERV"
kilk_cds = len(DOMAIN_CONTROLLERS)

SUBMENU_FILE = 'submenu_buttons.json'   #  файл використ в класі Controller в методах: def load_name_btns_from_json, def save_name_btns_in_json

WHERE_SEARCH_USER = 'DC=videoservaillance,DC=com'
WHERE_SEARCH_GROUPS_FOR_THIS_PROGRAM = 'OU=vpnobserv groups,OU=groups for specprograms,DC=videoservaillance,DC=com'  # спец OU де є групи тільки для цієї проги

gener_kilk_sprob_enter = 4  # загальна кількість невдалих спроб логування доменим користувачем
failed_sproba_enter = 0

width = 300   # задаємо ширину і висоту вікна логування 
height = 200  # задаємо ширину і висоту вікна логування

NAME_BUTTONS = {       # словник для зберігання даних у форматі «ключ: значення»
    "Sales":     "Продажі",
    "Purchases": "Закупівлі",
    "Stock":     "Склад",
    "Person":  "Персонал",
    "Salary":    "Зарплата",
    "Reports":   "Звіти",
    "Settings":  "Налаштування",
    "Admin":     "Адміністратору",
    "Exit":      "Вихід"
}
Schema = 'hardware'
Table_category = f"{Schema}.Categories"   # Повна назва таблиці зі схемою
Table_main_product = f"{Schema}.Products"
Table_tag = f"{Schema}.Tag_detail"
Table_translate = f"{Schema}.Transl_stovpci"