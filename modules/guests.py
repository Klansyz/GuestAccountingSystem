import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from utils import setup_window, execute_query
from config import DB_PATH


# Загрузка данных гостей из базы данных
def load_guests(tree, search_query=""):
    try:
        # Базовый SQL-запрос
        query = """
        SELECT * FROM Guests
        WHERE guest_id LIKE ? OR last_name LIKE ? OR first_name LIKE ? OR middle_name LIKE ? 
              OR phone LIKE ? OR email LIKE ? OR passport LIKE ?
        ORDER BY guest_id DESC
        """

        params = tuple(f"%{search_query}%" for _ in range(7))
        rows = execute_query(DB_PATH, query, params)

        for row in tree.get_children():
            tree.delete(row)

        for row in rows:
            tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить данные гостей: {e}")


# Добавление нового гостя
def add_guest(tree):
    def save_guest():
        guest_data = {
            "last_name": entry_last_name.get(),
            "first_name": entry_first_name.get(),
            "middle_name": entry_middle_name.get(),
            "phone": entry_phone.get(),
            "email": entry_email.get(),
            "passport": entry_passport.get(),
        }

        if not guest_data["last_name"] or not guest_data["first_name"]:
            messagebox.showwarning("Предупреждение", "Имя и фамилия обязательны для заполнения!")
            return

        try:
            query = '''
                INSERT INTO Guests (last_name, first_name, middle_name, phone, email, passport)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = tuple(guest_data.values())
            execute_query(DB_PATH, query, params)

            messagebox.showinfo("Успех", "Гость добавлен!")
            add_window.destroy()
            load_guests(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить гостя: {e}")

    # Окно добавления гостя
    add_window = tk.Toplevel()
    add_window.title("Добавить гостя")
    add_window.transient(guest_window)
    add_window.resizable(False, False)
    setup_window(add_window, "Добавить гостя", 400, 500)

    def on_close_add_window():
        add_window.destroy()

    add_window.protocol("WM_DELETE_WINDOW", on_close_add_window)

    # Поля ввода
    tk.Label(add_window, text="Фамилия:", font=("Arial", 14)).pack(pady=5)
    entry_last_name = tk.Entry(add_window, font=("Arial", 14))
    entry_last_name.pack()

    tk.Label(add_window, text="Имя:", font=("Arial", 14)).pack(pady=5)
    entry_first_name = tk.Entry(add_window, font=("Arial", 14))
    entry_first_name.pack()

    tk.Label(add_window, text="Отчество:", font=("Arial", 14)).pack(pady=5)
    entry_middle_name = tk.Entry(add_window, font=("Arial", 14))
    entry_middle_name.pack()

    tk.Label(add_window, text="Телефон:", font=("Arial", 14)).pack(pady=5)
    entry_phone = tk.Entry(add_window, font=("Arial", 14))
    entry_phone.pack()

    tk.Label(add_window, text="Email:", font=("Arial", 14)).pack(pady=5)
    entry_email = tk.Entry(add_window, font=("Arial", 14))
    entry_email.pack()

    tk.Label(add_window, text="Паспорт:", font=("Arial", 14)).pack(pady=5)
    entry_passport = tk.Entry(add_window, font=("Arial", 14))
    entry_passport.pack()

    tk.Button(add_window, text="Сохранить", font=("Arial", 14), command=save_guest).pack(pady=20)


# Удаление гостя
def delete_guest(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите гостя для удаления!")
        return

    guest_id = tree.item(selected_item)["values"][0]

    try:
        # Проверка
        query = "SELECT COUNT(*) FROM Bookings WHERE guest_id = ?"
        result = execute_query(DB_PATH, query, (guest_id,))
        count_bookings = result[0][0]  # Количество бронирований для данного гостя

        if count_bookings > 0:
            messagebox.showwarning("Ошибка", "Невозможно удалить гостя, так как у него есть брони!")
            return

        confirmation = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить этого гостя?")
        if confirmation:
            query = "DELETE FROM Guests WHERE guest_id = ?"
            execute_query(DB_PATH, query, (guest_id,))
            messagebox.showinfo("Успех", "Гость удален!")
            load_guests(tree)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить гостя: {e}")


# Редактирование данных гостя
def edit_guest(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите гостя для редактирования!")
        return

    guest_data = tree.item(selected_item)["values"]

    def save_changes():
        updated_data = {
            "last_name": entry_last_name.get(),
            "first_name": entry_first_name.get(),
            "middle_name": entry_middle_name.get(),
            "phone": entry_phone.get(),
            "email": entry_email.get(),
            "passport": entry_passport.get(),
        }

        if not updated_data["last_name"] or not updated_data["first_name"]:
            messagebox.showwarning("Предупреждение", "Имя и фамилия обязательны для заполнения!")
            return

        guest_id = guest_data[0]

        try:
            query = '''
                UPDATE Guests
                SET last_name = ?, first_name = ?, middle_name = ?, phone = ?, email = ?, passport = ?
                WHERE guest_id = ?
            '''
            params = tuple(updated_data.values()) + (guest_id,)
            execute_query(DB_PATH, query, params)

            messagebox.showinfo("Успех", "Данные гостя обновлены!")
            edit_window.destroy()
            load_guests(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные гостя: {e}")

    edit_window = tk.Toplevel()
    edit_window.title("Редактировать гостя")
    edit_window.transient(guest_window)
    edit_window.resizable(False, False)
    setup_window(edit_window, "Редактировать гостя", 400, 500)

    def on_close_edit_window():
        edit_window.destroy()

    edit_window.protocol("WM_DELETE_WINDOW", on_close_edit_window)

    tk.Label(edit_window, text="Фамилия:", font=("Arial", 14)).pack(pady=5)
    entry_last_name = tk.Entry(edit_window, font=("Arial", 14))
    entry_last_name.insert(0, guest_data[1])
    entry_last_name.pack()

    tk.Label(edit_window, text="Имя:", font=("Arial", 14)).pack(pady=5)
    entry_first_name = tk.Entry(edit_window, font=("Arial", 14))
    entry_first_name.insert(0, guest_data[2])
    entry_first_name.pack()

    tk.Label(edit_window, text="Отчество:", font=("Arial", 14)).pack(pady=5)
    entry_middle_name = tk.Entry(edit_window, font=("Arial", 14))
    entry_middle_name.insert(0, guest_data[3])
    entry_middle_name.pack()

    tk.Label(edit_window, text="Телефон:", font=("Arial", 14)).pack(pady=5)
    entry_phone = tk.Entry(edit_window, font=("Arial", 14))
    entry_phone.insert(0, guest_data[4])
    entry_phone.pack()

    tk.Label(edit_window, text="Email:", font=("Arial", 14)).pack(pady=5)
    entry_email = tk.Entry(edit_window, font=("Arial", 14))
    entry_email.insert(0, guest_data[5])
    entry_email.pack()

    tk.Label(edit_window, text="Паспорт:", font=("Arial", 14)).pack(pady=5)
    entry_passport = tk.Entry(edit_window, font=("Arial", 14))
    entry_passport.insert(0, guest_data[6])
    entry_passport.pack()

    tk.Button(edit_window, text="Сохранить изменения", font=("Arial", 14), command=save_changes).pack(pady=20)


# Копирование данных гостя
def copy_guest(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите гостя для копирования данных!")
        return

    guest_data = tree.item(selected_item)["values"]

    # В строку
    clipboard_text = f"Фамилия: {guest_data[1]}\n" \
                     f"Имя: {guest_data[2]}\n" \
                     f"Отчество: {guest_data[3]}\n" \
                     f"Телефон: {guest_data[4]}\n" \
                     f"Email: {guest_data[5]}\n" \
                     f"Паспорт: {guest_data[6]}"

    # Буфер обмена
    pyperclip.copy(clipboard_text)

    messagebox.showinfo("Успех", "Данные скопированы в буфер обмена!")


# Поиск гостей в базе данных
# def search_guests(tree, search_query):
#     load_guests(tree, search_query)


# Интерфейс управления гостями
def open_guest_management(root):
    root.withdraw()

    global guest_window
    guest_window = tk.Toplevel()
    setup_window(guest_window, "Управление гостями", 1000, 600)

    tk.Label(guest_window, text="Управление гостями", font=("Arial", 20, "bold")).pack(pady=20)

    def on_close():
        guest_window.destroy()
        root.deiconify()

    guest_window.protocol("WM_DELETE_WINDOW", on_close)

    columns = ("ID", "Фамилия", "Имя", "Отчество", "Телефон", "Email", "Паспорт")
    tree = ttk.Treeview(guest_window, columns=columns, show="headings", height=15)

    for col in columns:
        if col == "ID":
            tree.column(col, width=40)  # 4 символа
        elif col in ["Фамилия", "Имя", "Отчество"]:
            tree.column(col, width=120)  # 10
        elif col == "Телефон":
            tree.column(col, width=160)  # 20
        elif col == "Email":
            tree.column(col, width=280)  # 35
        elif col == "Паспорт":
            tree.column(col, width=120)  # 15
        else:
            tree.column(col, width=130)  # По умолчанию
        tree.heading(col, text=col)

    scrollbar = ttk.Scrollbar(guest_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(pady=20, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(guest_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Добавить гостя", font=("Arial", 14),
              command=lambda: add_guest(tree)).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Удалить гостя", font=("Arial", 14),
              command=lambda: delete_guest(tree)).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Редактировать гостя", font=("Arial", 14),
              command=lambda: edit_guest(tree)).grid(row=0, column=2, padx=10)
    tk.Button(button_frame, text="Копировать", font=("Arial", 14),
              command=lambda: copy_guest(tree)).grid(row=0, column=3, padx=10)

    search_frame = tk.Frame(guest_window)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Поиск:", font=("Arial", 14)).grid(row=0, column=0, padx=10)

    search_entry = tk.Entry(search_frame, font=("Arial", 14))
    search_entry.grid(row=0, column=1, padx=10)

    # Событие, которое срабатывает при каждом изменении текста в поле ввода
    def on_search_change(event): # event обязателен
        search_query = search_entry.get()
        load_guests(tree, search_query)

    search_entry.bind("<KeyRelease>", on_search_change)  # Привязываем событие к изменению текста

    load_guests(tree)
