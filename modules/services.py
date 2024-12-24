import tkinter as tk
from tkinter import ttk, messagebox
from utils import setup_window, execute_query
from config import DB_PATH


# Загрузка услуг
def load_services(tree, search_query=""):
    try:
        query = """
            SELECT 
                s.service_id, 
                s.service_name, 
                s.price, 
                s.description, 
                s.service_type, 
                s.availability
            FROM Services s
        """
        if search_query:
            query += """
                WHERE CAST(s.service_name AS TEXT) LIKE ? 
                   OR CAST(s.price AS TEXT) LIKE ? 
                   OR CAST(s.description AS TEXT) LIKE ?
                   OR CAST(s.service_type AS TEXT) LIKE ?
                   OR CAST(s.availability AS TEXT) LIKE ?
            """
            params = ('%' + search_query + '%',) * 5
        else:
            params = ()

        # Запрос
        rows = execute_query(DB_PATH, query, params)

        for row in tree.get_children():
            tree.delete(row)

        for row in rows:
            tree.insert("", "end", values=row)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить данные услуг: {e}")


# Добавление новой услуги
def add_service(tree):
    def save_service():
        service_data = {
            "service_name": entry_service_name.get(),
            "price": entry_price.get(),
            "description": entry_description.get("1.0", "end-1c"),  # Получаем текст из поля Text!!
            "service_type": service_type_var.get(),
            "availability": availability_var.get()
        }

        if not service_data["service_name"] or not service_data["price"]:
            messagebox.showwarning("Предупреждение", "Все поля обязательны для заполнения!")
            return

        if not service_data["price"].replace('.', '', 1).isdigit():
            messagebox.showwarning("Ошибка", "Цена должна быть числом!")
            return

        try:
            query = '''
                INSERT INTO Services (service_name, price, description, service_type, availability)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (
                service_data["service_name"],
                float(service_data["price"]),
                service_data["description"],
                service_data["service_type"],
                service_data["availability"]
            )
            execute_query(DB_PATH, query, params)

            messagebox.showinfo("Успех", "Услуга добавлена!")
            add_window.destroy()
            load_services(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить услугу: {e}")

    add_window = tk.Toplevel()
    add_window.title("Добавить услугу")
    add_window.transient(service_window)
    add_window.resizable(False, False)
    setup_window(add_window, "Добавить услугу", 400, 600)

    def on_close_add_window():
        add_window.destroy()

    add_window.protocol("WM_DELETE_WINDOW", on_close_add_window)

    # Поля ввода
    tk.Label(add_window, text="Название услуги:", font=("Arial", 14)).pack(pady=5)
    entry_service_name = tk.Entry(add_window, font=("Arial", 14))
    entry_service_name.pack()

    tk.Label(add_window, text="Цена:", font=("Arial", 14)).pack(pady=5)
    entry_price = tk.Entry(add_window, font=("Arial", 14))
    entry_price.pack()

    tk.Label(add_window, text="Описание услуги:", font=("Arial", 14)).pack(pady=5)
    entry_description = tk.Text(add_window, font=("Arial", 14), height=6, width=30)
    entry_description.pack(pady=5)

    # Выпадающий список
    tk.Label(add_window, text="Тип услуги:", font=("Arial", 14)).pack(pady=5)
    service_type_var = tk.StringVar(value="Разовая")
    service_type_options = ["Разовая", "Ежедневная"]
    service_type_menu = ttk.Combobox(add_window, textvariable=service_type_var, values=service_type_options, font=("Arial", 14), state="readonly")
    service_type_menu.pack(pady=5)

    # Флажок для доступности
    tk.Label(add_window, text="Доступность:", font=("Arial", 14)).pack(pady=5)
    availability_var = tk.BooleanVar(value=True)
    availability_check = tk.Checkbutton(add_window, text="Доступна", variable=availability_var)
    availability_check.pack(pady=5)

    tk.Button(add_window, text="Сохранить", font=("Arial", 14), command=save_service).pack(pady=20)


# Удаление услуги
def delete_service(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите услугу для удаления!")
        return

    service_id = tree.item(selected_item)["values"][0]

    try:
        # Проверяем в актуальных бронях
        query_check = """
            SELECT COUNT(*) 
            FROM Booking_Services bs
            JOIN Bookings b ON bs.booking_id = b.booking_id
            WHERE bs.service_id = ? AND b.status IN ('Забронировано', 'Проживание', 'Выполнено', 'Отменено')
        """
        result = execute_query(DB_PATH, query_check, (service_id,))
        if result[0][0] > 0:
            messagebox.showwarning(
                "Удаление невозможно",
                "Эта услуга используется в бронях и не может быть удалена."
            )
            return

        # Подтверждение удаления
        confirmation = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить эту услугу?")
        if confirmation:
            query_delete = "DELETE FROM Services WHERE service_id = ?"
            execute_query(DB_PATH, query_delete, (service_id,))
            messagebox.showinfo("Успех", "Услуга удалена!")
            load_services(tree)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить услугу: {e}")


# Редактирование услуги
def edit_service(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите услугу для редактирования!")
        return

    service_data = tree.item(selected_item)["values"]

    def save_changes():
        updated_data = {
            "service_name": entry_service_name.get(),
            "price": entry_price.get(),
            "description": entry_description.get("1.0", "end-1c"),
            "service_type": service_type_var.get(),
            "availability": availability_var.get()
        }

        if not updated_data["service_name"] or not updated_data["price"]:
            messagebox.showwarning("Предупреждение", "Все поля обязательны для заполнения!")
            return

        if not updated_data["price"].replace('.', '', 1).isdigit():
            messagebox.showwarning("Ошибка", "Цена должна быть числом!")
            return

        try:
            # Обновление данных услуги
            query = '''
                UPDATE Services
                SET service_name = ?, price = ?, description = ?, service_type = ?, availability = ?
                WHERE service_id = ?
            '''
            params = (
                updated_data["service_name"],
                float(updated_data["price"]),
                updated_data["description"],
                updated_data["service_type"],
                updated_data["availability"],
                service_data[0]  # service_id
            )
            execute_query(DB_PATH, query, params)

            # Если доступность изменилась на недоступно
            if not updated_data["availability"]:
                delete_query = '''
                    DELETE FROM Booking_Services
                    WHERE service_id = ? AND booking_id IN (
                        SELECT booking_id
                        FROM Bookings
                    )
                '''
                execute_query(DB_PATH, delete_query, (service_data[0],))
                messagebox.showinfo(
                    "Информация",
                    "Услуга стала недоступной и была удалена из всех актуальных броней."
                )

            messagebox.showinfo("Успех", "Данные услуги обновлены!")
            edit_window.destroy()
            load_services(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить услугу: {e}")

    edit_window = tk.Toplevel()
    edit_window.title("Редактировать услугу")
    edit_window.transient(service_window)
    edit_window.resizable(False, False)
    setup_window(edit_window, "Редактировать услугу", 400, 600)

    def on_close_edit_window():
        edit_window.destroy()

    edit_window.protocol("WM_DELETE_WINDOW", on_close_edit_window)

    # Поля ввода
    tk.Label(edit_window, text="Название услуги:", font=("Arial", 14)).pack(pady=5)
    entry_service_name = tk.Entry(edit_window, font=("Arial", 14))
    entry_service_name.insert(0, service_data[1])  # service_name
    entry_service_name.pack()

    tk.Label(edit_window, text="Цена:", font=("Arial", 14)).pack(pady=5)
    entry_price = tk.Entry(edit_window, font=("Arial", 14))
    entry_price.insert(0, service_data[2])
    entry_price.pack()

    tk.Label(edit_window, text="Описание услуги:", font=("Arial", 14)).pack(pady=5)
    entry_description = tk.Text(edit_window, font=("Arial", 14), height=6, width=30)  # Многострочное поле
    entry_description.insert("1.0", service_data[3])
    entry_description.pack(pady=5)

    # Выпадающий список
    tk.Label(edit_window, text="Тип услуги:", font=("Arial", 14)).pack(pady=5)
    service_type_var = tk.StringVar(value=service_data[4])  # Значение типа услуги
    service_type_options = ["Разовая", "Ежедневная"]
    service_type_menu = ttk.Combobox(edit_window, textvariable=service_type_var, values=service_type_options, font=("Arial", 14), state="readonly")
    service_type_menu.pack(pady=5)

    # Флажок
    tk.Label(edit_window, text="Доступность:", font=("Arial", 14)).pack(pady=5)
    availability_var = tk.BooleanVar(value=service_data[5] == 1)  # Если доступность = 1, то True
    availability_check = tk.Checkbutton(edit_window, text="Доступна", variable=availability_var)
    availability_check.pack(pady=5)

    tk.Button(edit_window, text="Сохранить изменения", font=("Arial", 14), command=save_changes).pack(pady=20)


# Интерфейс управления услугами
def open_service_management(root):
    root.withdraw()

    global service_window
    service_window = tk.Toplevel()
    setup_window(service_window, "Управление услугами", 1000, 600)

    tk.Label(service_window, text="Управление услугами", font=("Arial", 20, "bold")).pack(pady=20)

    def on_close():
        service_window.destroy()
        root.deiconify()

    service_window.protocol("WM_DELETE_WINDOW", on_close)

    columns = ("ID", "Название услуги", "Цена, руб.", "Описание", "Тип услуги", "Доступность")
    tree = ttk.Treeview(service_window, columns=columns, show="headings", height=15)

    tree.column("ID", width=30, anchor="center")  # (~5 символов)
    tree.column("Название услуги", width=100)
    tree.column("Цена, руб.", width=50)
    tree.column("Описание", width=400)
    tree.column("Тип услуги", width=100)
    tree.column("Доступность", width=100)

    for col in columns:
        tree.heading(col, text=col)

    scrollbar = ttk.Scrollbar(service_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(pady=20, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(service_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Добавить услугу", font=("Arial", 14),
              command=lambda: add_service(tree)).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Удалить услугу", font=("Arial", 14),
              command=lambda: delete_service(tree)).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Редактировать услугу", font=("Arial", 14),
              command=lambda: edit_service(tree)).grid(row=0, column=2, padx=10)

    search_frame = tk.Frame(service_window)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Поиск:", font=("Arial", 14)).grid(row=0, column=0, padx=10)
    search_entry = tk.Entry(search_frame, font=("Arial", 14))
    search_entry.grid(row=0, column=1, padx=10)

    def on_search_change(event):
        search_query = search_entry.get()
        load_services(tree, search_query)

    search_entry.bind("<KeyRelease>", on_search_change)

    load_services(tree)
