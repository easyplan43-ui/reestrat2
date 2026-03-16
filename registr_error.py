import logging   # Використ для запису помилок зєднання в файл використовую для вявлення основних
import os        # зєднання з AD і з бд і ще забагато спроб вводу неправ паролю
import sys
from logging.handlers import RotatingFileHandler   # обмеження по розміру файлу логування 
      # Визначаємо шлях до папки, де знаходиться сам .exe (або .py)
if getattr(sys, 'frozen', False): # провіряєм чи є спец атрибут від упаковщика pyinstaller, if yes return true, чи является ли запущенный файл «замороженным» (EXE-шником).
    application_path = os.path.dirname(sys.executable)      # Якщо запущено як EXE, беремо полный путь к самому .exe файлу, отсекает имя файла и оставляет только путь к папке.
else:
    application_path = os.path.dirname(os.path.abspath(__file__))   # Якщо запущено як скрипт .py,  __file__: Специальная переменная, содержащая путь к текущему .py файлу.
log_file = os.path.join(application_path, 'app_errors.log')  # создает полный путь к файлу логов, объединяя папку приложения с именем файла
# Настройка через handlers позволяет использовать RotatingFileHandler внутри basicConfig
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[ RotatingFileHandler('app_errors.log', maxBytes=10*1024*1024, backupCount=1, encoding='utf-8')]  # 10 МБ (размер одного файла), Хранить 1 старых файла (+ 1 текущий)
)

logger_main_conn = logging.getLogger("LogCheckMainConn")    # Беремо екземпляр логера для логув помилок щодо головного зєднання
logger_db_conn = logging.getLogger("LogCheckDBConn")    # Беремо екземпляр логера для логув помилок зєднання з бд
logger_configfile_conn = logging.getLogger("LogCheckConfFileConn")    # Беремо екземпляр логера для логув помилок зєднання з конфіг файлами: json, yaml

# Щоб використати в самому коді при перевірці пиши: logger_configfile_conn.error(f"Файл формування підменю не знайдено за шляхом:\n{config_path}") 