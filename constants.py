import os
sql_server = 'listreestr'  # this is name of listener of availability group, consists from two replics sqlserv03, sqlserv04
database = 'vpn_serv01' 
DOMAIN_CONTROLLERS = 'cd01.videoservaillance.com'
domain = "VIDEOSERV"
kilk_cds = len(DOMAIN_CONTROLLERS)

SUBMENU_FILE = 'submenu_buttons.json'   #  файл використ в класі Controller в методах: def load_name_btns_from_json, def save_name_btns_in_json

WHERE_SEARCH_USER = 'DC=videoservaillance,DC=com'
WHERE_SEARCH_GROUPS_FOR_THIS_PROGRAM = 'OU=reestrat groups,OU=groups for specprograms,DC=videoservaillance,DC=com'  # спец OU де є групи тільки для цієї проги

gener_kilk_sprob_enter = 4  # загальна кількість невдалих спроб логування доменим користувачем
failed_sproba_enter = 0

width = 300   # задаємо ширину і висоту вікна логування 
height = 200  # задаємо ширину і висоту вікна логування

NAME_BUTTONS = {       # словник для зберігання: key, icon, ukr_name, список roles
    "Sales":     ("📈", "Продажі", ['bychalt_role', 'admin_role', 'prodaz_role']),
    "Purchases": ("🛒", "Закупівлі", ['admin_role', 'zakypiv_role']),
    "Stock":     ("📦", "Склад", ['admin_role', 'sklad_role']),
    "Person":    ("👥", "Персонал", ['bychalt_role', 'admin_role', 'kadru_role']),
    "Salary":    ("💰", "Зарплата", ['bychalt_role', 'admin_role', 'kadru_role']),
    "Reports":   ("📊", "Звіти", ['bychalt_role', 'admin_role', 'sklad_role', 'prodaz_role']),
    "Struct":    ("📁", "Структура", ['admin_role']),
    "Settings":  ("⚙️", "Налаштування", ['admin_role']),
    "Admin":     ("🛡️", "Адміністратору", ['admin_role']),
    "Exit":      ("🚪", "Вихід", ['bychalt_role', 'admin_role', 'sklad_role', 'kadru_role', 'zakypiv_role', 'prodaz_role'])
}
Schema = 'hardware'
Table_category = f"{Schema}.Categories"   # Повна назва таблиці зі схемою
Table_main_product = f"{Schema}.Products"
Table_tag = f"{Schema}.Tag_detail"
Table_translate = f"{Schema}.Transl_stovpci"
Table_translate2 = f"{Schema}.Transl_stovpci2"

Schema2 = 'inventory'
Table_typepoint = f"{Schema2}.Type_points"
Table_skladu = f"{Schema2}.Skladu"

File_conf_roles = 'users_roles.yaml'