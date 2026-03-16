# changes made 16:40
#changes made in 17:05 by me
# from web oblako made 18:19
import sys, os
from PyQt6.QtWidgets import QApplication, QDialog
from gui_golov_wind import LoginWindow, MainWindow
def main():
    # Установка атрибута масштабирования
    app = QApplication(sys.argv)  # создаем главный объект приложения, инициализируя среду Qt. Она необходима для запуска графического интерфейса, управления событиями и обработки аргументов командной строки,
    login_wind = LoginWindow()  # создаем новый объект класса LoginWindow и присваивает его переменной login_wind
    if login_wind.exec() == QDialog.DialogCode.Accepted:  #  открываем модальное диалоговое окно login_wind, приостанавливает выполнение кода, пока user не закроет его, и проверяет, нажал ли он «ОК» . Если login закрыт через "ОК", код внутри блока if выполняется
        user_perms =  login_wind.dict_user_permis   # беремо з класу LoginWindow словник dict_user_permis 
        full_us_nam = login_wind.full_name       # беремо з класу LoginWindow Фаміл Імя Отчество
        user_gr_acc = login_wind.dozvol_group_vhody # беремо з класу LoginWindow з якою групою доступу користувач зайшов в прогу
        window = MainWindow(user_permission = user_perms, user_group_access = user_gr_acc, full_username = full_us_nam)  # словник dict_user_permis передаємо на MainWindow
        window.showMaximized() # Головне вікно на весь екран
        sys.exit(app.exec())  #  запускаем главный цикл обработки событий графического интерфейса (app.exec_()) и, после закрытия окна, корректно завершает работу приложения

if __name__ == "__main__":  # это проверка, запускается ли скрипт напрямую (как основной файл) или импортируется как модуль. Код внутри блока выполняется только при прямом запуске
  main()

