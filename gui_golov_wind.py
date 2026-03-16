from PyQt6.QtWidgets import QDialog, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QCheckBox, QHBoxLayout, QFrame
from PyQt6.QtWidgets import QMenuBar, QToolBar, QTabWidget, QWidgetAction  
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon
from ldap3 import Server, Connection, ALL, SAFE_SYNC, SUBTREE, SIMPLE
from ldap3.core.exceptions import LDAPException, LDAPBindError 
from controller import Controller 
from check_functions import instead_path_create_meipass
from registr_error import logger_main_conn, logger_configfile_conn
import os
import sys
import yaml
from constants import *

class LoginWindow(QDialog):
    def __init__(self):      #  метод-КОНСТРУКТОР, автоматически вызываемый при создании нового экземпляра класса
        super().__init__()   # используется внутри метода __init__ дочернего класса для вызова конструктора родительского класса
        self.setWindowTitle("Вхід в Registrat")     # устанавливает текст в заголовке окна
        self.resize(width, height)   # Оптимальний розмір для вікна логіна з файлу  constants
        layout = QVBoxLayout()      # создает вертикал контейнер, який автоматично выстраивает кнопки, метки, поля ввода сверху вниз в один столбец
        self.sproba_vhody = 0     # Це для кількості невдалих спроб введення паролю при логуванні
        self.dict_user_permis = {}  # словник який я використ в методі authenticate_ad, для подальшої передачі його в функцію main()
        self.dozvol_group_vhody = None  # передаю цей аргумент в клас UserConnectionInfobar, щоб вивести групу корист на екран в верхню стрічку
        self.full_name = None   # Фаміл Імя Отчество, яке передаємо на вивід у клас UserConnectInfoBar
        self.user_input = QLineEdit()  #   создание виджета однострочного текстового поля для ЛОГИНА
        self.user_input.setMinimumHeight(30)  # Встановлює висоту 40 пікселів для поля воду логина
        self.current_user = os.getenv('USERNAME')  # Отримуємо логін з системи Windows
        self.user_input.setText(self.current_user)   # Встановлюємо текст та блокуємо редагування
        #self.user_input.setReadOnly(True) 
        self.pass_input = QLineEdit(placeholderText="Пароль") # QLineEdit створює однорядкове поле для введення тексту 
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setMinimumHeight(30)  # Встановлює висоту 30 пікселів для поля воду пароля
        QTimer.singleShot(0, self.pass_input.setFocus)  # Відкладаєм выполнение setFocus на ничтожный срок (0 мс), чтобы Qt успел отрисовать окно
        self.login_btn = QPushButton("Увійти")  # login_btn - змінна, яка зберігає посилання на кнопку "Увійти"
        layout.addWidget(QLabel("Введіть пароль:"))  # создаем текстовую метку і добавляєм її в макет  
        layout.addWidget(self.user_input)    # Добавляєм до контейн layout -  поле вводу логіна
        layout.addWidget(self.pass_input)    # Добавляєм до контейн layout -  поле вводу пароля

        self.show_password = QCheckBox("Показати пароль")    # Створюємо прапорець Checkbox.
        self.show_password.toggled.connect(self.make_password_visibl)  # Когда пользователь нажимает на галочку "Показать пароль", срабатывает сигнал toggled. Он вызывает метод toggle_password_visibility
        layout.addWidget(self.show_password)    # Добавляєм до контейн layout -  элемент Checkbox 
        self.setLayout(layout)  # Керуй розташуванням елементів так, як прописано в цьому макеті layout, тут діє Автоматичне масштабування
        self.login_btn.clicked.connect(self.obrabotcuk_btn_login) # Когда пользователь нажмет на кнопку login_btn, программа должна автоматически выполнить функцию obrabotcuk_btn_login 
        layout.addWidget(self.login_btn)     # Добавляєм до контейн layout -  кнопка  login_btn "Увійти"
    
    def obrabotcuk_btn_login(self):     # Обработчик при нажатии на кнопку  btn_login  "Увійти" звертається до ф-ї authenticate_ad, яка провіряє чи вдала аутентиф
        # Цей метод провіряє чи належить користувач до групи доступу чи ні. Тут реаліз. кількість спроб вводу неправильного паролю 4 рази
        stat_in_AD, stat_this_progr = self.authenticate_ad(self.user_input.text(), self.pass_input.text())  #  self.user_input.text() - получения текста, который пользователь ввел в поле ввода
        if stat_in_AD == True and stat_this_progr == True:  #  Користув  ввійшов в AD і має групу доступу до цієї проги
            self.accept() # закриваємо вікно логування і передаємо сигнал програмі, що авторизація пройшла успішно, і можна відкривати головне вікно.
        elif stat_in_AD == True and stat_this_progr == False:   #  Користув  ввійшов в AD але не має групу доступу до цієї проги
            QMessageBox.critical(self, "Помилка", f"Користувач: {self.user_input.text()} не має доступу до цієї програми. Програма буде закрита.") 
            logger_main_conn.error(f"Користувач: {self.user_input.text()} не має доступу до цієї програми.")   # logger з файлу ragistr_error
            self.reject()  # Закриваємо вікно
        elif stat_in_AD == False and stat_this_progr == True:  #  Користув  ввів неправильно логін/пароль і ми ще не знаємо чи має він якісь групи доступу
            self.sproba_vhody = self.sproba_vhody + 1 
            remaining_sprob = 4 - self.sproba_vhody  
            self.pass_input.clear()    # очищаємо поле вводу неправильного паролю
            self.pass_input.setFocus()    # встановлюємо курсор на поле вводу нового паролю
            if self.sproba_vhody >=4:
                QMessageBox.critical(self, "Помилка", "Перевищено кількість спроб. Програма буде закрита.")
                logger_main_conn.error(f"Перевищено кількість спроб входу для користувача: {self.user_input.text()}")   # logger з файлу ragistr_error
                self.reject()  # Закриваємо вікно
            else:
                QMessageBox.warning(self, "Помилка", f"Невірний логін або пароль. Залишилося спроб: {remaining_sprob}") 
        elif  stat_in_AD == False and stat_this_progr == False:    # Всякі помилки типу недоступний AD server і т. д.
                self.reject()  # Закриваємо вікно
                
    def make_password_visibl(self, checked):  # Або показує пароль або ховає його зірочками
        if checked:
            # Показуємо текст як він є
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)  # QLineEdit.Normal - текст виден и его можно копировать, setEchoMode - Метод, управляет тем, как введенный текст «эхом» (визуально) отражается на экране.
        else: 
            # Приховуємо текст (крапки/зірочки)
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)  # QLineEdit.Password - константа, указывающая, что символы должны быть замаскированы.    

    def authenticate_ad(self, username, password):   # Аутентиф в AD і отримує групи до яких належ користувач і групи-доступу до цієї проги 
       cd = f"ldap://{DOMAIN_CONTROLLERS}" 
       user_dn = f"{domain}\\{username}"
       try:
          server = Server(cd, get_info=ALL)  # створ обєкт сервера
          conn = Connection(server, user=user_dn, password=password, auto_bind=True) #  auto_bind=True - Установить сетевое соединение с сервером і пройти аутентификацию под указанной учеткой 
          if conn.bind():
            users_groups = self.get_users_groups_inAD(username, conn)     # отримуємо всі групи по яких належит даний користув в AD який вже залогінився
            necces_group_for_program = self.get_necces_groups_inAD(WHERE_SEARCH_GROUPS_FOR_THIS_PROGRAM, conn)  # отримуємо всі групи доступу з OU AD  до цієї проги
            self.dozvol_group_vhody = set(users_groups) & set(necces_group_for_program)    #  шукаєм перетин двох множин і буде дозволена група/групи входу
            if self.dozvol_group_vhody:  #  пройшов аутентифікацію в AD і він належить до дозволеної групи входу
                 self.dict_user_permis = {  # тоді визнач його права в прозі,  словник типу : {'bychalt_role': True, 'sklad_role': True, 'admin_role': False, 'operat_role': True}
                   "bychalt_role":   self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "bychalt_role"),
                   "sklad_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "sklad_role"),
                   "admin_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "admin_role"),          # Це карта доступу
                   "zakypiv_role":    self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "zakypiv_role"),
                   "kadru_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "kadru_role"),
                   "prodaz_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "prodaz_role")
                 }
                 zrazok_search = f'(&(objectClass=person)(sAMAccountName={username}))'  # проста f строка
                 conn.search(search_base=WHERE_SEARCH_USER, search_filter = zrazok_search, attributes=['cn'])  #  за логіном шукаємо повне імя cn корист в AD
                 if conn.entries:
                     full_cn_username = conn.entries[0]  # це довгий вивід типу cn=...............  Status ........
                     self.full_name = full_cn_username.cn.value
                     #self.full_name = str( full_cn_username.cn) # Це вже саме Фаміл імя Отчество ne yde na windows 2022 server
                 conn.unbind()
                 return True, True   #   Якщо корист залогінився в AD і корист має доступ до цієї проги 
            elif (users_groups == [] or not self.dozvol_group_vhody):  # користув пройшов аутентифік в AD, але не входить до груп доступу
                 conn.unbind()  #  означает завершение сессии и закрытие соединения с сервером.
                 return True, False  #   Якщо корист залогінився в AD але корист не має доступу до цієї проги
       except LDAPBindError as e:
                 return False, True    # Якщо користувач ввів неправильно логін/пароль
       except LDAPException as e:
               QMessageBox.critical(None, "Error", f"Error LDAP of connection to domain controler: {cd}: {e}")
               logger_main_conn.error(f"Error LDAP of connection to domain controler: {cd}: {e}")   # logger_main_conn з файлу ragistration_error
               return False, False
       except Exception as e:
               QMessageBox.critical(None, "Error", f"Unknown Error of connection to domain controler: {cd}: {e}") 
               logger_main_conn.error(f"Unknown Error of connection to domain controler: {cd}: {e}")   # logger_main_conn з файлу ragistration_error
               return False, False
   
    def get_users_groups_inAD(self, username_tofind, connect):     #  
       #-----------  Отримує з AD для конкретного користувача всі його групи і вертає їх але крім основої групи Domain Users   ------
       #  --------- якщо ж корист належить тільки до Domain Users то вертає []
       search_filter1 = f'(&(objectClass=user)(sAMAccountName={username_tofind}))'  # search_filter1 = (&(objectClass=user)(sAMAccountName=oleg.sheredko))
       connect.search(search_base = WHERE_SEARCH_USER, search_filter = search_filter1, search_scope=SUBTREE, attributes=['memberOf']) 
       if len(connect.entries) == 0:
          return []
       user_entry = connect.entries[0]
       group_dns = user_entry['memberOf'].values
       group_names = []
       for dn in group_dns:
          # Парсинг CN из DN строки (например, 'CN=GroupName,OU=Groups,...')
          cn_part = next(part for part in dn.split(',') if part.startswith('CN='))
          group_name = cn_part.split('=', 1)[1]
          group_names.append(group_name)
       return group_names

    def get_necces_groups_inAD(self, way_to_necces_groups, connect): # отримує групи за шляхом 'OU=publ group,DC=videoservaillance,DC=com' з AD
        # Це та OU в AD де вносять тільки групи потрібні для цієї програми і все            
        # Вертає всі користувацькі групи в list. 
        connect.search(way_to_necces_groups, '(objectclass=group)', search_scope=SUBTREE, attributes='cn')
        if len(connect.entries) > 0:
           list_all_groups = [entry['cn'].value for entry in connect.entries]
           return list_all_groups
        else:
           return []

    def spivpadinja_groups_za_role(self, users_group, role_name):
       if getattr(sys, 'frozen', False):   # запущена программа как обычный скрипт или как замороженный исполняемый файл (собранный через PyInstaller,
          base_path = os.path.dirname(sys.executable)     # Если программа скомпилирована
       else:
          base_path = os.path.dirname(os.path.abspath(__file__))   # Если запуск из исходного кода де __file__: переменная, содержащая путь к текущему файлу
       config_path = os.path.join(base_path, 'users_roles.yaml')   # Створюєм абсолютный путь к файлу конфигурации 'users_roles.yaml' 
       try:
         with open(config_path, 'r', encoding='utf-8') as f:
            role_of_program = yaml.safe_load(f).get('roles', {})   # читаем файл и превращает его структуру в словарь . safe_load чтобы исключить выполнение произвольного кода из YAML-файла.
            vsi_groupu_za_role = role_of_program.get(role_name, [])  # Если ключ role_name есть в словаре role_of_program, метод вернет соответствующее ему значение.
            return any(group in users_group for group in vsi_groupu_za_role) # перевірка чи є хоча б одна група зі списку vsi_groupu_za_role у списку users_group. 
       except FileNotFoundError:
         msg = QMessageBox(self)
         msg.setIcon(QMessageBox.Icon.Critical)
         msg.setWindowTitle("Помилка")
         msg.setText(f"Файл конфігурації ролей не знайдено за шляхом:\n{config_path}")
         msg.exec()
         logger_configfile_conn.error(f"Файл конфігурації ролей не знайдено за шляхом: {config_path}")   # logger_main_conn з файлу ragistr_error
         sys.exit(1)    # закриваємо саму прогу
       except Exception as e:
         msg = QMessageBox(self)
         msg.setIcon(QMessageBox.Icon.Warning)
         msg.setWindowTitle("Помилка YAML")
         msg.setText(f"Помилка у структурі файлу конфігурації ролей: {e}")
         msg.exec()
         logger_configfile_conn.error(f"Помилка у структурі файлу конфігурації ролей: {e}")   # logger_main_conn з файлу ragistr_error
         sys.exit(1)    # закриваємо саму прогу

