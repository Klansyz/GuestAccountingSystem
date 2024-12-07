import sqlite3
import tkinter as tk
import re
from config import DB_PATH


def setup_window(window, title, width, height, resizable=False):
    """
    Настраивает окно: устанавливает заголовок, размеры, центрирует его на экране и задаёт возможность изменения размеров.

    Args:
        window: объект окна Tkinter (tk.Tk или tk.Toplevel).
        title: заголовок окна.
        width: ширина окна.
        height: высота окна.
        resizable: флаг, разрешать ли изменять размер окна (по умолчанию False).
    """
    # Устанавливаем заголовок окна
    window.title(title)

    # Устанавливаем возможность изменения размера
    window.resizable(resizable, resizable)

    # Центрируем окно
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def execute_query(db_path, query, params=None):
    try:
        conn = sqlite3.connect(db_path)

        # Включение проверки внешних ключей
        conn.execute("PRAGMA foreign_keys = ON;")

        cursor = conn.cursor()

        # Выполнение запроса
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = cursor.fetchall()
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка выполнения запроса: {e}")
        result = None
    finally:
        conn.close()

    return result


# Функция для добавления точки в нужный момент
def format_date_input(event, entry):
    date_text = entry.get()

    # Убираем все символы, кроме цифр
    date_text = re.sub(r'\D', '', date_text)

    # Разбиваем строку на части
    if len(date_text) > 2:
        date_text = date_text[:2] + '.' + date_text[2:]
    if len(date_text) > 5:
        date_text = date_text[:5] + '.' + date_text[5:]

    # Обновляем поле ввода с отформатированным текстом
    entry.delete(0, tk.END)
    entry.insert(0, date_text)


# Функция для проверки и форматирования даты
def validate_date(date_string):
    # Проверяем, что дата в формате ДД.ММ.ГГГГ
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_string):
        return True
    return False


# Загружает список гостей из базы данных. Для добавления и изменения броней.
def load_guests():
    query = '''
    SELECT guest_id, last_name || ' ' || first_name AS full_name FROM Guests
    '''
    results = execute_query(DB_PATH, query)
    return [f"{row[0]} - {row[1]}" for row in results]


# Загружает список доступных комнат из базы данных. Для добавления и изменения броней.
def load_rooms():
    query = '''
    SELECT room_number, room_type 
    FROM Rooms
    WHERE availability = 1 -- Только доступные номера
    '''
    results = execute_query(DB_PATH, query)
    return [f"{row[0]} - {row[1]}" for row in results]