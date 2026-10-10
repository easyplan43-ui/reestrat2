from PyQt6.QtWidgets import QDialog, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout, QFrame
from PyQt6.QtWidgets import QMenuBar, QToolBar, QTabWidget, QFormLayout  
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM
from ldap3.core.exceptions import LDAPException, LDAPBindError 
from controller import Controller 
from dodat_classes import CheckBoxManager, DialogWindow
from check_functions import instead_path_create_meipass
from registr_error import logger_main_conn, logger_configfile_conn
import os
import sys
import yaml
from style import SidebarButtonStyle, SubmenuStyle, UserInfoBarStyle
from constants import *
from conn_to_db import *
from string_to_class import *
class LoginWindow(QDialog):
    def __init__(self):      #  метод-КОНСТРУКТОР, автоматически вызываемый при создании нового экземпляра класса
        super().__init__()   # используется внутри метода __init__ дочернего класса для вызова конструктора родительского класса
        self.setWindowTitle("Вхід в Registrat")     # устанавливает текст в заголовке окна
        self.resize(width, height)   # Оптимальний розмір для вікна логіна з файлу  constants
        layout = QFormLayout()      # Инициализируем форму вводу
        self.sproba_vhody = 0     # Це для кількості невдалих спроб введення паролю при логуванні
        self.dict_user_permis = {}  # словник який я використ в методі authenticate_ad, для подальшої передачі його в функцію main()
        self.dozvol_group_vhody = None  # передаю цей аргумент в клас UserConnectionInfobar, щоб вивести групу корист на екран в верхню стрічку
        self.full_name = None   # Фаміл Імя Отчество, яке передаємо на вивід у клас UserConnectInfoBar
        
        self.user_input = QLineEdit()  #   создание виджета однострочного текстового поля для ЛОГИНА
        self.user_input.setMinimumHeight(30)  # Встановлює висоту 40 пікселів для поля воду логина
        self.current_user = os.getenv('USERNAME')  # Отримуємо логін з системи Windows
        self.user_input.setText(self.current_user)   # Встановлюємо текст та блокуємо редагування
        #self.user_input.setReadOnly(True) 
        
        self.pass_input = QLineEdit() # QLineEdit створює однорядкове поле для введення паролю
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)  # перетвор букви в зірочки
        self.pass_input.setMinimumHeight(30)  # Встановлює висоту 30 пікселів для поля воду пароля
        
        self.login_btn = QPushButton("Увійти")  # login_btn - змінна, яка зберігає посилання на кнопку "Увійти"

        self.ekzemp_prap_show_pass =  CheckBoxManager("Показати пароль", checked_default = False)  # створ екземпляр класу по роботі із прапорцями
        
        layout.addRow("Введіть логін:", self.user_input) # створ текстову мітку "Введіть логін:" і звязує її із полем вводу self.user_input
        layout.addRow("Введіть пароль:", self.pass_input)
        layout.addRow(self.ekzemp_prap_show_pass)
        layout.addRow(self.login_btn)                #  размещает кнопку на экране
        
        QTimer.singleShot(0, self.pass_input.setFocus)  # Відкладаєм выполнение setFocus на ничтожный срок (0 мс), чтобы Qt успел отрисовать окно
       
        self.setLayout(layout)  # Керуй розташуванням елементів так, як прописано в цьому макеті layout, тут діє Автоматичне масштабування
       
        # ----------------------------------------------------- Сигнали --------------------------------------------------------------------------
        self.login_btn.clicked.connect(self.obrabotcuk_btn_login) # Когда пользователь нажмет на кнопку login_btn, программа должна автоматически выполнить функцию obrabotcuk_btn_login 
        self.ekzemp_prap_show_pass.toggled.connect(self.make_password_visibl)  # Когда пользователь нажимает на галочку "Показать пароль", срабатывает сигнал toggled. Он вызывает метод make_password_visibl
            
    def obrabotcuk_btn_login(self):     # Обработчик при нажатии на кнопку  btn_login  "Увійти" звертається до ф-ї authenticate_ad, яка провіряє чи вдала аутентиф
        username = self.user_input.text()
        password = self.pass_input.text()
        # Цей метод провіряє чи належить користувач до групи доступу чи ні. Тут реаліз. кількість спроб вводу неправильного паролю 4 рази
        stat_in_AD, stat_this_progr = self.authenticate_ad(username, password)  #  
        if stat_in_AD and stat_this_progr:  # Вар-1: Користув  ввійшов в AD і має групу доступу до цієї проги
            self.accept() # закриваємо вікно логування і передаємо сигнал програмі, що авторизація пройшла успішно, і можна відкривати головне вікно.
            return
        if stat_in_AD and not stat_this_progr:   # Вар-2  Користув  ввійшов в AD але не має групу доступу до цієї проги
            QMessageBox.critical(self, "Помилка", f"Користувач: {username} не має доступу до цієї програми. Програма буде закрита.") 
            logger_main_conn.error(f"Користувач: {username} не має доступу до цієї програми.")   # logger з файлу ragistr_error
            self.reject()  # Закриваємо вікно
            return
        if not stat_in_AD and stat_this_progr:  #  Вар-3: Користув  ввів неправильно логін/пароль і ми ще не знаємо чи має він якісь групи доступу
            self.sproba_vhody = self.sproba_vhody + 1 
            self.pass_input.clear()    # очищаємо поле вводу неправильного паролю
            self.pass_input.setFocus()    # встановлюємо курсор на поле вводу нового паролю
            if self.sproba_vhody >=4:
                QMessageBox.critical(self, "Помилка", "Перевищено кількість спроб. Програма буде закрита.")
                logger_main_conn.error(f"Перевищено кількість спроб входу для користувача: {username}")   # logger з файлу ragistr_error
                self.reject()  # Закриваємо вікно
            else:
                remaining_sprob = 4 - self.sproba_vhody
                QMessageBox.warning(self, "Помилка", f"Невірний логін або пароль. Залишилося спроб: {remaining_sprob}") 
            return    
        if not stat_in_AD and not stat_this_progr:    #  Вар-4: Всякі помилки типу недоступний AD server і т. д.
                QMessageBox.critical(self, "Помилка зв'язку", "Не вдалося зв'язатися з сервером Active Directory. Перевірте мережу.")
                logger_main_conn.critical(f"Помилка підключення до AD для користувача: {username}")
                self.reject()  # Закриваємо вікно
                return
                
    def make_password_visibl(self, checked):  # Або показує пароль або ховає його зірочками
        if checked:
            # Показуємо текст як він є
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)  # QLineEdit.Normal - текст виден и его можно копировать, setEchoMode - Метод, управляет тем, как введенный текст «эхом» (визуально) отражается на экране.
        else: 
            # Приховуємо текст (крапки/зірочки)
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)  # QLineEdit.Password - константа, указывающая, что символы должны быть замаскированы.    

    def authenticate_ad(self, username, password):   # Аутентиф в AD, не надсилаючи пароль до cd і отримує групи до яких належ користувач і групи-доступу до цієї проги 
       #  Розкоментуй 3 нижніх рядки якщо ти хочеш щоб тільки юзер який залог в Windows той і зміг зайти в прогу
       #if username.lower() != self.current_user.lower():  # Це умова, що до програми може зайти тільки той юзер який зайшов в Windows
       #   QMessageBox.warning(None, "Увага", "Ви можете авторизуватися лише під своїм обліковим записом Windows!")
       #   return False, False
       if not username or not password:   # Захист від порожніх полів 
           return False, True              # Трактуємо як невірний логін/пароль, тобто тут буде застос 4 спроби входу
       cd = f"ldap://{DOMAIN_CONTROLLERS}" 
       user_dn = f"{domain}\\{username}"
       try:
          server = Server(cd, get_info=ALL)  # створ обєкт сервера
          with Connection(server, user=user_dn, password=password, authentication = NTLM) as conn:  
             #  NTLM - не надсилати пароль від юзера до cd взагалі, а використовувати вбудовані механізмы Windows для безпечної перевірки (хешування)
             if not conn.bind():      # Виконуємо аутентифікацію, якщо пароль невірний, .bind() поверне False без падіння програми
                 return False, True   # Користувач НЕ пройшов автентифікацію в AD, але сервер працює 
             
             users_groups = self.get_users_groups_inAD(username, conn)     # отримуємо всі групи по яких належит даний користув в AD який вже залогінився
             necces_group_for_program = self.get_necces_groups_inAD(WHERE_SEARCH_GROUPS_FOR_THIS_PROGRAM, conn)  # отримуємо всі групи доступу з OU AD  до цієї проги
             self.dozvol_group_vhody = set(users_groups) & set(necces_group_for_program)    #  шукаєм перетин двох множин і буде дозволена група/групи входу
             if self.dozvol_group_vhody:  #  пройшов аутентифікацію в AD і він належить до дозволеної групи входу
                 self.dict_user_permis = {  # тоді визнач його права в прозі,  словник типу : {'bychalt_role': True, 'sklad_role': True, 'admin_role': False, 'operat_role': True}
                   "bychalt_role":   self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "bychalt_role"),
                   "sklad_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "sklad_role"),
                   "admin_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "admin_role"),          # Це карта доступу
                   "zakypiv_role":   self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "zakypiv_role"),
                   "kadru_role":     self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "kadru_role"),
                   "prodaz_role":    self.spivpadinja_groups_za_role(self.dozvol_group_vhody, "prodaz_role")
                 }
                 zrazok_search = f'(&(objectClass=person)(sAMAccountName={username}))'  # проста f строка
                 #  Пошук повного імені (CN) користувача в AD                
                 conn.search(search_base=WHERE_SEARCH_USER, search_filter = zrazok_search, attributes=['cn'])  #  за логіном шукаємо повне імя cn корист в AD
                 if conn.entries:    # Безпечна перевірка: чи знайшли ми користувача в базі пошуку
                     full_cn_username = conn.entries[0]  # це довгий вивід типу cn=...............  Status ........
                     self.full_name = full_cn_username.cn.value  # Безпечне отримання значення для Windows Server 2022
                 else:
                     # Якщо cn не знайдено, ставимо логін як дефолтне ім'я, щоб програма не падала   
                     self.full_name = username 
                 return True, True   #   Якщо корист залогінився в AD і корист має доступ до цієї проги 
             else:      # користув пройшов аутентифік в AD, але не входить до груп доступу
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
       config_path = os.path.join(base_path, File_conf_roles)   # Створюєм абсолютный путь к файлу конфигурации 'users_roles.yaml' 
       try:
         with open(config_path, 'r', encoding='utf-8') as f:
            role_of_program = yaml.safe_load(f).get('roles', {})   # читаем файл и превращает его структуру в словарь . safe_load чтобы исключить выполнение произвольного кода из YAML-файла.
            vsi_groupu_za_role = role_of_program.get(role_name, [])  # Если ключ role_name есть в словаре role_of_program, метод вернет соответствующее ему значение.
            return any(group in users_group for group in vsi_groupu_za_role) # перевірка чи є хоча б одна група зі списку vsi_groupu_za_role у списку users_group. 
       except FileNotFoundError:
         DialogWindow.form_dialog_wind("Помилка", f"Файл конфігурації ролей не знайдено за шляхом:\n{config_path}", QMessageBox.Icon.Critical)
         logger_configfile_conn.error(f"Файл конфігурації ролей не знайдено за шляхом: {config_path}")   # logger_main_conn з файлу ragistr_error
         sys.exit(1)    # закриваємо саму прогу
       except Exception as e:
         DialogWindow.form_dialog_wind("Помилка YAML", f"Помилка у структурі файлу {File_conf_roles} конфігурації ролей: {e}", QMessageBox.Icon.Critical)
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
        self.submenu = SubmenuBase(self)   # створюємо підменю від головних кнопок
        self.submenu.hide()            # Початково приховане
        self.vkladku_in_mainwind = QTabWidget()       #  Создает сам виджет - контейнер для вкладок в головному вікні програми
        self.vkladku_in_mainwind.setTabsClosable(True)   # Добавляет на каждую вкладку маленькую иконку крестика (кнопку закрытия). Без этой строки крестиков не будет
        self.vkladku_in_mainwind.tabCloseRequested.connect(lambda index: self.vkladku_in_mainwind.removeTab(index))   #  User  закрыває ненужные страницы кликом по x, завдяки сигналу tabCloseRequested 
              
        self.hor_layout.addWidget(self.sidebar)              #  Добавляем бокову панель sidebar в главный слой
        self.hor_layout.addWidget(self.submenu)              #  Добавляем  саме підменю яке походить від Продажі, Склад, закупки і т. д.
        self.hor_layout.addWidget(self.vkladku_in_mainwind)  #  Добавляем вкладки які утворюються після натискання на submenu
        self.controller = Controller(self)       #  Cтворюєм новий обєкт класса Controller, передавая йому обєкт MainWindow, щоб контрол керував вікном MainWindow

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
        self.dict_side_btn = {}       # Словник для збереження об'єктів кнопок
        
        for key, (icon, value, roles) in NAME_BUTTONS.items():     # Налаштовуємо та додаємо тільки дозволені кнопки
            access = False  # Початково вважаємо що доступу у корист немає 
            for role in roles: # де role - bychalt_role, admin_role, 
                if permissions.get(role) == True:
                    access = True
                    break # зупиняємо перевірку на доступ бо юзер має доступ до хоча б однієї кнопки
            if access:
                btn = QPushButton(f"{icon} {value}") # створ кнопку за шаблоном
                btn.setCheckable(True)
                btn.setAutoExclusive(True)   # При нажатии одной кнопки остальные автоматически отжимаются
                btn.setStyleSheet(SidebarButtonStyle.COMMON)  # застосовуємо стиль взятий з класу  SidebarButtonStyle
                layout.addWidget(btn)
                self.dict_side_btn[key] = btn # зберігаємо у словник для майбутнього доступу
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
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter)   # Вирівнюємо вміст віджету строго по центру як по гориз чтак і по вертикалі
        self.setStyleSheet(UserInfoBarStyle.USER_INFO_BAR)   # Застосовуємо стиль який виражений окремим класом

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
               