class MainWindow(QMainWindow):  # Работает как «сборщик»
    def __init__(self, user_permission, user_group_access, full_username):
        super().__init__()       #   викликає ініціалізацію батьківського класу (QMainWindow)
        self.setWindowTitle("ERP Reestrat")
        self.setMenuBar(UpperMenu(self))  # Встановлюємо верхню строку меню: Файл, Правка, Операции, Сервис
        self.user_conn_info = UserConnectInfoBar(user_group_access, full_username)  #  Виводим строку вгорі екрану де вказано: Корист login авториз до cd01
        self.panel_for_iconimage = QToolBar("Icons Toolbar")   # Створюємо панель для виводу зображень іконок типу: друк, прикріпити
        self.icon_loader = IconsManager(self.panel_for_iconimage, instead_path_create_meipass('icons'))   
       
        central_widget = QWidget()                        # создаем пустой виджет-контейнер, який буде основной рабочей областью окна
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)         #  Создаем главный вертикальный слой для центрального виджета
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.user_conn_info)        #  Добавляем self.user_conn_info наверх (на всю ширину)  
        main_layout.addWidget(self.panel_for_iconimage)   # Добавляем self.panel_for_iconimage под ним (тоже на всю ширину)

        self.hor_layout = QHBoxLayout()                   # Cоздаем новый горизонтальный слой для sidebar, submenu, vkladku_in_mainwind
        self.hor_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(self.hor_layout)       # добавляем hor_layout в основной вертикальный main_layout
        
        self.sidebar = SidebarBase(user_permission)   # створюємо лівостороню бокову панель  з кнопками
        self.submenu = SubmenuBase()   # створюємо підменю від головних кнопок
        self.submenu.hide()            # Початково приховане
        self.vkladku_in_mainwind = QTabWidget()       #  Создает сам виджет - контейнер для вкладок в головному вікні програми
        self.vkladku_in_mainwind.setTabsClosable(True)   # Добавляет на каждую вкладку маленькую иконку крестика (кнопку закрытия). Без этой строки крестиков не будет
        self.vkladku_in_mainwind.tabCloseRequested.connect(lambda index: self.vkladku_in_mainwind.removeTab(index))   #  User  закрыває ненужные страницы кликом по x, завдяки сигналу tabCloseRequested 
              
        self.hor_layout.addWidget(self.sidebar)              #  Добавляем бокову панель sidebar в главный слой
        self.hor_layout.addWidget(self.submenu)              #  Добавляем  саме підменю яке походить від Продажі, Склад, закупки і т. д.
        self.hor_layout.addWidget(self.vkladku_in_mainwind)  #  Добавляем вкладки які утворюються після натискання на submenu
        self.controller = Controller(self)       #  Cтворюєм новий обєкт класса Controller, передавая йому обєкт MainWindow, щоб контрол керував вікном MainWindow

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

