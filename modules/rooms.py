import tkinter as tk
from tkinter import ttk, messagebox
from utils import setup_window, execute_query
from config import DB_PATH


# Загрузка данных номеров из базы данных
def load_rooms(tree, search_query=""):
    try:
        query = "SELECT * FROM Rooms"
        if search_query:
            query += f" WHERE room_type LIKE ? OR room_number LIKE ? OR CAST(price AS TEXT) LIKE ?"
            params = ('%' + search_query + '%',) * 3
        else:
            params = ()

        rows = execute_query(DB_PATH, query, params)

        for row in tree.get_children():
            tree.delete(row)

        for row in rows:
            tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить данные номеров: {e}")


# Добавление нового номера
def add_room(tree):
    def save_room():
        room_data = {
            "room_type": entry_room_type.get(),
            "room_number": entry_room_number.get(),
            "price": entry_price.get(),
            "availability": var_availability.get(),
        }

        if not room_data["room_type"] or not room_data["room_number"] or not room_data["price"]:
            messagebox.showwarning("Предупреждение", "Все поля обязательны для заполнения!")
            return

        if not room_data["room_number"].isdigit():
            messagebox.showwarning("Ошибка", "Номер должен быть числом!")
            return

        if not room_data["price"].replace('.', '', 1).isdigit():
            messagebox.showwarning("Ошибка", "Цена должна быть числом!")
            return

        # Проверка на существование такого же номера
        query_check_existing = "SELECT COUNT(*) FROM Rooms WHERE room_number = ?"
        result = execute_query(DB_PATH, query_check_existing,
                               (room_data["room_number"],))
        if result[0][0] > 0:
            messagebox.showwarning("Ошибка", "Номер уже существует!")
            return

        try:
            query = '''
                INSERT INTO Rooms (room_number, room_type, price, availability)
                VALUES (?, ?, ?, ?)
            '''
            params = (room_data["room_number"], room_data["room_type"], float(room_data["price"]),
                      room_data["availability"])
            execute_query(DB_PATH, query, params)

            messagebox.showinfo("Успех", "Номер добавлен!")
            add_window.destroy()
            load_rooms(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить номер: {e}")

    add_window = tk.Toplevel()
    add_window.title("Добавить номер")
    add_window.transient(room_window)
    add_window.resizable(False, False)
    setup_window(add_window, "Добавить номер", 400, 500)

    def on_close_add_window():
        add_window.destroy()

    add_window.protocol("WM_DELETE_WINDOW", on_close_add_window)

    # Поля ввода
    tk.Label(add_window, text="Номер:", font=("Arial", 14)).pack(pady=5)
    entry_room_number = tk.Entry(add_window, font=("Arial", 14))
    entry_room_number.pack()

    tk.Label(add_window, text="Тип номера:", font=("Arial", 14)).pack(pady=5)
    entry_room_type = tk.Entry(add_window, font=("Arial", 14))
    entry_room_type.pack()

    tk.Label(add_window, text="Цена:", font=("Arial", 14)).pack(pady=5)
    entry_price = tk.Entry(add_window, font=("Arial", 14))
    entry_price.pack()

    tk.Label(add_window, text="Доступность:", font=("Arial", 14)).pack(pady=5)
    var_availability = tk.BooleanVar(value=True)
    tk.Checkbutton(add_window, text="Доступен", variable=var_availability).pack()

    tk.Button(add_window, text="Сохранить", font=("Arial", 14), command=save_room).pack(pady=20)


# Удаление номера
def delete_room(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите номер для удаления!")
        return

    room_number = tree.item(selected_item)["values"][0]

    try:
        # Проверка наличия брони для номера
        query = "SELECT COUNT(*) FROM Bookings WHERE room_number = ?"
        result = execute_query(DB_PATH, query, (room_number,))
        count_bookings = result[0][0]  # Получаем количество бронирований для этого номера

        if count_bookings > 0:
            messagebox.showwarning("Ошибка", "Невозможно удалить номер, так как на него есть брони!")
            return

        # Подтверждение удаления номера
        confirmation = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить этот номер?")
        if confirmation:
            query = "DELETE FROM Rooms WHERE room_number = ?"
            execute_query(DB_PATH, query, (room_number,))
            messagebox.showinfo("Успех", "Номер удалён!")
            load_rooms(tree)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить номер: {e}")


# Редактирование номера
def edit_room(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите номер для редактирования!")
        return

    room_data = tree.item(selected_item)["values"]

    # Проверка наличия броней на номер
    room_number = room_data[0]
    query_check_bookings = "SELECT COUNT(*) FROM Bookings WHERE room_number = ?"
    result = execute_query(DB_PATH, query_check_bookings,
                           (room_number,))
    # bookings_exist = result[0][0] > 0  # Есть ли брони на данный номер

    def save_changes():
        updated_data = {
            "room_type": entry_room_type.get(),
            "room_number": entry_room_number.get(),
            "price": entry_price.get(),
            "availability": var_availability.get(),
        }

        if not updated_data["room_type"] or not updated_data["room_number"] or not updated_data["price"]:
            messagebox.showwarning("Предупреждение", "Все поля обязательны для заполнения!")
            return

        if not updated_data["room_number"].isdigit():
            messagebox.showwarning("Ошибка", "Номер должен быть числом!")
            return

        if not updated_data["price"].replace('.', '', 1).isdigit():
            messagebox.showwarning("Ошибка", "Цена должна быть числом!")
            return

        try:
            # Проверка, изменился ли номер комнаты
            new_room_number = updated_data["room_number"]
            if str(room_number) != new_room_number:
                # Если номер изменился, проверяем, существует ли новый номер
                query_check_existing = "SELECT COUNT(*) FROM Rooms WHERE room_number = ?"
                result = execute_query(DB_PATH,
                                       query_check_existing, (new_room_number,))
                if result[0][0] > 0:
                    messagebox.showwarning("Ошибка", "Номер уже существует!")
                    return

                # Обновляем номер в таблице `Rooms` и связанных записях в `Bookings`
                query_update_room_number = "UPDATE Bookings SET room_number = ? WHERE room_number = ?"
                execute_query(DB_PATH,
                              query_update_room_number, (new_room_number, room_number))

            # Обновление данных номера
            query = '''
                UPDATE Rooms
                SET room_type = ?, room_number = ?, price = ?, availability = ?
                WHERE room_number = ?
            '''
            params = (updated_data["room_type"], new_room_number, float(updated_data["price"]),
                      updated_data["availability"], room_number)
            execute_query(DB_PATH, query, params)

            messagebox.showinfo("Успех", "Данные номера обновлены!")
            edit_window.destroy()
            load_rooms(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить номер: {e}")

    # Окно редактирования
    edit_window = tk.Toplevel()
    edit_window.title("Редактировать номер")
    edit_window.transient(room_window)
    edit_window.resizable(False, False)
    setup_window(edit_window, "Редактировать номер", 400, 500)

    def on_close_edit_window():
        edit_window.destroy()

    edit_window.protocol("WM_DELETE_WINDOW", on_close_edit_window)

    # Ввод данных
    tk.Label(edit_window, text="Номер:", font=("Arial", 14)).pack(pady=5)
    entry_room_number = tk.Entry(edit_window, font=("Arial", 14))
    entry_room_number.insert(0, room_data[0])  # Используем room_number
    entry_room_number.pack()

    # Если есть брони, номер комнаты нельзя редактировать
    # if bookings_exist:
    #     entry_room_number.config(state="readonly")

    tk.Label(edit_window, text="Тип номера:", font=("Arial", 14)).pack(pady=5)
    entry_room_type = tk.Entry(edit_window, font=("Arial", 14))
    entry_room_type.insert(0, room_data[1])
    entry_room_type.pack()

    tk.Label(edit_window, text="Цена:", font=("Arial", 14)).pack(pady=5)
    entry_price = tk.Entry(edit_window, font=("Arial", 14))
    entry_price.insert(0, room_data[2])
    entry_price.pack()

    tk.Label(edit_window, text="Доступность:", font=("Arial", 14)).pack(pady=5)
    var_availability = tk.BooleanVar(value=room_data[3])
    tk.Checkbutton(edit_window, text="Доступен", variable=var_availability).pack()

    tk.Button(edit_window, text="Сохранить изменения", font=("Arial", 14), command=save_changes).pack(pady=20)


# Интерфейс управления номерами
def open_room_management(root):
    root.withdraw()

    global room_window
    room_window = tk.Toplevel()
    setup_window(room_window, "Управление номерами", 1000, 600)

    tk.Label(room_window, text="Управление номерами", font=("Arial", 20, "bold")).pack(pady=20)

    def on_close():
        room_window.destroy()
        root.deiconify()

    room_window.protocol("WM_DELETE_WINDOW", on_close)

    # Определяем столбцы
    columns = ("Номер", "Тип номера", "Цена", "Доступность")
    tree = ttk.Treeview(room_window, columns=columns, show="headings", height=15)

    # Настраиваем ширину столбцов
    tree.column("Номер", width=30)          # Узкий столбец для номера
    tree.column("Тип номера", width=70)     # Широкий столбец для типа номера
    tree.column("Цена", width=50)           # Узкий столбец для цены
    tree.column("Доступность", width=150)    # Средний столбец для доступности

    # Настраиваем заголовки
    for col in columns:
        tree.heading(col, text=col)

    # Добавляем вертикальный скроллбар
    scrollbar = ttk.Scrollbar(room_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(pady=20, fill=tk.BOTH, expand=True)

    # Кнопки управления
    button_frame = tk.Frame(room_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Добавить номер", font=("Arial", 14),
              command=lambda: add_room(tree)).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Удалить номер", font=("Arial", 14),
              command=lambda: delete_room(tree)).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Редактировать номер", font=("Arial", 14),
              command=lambda: edit_room(tree)).grid(row=0, column=2, padx=10)

    # Поле поиска
    search_frame = tk.Frame(room_window)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Поиск:", font=("Arial", 14)).grid(row=0, column=0, padx=10)

    search_entry = tk.Entry(search_frame, font=("Arial", 14))
    search_entry.grid(row=0, column=1, padx=10)

    def on_search_change(event):
        search_query = search_entry.get()
        load_rooms(tree, search_query)

    search_entry.bind("<KeyRelease>", on_search_change)

    # Загружаем номера в таблицу
    load_rooms(tree)