class SubmenuBase(QFrame):    # Створює підменю від головного лівостронього toolbar c кнопками
    def __init__(self, main_window):
        super().__init__()
        self.main_wind = main_window
        self.setObjectName("SubmenuPanel")
        self.setFixedWidth(190)
        self.setStyleSheet(SubmenuStyle.PANEL)  # за стиль відповідає окремий клас  SubmenuStyle
        self.layout = QVBoxLayout(self)     # Головний макет
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)   # Всі віджети будуть липнути до верху
        self.hide_left_btn = QPushButton("◀ Сховати")   # Кнопка закриття (ховання вліво)
        self.hide_left_btn.setStyleSheet("background: #bdc3c7; border: none; padding: 5px;")
        self.layout.addWidget(self.hide_left_btn)  #  Добавить кнопку hide_left_btn в макет (layout) текущего окна или виджета
        self.buttons = []        #  это инициализация пустого списка (list), це кнопки підменю
                   
    def create_dynamic_submenu(self, dict_name_btns_submenu):    #  На вхід приймає словник за категор. типу: Назва_кнопки_підменю: Назва_класу_що_її_обробляє
        #  {'Залишки товарів': 'ZalushTovary', 'Переміщення': 'Peremichena', 'Інвентаризація': 'Inventariz',  'Списання': 'Spusanja', 'Оприбуткування': 'Oprubytkyv',           
        for btn in self.buttons:            # Очистка старих кнопок підменю
            self.layout.removeWidget(btn)   #  Видаляє кожну кнопку з макета (layout.removeWidget) 
            btn.deleteLater()               #  повністю знищує об'єкт кнопки з пам'яті (deleteLater
        self.buttons = []                   #  Обнуляє список self.buttons = [], щоб він був порожнім
        for nazva_menu, nazva_classy in dict_name_btns_submenu.items():       #  Проходимся по: Залишки товарів,  Переміщення, Інвентаризація, Списання, ...
            btn = QPushButton(nazva_menu)         #  Для кожного елемента створює нову кнопку QPushButton 
            btn.setCheckable(True)          #  одночасно може бути натиснута лише одна кнопка
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, nazva_classy=nazva_classy: self.add_tab(nazva_classy))  # Передаємо назву класу
            self.layout.addWidget(btn)      #  Додає нові кнопки у макет вікна
            self.buttons.append(btn)
   
    def add_tab(self, nazva_classy):              # Добавляє вкладки в основ робочу область, но предотвращает открытие нескольких одинаковых окон
        # Отримуємо об'єкт кнопки, яка викликала цей метод
        sub_btn = self.sender()   # Отримуємо об'єкт кнопки, яка викликала цей метод
        btn_text = sub_btn.text()   #  определяем текст кнопки submenu, на которую нажал пользователь, наприклад  - Особисті картки
        for i in range(self.main_wind.vkladku_in_mainwind.count()):         #  Пробегаем по всем уже открытым вкладкам
            if self.main_wind.vkladku_in_mainwind.tabText(i) == btn_text:   # Если вкладка с таким названием уже существует
                self.main_wind.vkladku_in_mainwind.setCurrentIndex(i)       # Программа просто переключается на неё (setCurrentIndex) и прекращает выполнение метода, чтобы не открывать копию
                return
        real_class_to_submenubtn = Str_to_classname.get(nazva_classy)   # Шукаємо реальний клас у нашому словнику з файлу string_to_class
        if real_class_to_submenubtn == QLabel:                     #  Если такой вкладки нет
            new_tab = QLabel(f"Контент для {btn_text}")       #  создается новый виджет метка QLabel
            new_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)    #  Встановлюємо вирівнювання вмісту всередині віджета new_tab по центру
        else:
            new_tab = real_class_to_submenubtn() # Создаем экземпляр класу class_to_submenubtn, тобто відкриваємо вкладку
        self.main_wind.vkladku_in_mainwind.addTab(new_tab, btn_text)   # Додає віджет new_tab як нову вкладку до контейнера. Текст на самому «ярлику» вкладки буде взято зі змінної btn_text
        self.main_wind.vkladku_in_mainwind.setCurrentWidget(new_tab)  # Робить цю нову вкладку активною, щоб користувач відразу побачив її вміст після створення       
         