class UpperMenu(QMenuBar):    # Створюємо строку меню, та що в горі: Файл, Правка, Операции, Сервис 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addMenu("Файл")
        self.addMenu("Правка")
        self.addMenu("Операции")
        self.addMenu("Сервис")
        self.setFixedHeight(25)
       
class SidebarBase(QFrame):   #  Створює лівостор. бокову панель Sidebar з кнопками
    def __init__(self, permissions):
        super().__init__()
        self.setFixedWidth(170)  
        self.setStyleSheet("background-color: #2c3e50;")   
        layout = QVBoxLayout(self)  # Створення вертикал макету всередині панелі
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  
        self.btn_sales     = QPushButton(f"💰 {NAME_BUTTONS['Sales']}")   # Кнопки навігації 
        self.btn_purchases = QPushButton(f"🛒 {NAME_BUTTONS['Purchases']}")
        self.btn_stock     = QPushButton(f"📦 {NAME_BUTTONS['Stock']}")
        self.btn_person    = QPushButton(f"👥 {NAME_BUTTONS['Person']}")
        self.btn_salary    = QPushButton(f"💰 {NAME_BUTTONS['Salary']}")
        self.btn_reports   = QPushButton(f"📊 {NAME_BUTTONS['Reports']}")
        self.btn_settings  = QPushButton(f"⚙️ {NAME_BUTTONS['Settings']}")
        self.btn_admin     = QPushButton(f"⚙️ {NAME_BUTTONS['Admin']}")
        self.btn_exit      = QPushButton(f"🚪 {NAME_BUTTONS['Exit']}")
        # Мапа відповідності: кнопка -> роль з файлу users_roles, яка її бачить
        all_buttons = [               # Список кортежів .  ATTENTION!  Незабудь внести зміни ще й у def authenticate_ad в класі LoginWindow   
            (self.btn_sales,     permissions.get('bychalt_role')  or permissions.get('admin_role')                                                                                                                 or permissions.get('prodaz_role')),
            (self.btn_purchases,                                     permissions.get('admin_role')                                                                           or permissions.get('zakypiv_role')),
            (self.btn_stock,                                         permissions.get('admin_role')  or permissions.get('sklad_role')),
            (self.btn_person,    permissions.get('bychalt_role')  or permissions.get('admin_role')                                     or permissions.get('kadru_role')),
            (self.btn_salary,    permissions.get('bychalt_role')  or permissions.get('admin_role')                                     or permissions.get('kadru_role')), 
            (self.btn_reports,   permissions.get('bychalt_role')  or permissions.get('admin_role')  or permissions.get('sklad_role')                                                                               or permissions.get('prodaz_role')),
            (self.btn_settings,                                      permissions.get('admin_role')), 
            (self.btn_admin,                                         permissions.get('admin_role')),
            (self.btn_exit,      permissions.get('bychalt_role')  or permissions.get('admin_role')  or permissions.get('sklad_role')   or permissions.get('kadru_role')     or permissions.get('zakypiv_role')    or permissions.get('prodaz_role')) ]
        for btn, access in all_buttons:     # Налаштовуємо та додаємо тільки дозволені кнопки
            if access:
                btn.setCheckable(True)
                btn.setAutoExclusive(True)   # При нажатии одной кнопки остальные автоматически отжимаются
                btn.setStyleSheet(SidebarButtonStyle.COMMON)  # застосовуємо стиль взятий з класу  SidebarButtonStyle
                layout.addWidget(btn)
            else:
                btn.deleteLater()   # Якщо доступу немає, видаляємо об'єкт, щоб не займав пам'ять
        layout.addStretch()        

