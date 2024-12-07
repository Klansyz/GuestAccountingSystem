import tkinter as tk
from tkinter import messagebox
from modules.guests import open_guest_management  # Импортируем модуль управления гостями
from modules.rooms import open_room_management
from modules.bookings import open_booking_management
from modules.services import open_service_management
from modules.bills import open_bill_management
from utils import execute_query, setup_window
from config import DB_PATH


# Функция для проверки логина/пароля
def check_admin_login(login, password):
    query = "SELECT * FROM Admins WHERE login = ? AND password = ?"
    result = execute_query(DB_PATH, query, (login, password))
    return result[0] if result else None


# Функция для обработки входа
def login(event=None):
    login_value = entry_login.get()
    password_value = entry_password.get()

    # Проверяем логин и пароль через базу данных
    admin = check_admin_login(login_value, password_value)

    if admin:
        admin_name = f"{admin[1]} {admin[2]}"  # Получаем имя администратора из БД
        messagebox.showinfo("Успех", f"Добро пожаловать, {admin_name}!")
        login_window.destroy()  # Закрываем окно входа
        open_main_menu(admin_name)  # Передаем имя администратора в главное меню
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль!")


# Главное меню
def open_main_menu(admin_name):
    global root
    root = tk.Tk()
    setup_window(root, "Панель администратора", 1000, 700)

    # Заголовок
    label_title = tk.Label(root, text="Панель управления отелем", font=("Arial", 24, "bold"))
    label_title.pack(pady=30)

    # Информация о текущем пользователе
    label_admin_name = tk.Label(root, text=f"Администратор: {admin_name}", font=("Arial", 14))
    label_admin_name.pack(pady=10)

    # Основное меню (кнопки)
    frame_menu = tk.Frame(root)
    frame_menu.pack(pady=30)

    # Создание кнопок
    font_size = ("Arial", 18, "bold")  # Увеличенный шрифт

    btn_guests = tk.Button(frame_menu, text="Гости", command=lambda: open_guest_management(root), font=font_size,
                           width=30, height=3)
    btn_rooms = tk.Button(frame_menu, text="Номера", command=lambda: open_room_management(root), font=font_size,
                          width=30, height=3)
    btn_services = tk.Button(frame_menu, text="Услуги", command=lambda: open_service_management(root), font=font_size,
                             width=30, height=3)
    btn_bills = tk.Button(frame_menu, text="Счета", command=lambda: open_bill_management(root), font=font_size,
                          width=30, height=3)
    btn_bookings = tk.Button(frame_menu, text="Бронирования", command=lambda: open_booking_management(root),
                             font=font_size,
                             width=69, height=3)  # Ширина на всю ширину двух колонок

    # Размещение кнопок в сетке
    btn_guests.grid(row=0, column=0, padx=30, pady=20)
    btn_rooms.grid(row=0, column=1, padx=30, pady=20)
    btn_services.grid(row=1, column=0, padx=30, pady=20)
    btn_bills.grid(row=1, column=1, padx=30, pady=20)
    btn_bookings.grid(row=2, column=0, columnspan=2, padx=30, pady=20)  # Растянутая кнопка

    # Кнопка выхода
    btn_logout = tk.Button(root, text="Выйти", command=logout, font=font_size, width=30, height=3)
    btn_logout.pack(pady=5)

    root.mainloop()


# Функция для выхода в окно авторизации
def logout():
    root.destroy()  # Закрываем главное меню
    open_login_window()  # Открываем окно входа


# Окно входа
def open_login_window():
    global login_window, entry_login, entry_password
    login_window = tk.Tk()
    setup_window(login_window, "Вход администратора", 500, 350)

    # Заголовок
    label_login = tk.Label(login_window, text="Авторизация", font=("Arial", 20, "bold"))
    label_login.pack(pady=20)

    # Поля ввода
    frame_inputs = tk.Frame(login_window)
    frame_inputs.pack(pady=10)

    label_user = tk.Label(frame_inputs, text="Логин:", font=("Arial", 14))
    label_user.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    entry_login = tk.Entry(frame_inputs, font=("Arial", 14))
    entry_login.grid(row=0, column=1, padx=10, pady=10)

    label_password = tk.Label(frame_inputs, text="Пароль:", font=("Arial", 14))
    label_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    entry_password = tk.Entry(frame_inputs, font=("Arial", 14), show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=10)

    # Кнопка входа
    btn_login = tk.Button(login_window, text="Войти", command=login, font=("Arial", 14), width=15, height=1)
    btn_login.pack(pady=5)

    # Привязываем событие нажатия клавиши Enter к функции login()
    login_window.bind('<Return>', login)

    # Запуск окна входа
    login_window.mainloop()


# Запуск окна входа
open_login_window()