class UserConnectInfoBar(QLabel):    # Виводить строку вгорі екрану де вказано: Корист login авториз до cd01 
    def __init__(self, user_group_acc, full_username):   # parent=None,
        super().__init__()                 # parent
        self.user_group = user_group_acc
        self.full_username = full_username 
        #self.username = os.environ.get('USERNAME', 'Користувач')     # Отримуємо дані
        server = os.environ.get('LOGONSERVER', 'local').lstrip('\\')  # Windows вертае LOGONSERVER с двумя слешами в начале lstrip превращает это в чистое имя 
        self.setText(f"Користувач: <b>{self.full_username}</b> авторизований на: \"{server}\" належить до: {self.user_group}")   # Налаштовуємо текст та зовнішній вигляд
        self.setFixedHeight(25) 
        self.setStyleSheet("""
            background-color: #e1e1e1; 
            padding-left: 10px; 
            margin: 0px;               
            border-bottom: 1px solid #999;
            font-size: 11px;
            color: #333;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter)   # Вирівнюємо вміст віджету строго по центру як по гориз чтак і по вертикалі

class IconsManager: # Виводить рядок зображень-іконок типу: друк, прикріпити, кошик, видалити під рядком інфа про користувача
    def __init__(self, toolbar, folder_path):
        self.toolbar = toolbar
        self.folder_path = folder_path  # шлях до папки де лежать іконки-зображення
        self.load_icons()
        
    def load_icons(self):     
        if not os.path.exists(self.folder_path):    # Перевіряємо, чи існує папка
            return
        self.toolbar.setIconSize(QSize(30, 30))     # Налаштування розміру іконок у тулбарі
        for file_name in os.listdir(self.folder_path):  #  возвращает список имен всех файлов и подпапок, находящихся по пути self.folder_path.
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.ico')):
                icon_path = os.path.join(self.folder_path, file_name)  # Обєднуємо шлях до  папки з імям файлу іконки
                action = QAction(QIcon(icon_path), file_name, self.toolbar)  # инициализуемо кнопку с иконкой (QIcon(icon_path)), текстовой подписью (file_name) и привязывает её к панели инструментов (self.toolbar)
                self.toolbar.addAction(action)   # Додаємо дію на панель інструментів 
               
class SubmenuBase(QFrame):    # Створює підменю від головного лівостронього toolbar c копками
    def __init__(self, parent=None):
        super().__init__()
        self.setObjectName("SubmenuPanel")
        self.setFixedWidth(190)
        self.setStyleSheet(SubmenuStyle.PANEL)  # за стиль відповідає окремий клас  SubmenuStyle
        self.layout = QVBoxLayout(self)     # Головний макет
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)   # Всі віджети будуть липнути до верху
        self.hide_left_btn = QPushButton("◀ Сховати")   # Кнопка закриття (ховання вліво)
        self.hide_left_btn.setStyleSheet("background: #bdc3c7; border: none; padding: 5px;")
        self.layout.addWidget(self.hide_left_btn)  #  Добавить кнопку hide_left_btn в макет (layout) текущего окна или виджета
        self.buttons = []        #  это инициализация пустого списка (list), це кнопки підменю
        self.sub_buttons = []   # кнопки під-підменю
        self.create_dynamic_submenu([])  # методу передается пустой список в качестве аргумента, для інициализациї «чистого» меню без пунктов.
    
    def create_dynamic_submenu(self, dict_name_btns_submenu):    #  На вхід приймає словник за категор. типу: Назва_кнопки_підменю: Назва_класу_що_її_обробляє
        #      {'Залишки товарів': 'ZalushTovary', 'Переміщення': 'Peremichena', 'Інвентаризація': 'Inventariz',  'Списання': 'Spusanja', 'Оприбуткування': 'Oprubytkyv',           
        for btn in self.buttons:            # Очистка старих кнопок підменю
            self.layout.removeWidget(btn)   #  Видаляє кожну кнопку з макета (layout.removeWidget) 
            btn.deleteLater()               #  повністю знищує об'єкт кнопки з пам'яті (deleteLater
        self.buttons = []                   #  Обнуляє список self.buttons = [], щоб він був порожнім
        self.clear_sub_menu()   # викликаємо метод по очищенню під-під меню
        for item in dict_name_btns_submenu:       #  Проходимся по: Залишки товарів,  Переміщення, Інвентаризація, Списання, ...
            btn = QPushButton(item)         #  Для кожного елемента створює нову кнопку QPushButton 
            btn.setCheckable(True)          #  одночасно може бути натиснута лише одна кнопка
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, b=btn: self.create_nested_submenu(b)) # При клике вызываем функцию создания вложенного подменю
            self.layout.addWidget(btn)      #  Додає нові кнопки у макет вікна
            self.buttons.append(btn)
   
    def create_nested_submenu(self, clicked_button):
        self.clear_sub_menu()   # викликаємо метод по очищенню під-під меню
        if not clicked_button.isChecked():             # Якщо кнопку щойно вимкнули (зняли чек), просто виходимо після очищення
           return
        index = self.layout.indexOf(clicked_button)    # Знаходимо, де в списку макета знаходиться натиснута кнопка
         
        #parent_name = clicked_button.text()    # 3. Отримуємо дані з БД для цієї кнопки
        #nested_items = self.get_data_from_sql(parent_name)
        nested_items = ['подменю1', 'подменю2', 'подменю3']
        # 4. Вставляємо нові кнопки ОДНУ ЗА ОДНОЮ під натиснуту кнопку
        for i, item_text in enumerate(nested_items):
           sub_btn = QPushButton(f"   ↳ {item_text}") # Візуальний відступ
           sub_btn.setStyleSheet("background-color: #f0f0f0; margin-left: 20px;") # Стиль для підменю
           self.layout.insertWidget(index + 1 + i, sub_btn) # Вставляємо в макет за індексом: index + 1, index + 2 і т.д.
           self.sub_buttons.append(sub_btn) 
        
    def clear_sub_menu(self):  #  метод для очищення під-під меню
        while self.sub_buttons:
           btn_to_remove = self.sub_buttons.pop() # Витягуємо кнопку зі списку
           self.layout.removeWidget(btn_to_remove) # Прибираємо з макета
           btn_to_remove.setParent(None)           # "Відв'язуємо" від вікна
           btn_to_remove.deleteLater()             # Повністю видаляємо з пам'яті
        self.sub_buttons.clear()  

       
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

