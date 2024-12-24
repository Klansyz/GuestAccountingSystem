import tkinter as tk
from tkinter import ttk, messagebox
from utils import setup_window, execute_query, validate_date, format_date_input, load_guests, load_rooms
from config import DB_PATH


# Загрузка данных броней из базы данных
def load_bookings(tree, search_query=""):
    for row in tree.get_children():
        tree.delete(row)

    query = '''
    SELECT 
        b.booking_id, 
        g.guest_id || ' - ' || g.last_name || ' ' || g.first_name AS guest_info, -- ID гостя и ФИО
        b.room_number || ' - ' || r.room_type AS room_info, -- Номер комнаты и тип
        b.checking_date, 
        b.checkout_date, 
        b.status, 
        b.notes
    FROM Bookings b
    JOIN Guests g ON b.guest_id = g.guest_id
    JOIN Rooms r ON b.room_number = r.room_number
    WHERE 
        guest_info LIKE ? -- Поиск по гостям
        OR room_info LIKE ? -- Поиск по номерам комнат
        OR CAST(b.booking_id AS TEXT) LIKE ?
        OR b.checking_date LIKE ?
        OR b.checkout_date LIKE ?
        OR b.status LIKE ?
        OR b.notes LIKE ?
    ORDER BY b.booking_id DESC
    '''

    params = tuple(f"%{search_query}%" for _ in range(7))

    results = execute_query(DB_PATH, query, params)

    for row in results:
        tree.insert("", "end", values=row)


# Добавление брони
def add_booking(tree):
    def save_booking():
        selected_guest = var_guest.get()
        selected_room = var_room.get()
        if selected_guest and selected_room:
            booking_data = {
                "guest_id": selected_guest.split(" - ")[0],  # guest_id
                "room_number": selected_room.split(" - ")[0],  # room_number
                "checking_date": entry_checking_date.get(),
                "checkout_date": entry_checkout_date.get(),
                "status": var_status.get(),
                "notes": entry_notes.get(),
            }
        else:
            messagebox.showwarning("Предупреждение", "Выберите гостя и номер комнаты!")
            return

        if not booking_data["checking_date"] or not booking_data["checkout_date"]:
            messagebox.showwarning("Предупреждение", "Все поля обязательны для заполнения!")
            return

        # Проверка дат
        if not validate_date(booking_data["checking_date"]) or not validate_date(booking_data["checkout_date"]):
            messagebox.showwarning("Предупреждение", "Дата должна быть в формате ДД.ММ.ГГГГ!")
            return

        try:
            query = '''
                INSERT INTO Bookings (guest_id, room_number, checking_date, checkout_date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (int(booking_data["guest_id"]), int(booking_data["room_number"]),
                      booking_data["checking_date"], booking_data["checkout_date"],
                      booking_data["status"], booking_data["notes"])
            execute_query(DB_PATH, query, params)

            # update_room_availability(booking_data["room_number"])

            messagebox.showinfo("Успех", "Бронь добавлена!")
            add_window.destroy()
            load_bookings(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить бронь: {e}")

    add_window = tk.Toplevel()
    add_window.title("Добавить бронь")
    add_window.transient(booking_window)
    add_window.resizable(False, False)
    setup_window(add_window, "Добавить бронь", 400, 500)

    def on_close_add_window():
        add_window.destroy()

    add_window.protocol("WM_DELETE_WINDOW", on_close_add_window)

    tk.Label(add_window, text="Гость:", font=("Arial", 14)).pack(pady=5)

    # Выпадающий список гостей
    var_guest = tk.StringVar(value="")
    guest_options = load_guests()
    guest_menu = ttk.Combobox(add_window, textvariable=var_guest, values=guest_options, font=("Arial", 14), state="readonly")
    guest_menu.pack()

    tk.Label(add_window, text="Номер:", font=("Arial", 14)).pack(pady=5)

    # Выпадающий список комна
    var_room = tk.StringVar(value="")
    room_options = load_rooms()
    room_menu = ttk.Combobox(add_window, textvariable=var_room, values=room_options, font=("Arial", 14), state="readonly")
    room_menu.pack()

    tk.Label(add_window, text="Дата заезда:", font=("Arial", 14)).pack(pady=5)
    entry_checking_date = tk.Entry(add_window, font=("Arial", 14))
    entry_checking_date.pack()
    entry_checking_date.bind("<KeyRelease>", lambda event, entry=entry_checking_date: format_date_input(event, entry))

    tk.Label(add_window, text="Дата выезда:", font=("Arial", 14)).pack(pady=5)
    entry_checkout_date = tk.Entry(add_window, font=("Arial", 14))
    entry_checkout_date.pack()
    entry_checkout_date.bind("<KeyRelease>", lambda event, entry=entry_checkout_date: format_date_input(event, entry))

    tk.Label(add_window, text="Статус:", font=("Arial", 14)).pack(pady=5)
    var_status = tk.StringVar(value="Забронировано")
    status_options = ["Забронировано", "Проживание", "Выполнено", "Отменено"]

    status_menu = ttk.Combobox(add_window, textvariable=var_status, values=status_options, font=("Arial", 14), state="readonly")
    status_menu.pack()

    tk.Label(add_window, text="Примечания:", font=("Arial", 14)).pack(pady=5)
    entry_notes = tk.Entry(add_window, font=("Arial", 14))
    entry_notes.pack()

    tk.Button(add_window, text="Сохранить", font=("Arial", 14), command=save_booking).pack(pady=20)


# Удаление брони
def delete_booking(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите бронь для удаления!")
        return

    booking_id = tree.item(selected_item)["values"][0]

    confirmation = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить эту бронь?")
    if not confirmation:
        return

    try:
        bills_query = "SELECT bill_id FROM Bills WHERE booking_id = ?"
        bills = execute_query(DB_PATH, bills_query, (booking_id,))

        if bills:  # Если есть связанные счета
            messagebox.showerror(
                "Ошибка",
                "Невозможно удалить бронь: существуют связанные счета."
            )
            return

        # Удаление связанных услуг
        delete_services_query = "DELETE FROM Booking_Services WHERE booking_id = ?"
        execute_query(DB_PATH, delete_services_query, (booking_id,))

        # Удаление самой брони
        delete_booking_query = "DELETE FROM Bookings WHERE booking_id = ?"
        execute_query(DB_PATH, delete_booking_query, (booking_id,))

        messagebox.showinfo("Успех", "Бронь успешно удалена!")
        load_bookings(tree)  # Обновление данных
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить бронь: {e}")


# Редактирование брони
def edit_booking(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Предупреждение", "Выберите бронь для редактирования!")
        return

    booking_data = tree.item(selected_item)["values"]

    def save_changes():
        selected_guest = var_guest.get()
        selected_room = var_room.get()
        if selected_guest and selected_room:
            updated_data = {
                "guest_id": selected_guest.split(" - ")[0],
                "room_number": selected_room.split(" - ")[0],
                "checking_date": entry_checking_date.get(),
                "checkout_date": entry_checkout_date.get(),
                "status": var_status.get(),
                "notes": entry_notes.get(),
            }
        else:
            messagebox.showwarning("Предупреждение", "Выберите гостя и номер комнаты!")
            return

        if not updated_data["checking_date"] or not updated_data["checkout_date"]:
            messagebox.showwarning("Предупреждение", "Все поля обязательны для заполнения!")
            return

        if not validate_date(updated_data["checking_date"]) or not validate_date(updated_data["checkout_date"]):
            messagebox.showwarning("Предупреждение", "Дата должна быть в формате ДД.ММ.ГГГГ!")
            return

        booking_id = booking_data[0]

        try:
            query = '''
                UPDATE Bookings
                SET guest_id = ?, room_number = ?, checking_date = ?, checkout_date = ?, status = ?, notes = ?
                WHERE booking_id = ?
            '''
            params = (
                int(updated_data["guest_id"]),
                int(updated_data["room_number"]),
                updated_data["checking_date"],
                updated_data["checkout_date"],
                updated_data["status"],
                updated_data["notes"],
                booking_id,
            )
            execute_query(DB_PATH, query, params)

            messagebox.showinfo("Успех", "Данные брони обновлены!")
            edit_window.destroy()
            load_bookings(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить бронь: {e}")

    edit_window = tk.Toplevel()
    edit_window.title("Редактировать бронь")
    edit_window.transient(booking_window)
    edit_window.resizable(False, False)
    setup_window(edit_window, "Редактировать бронь", 400, 500)

    def on_close_edit_window():
        edit_window.destroy()

    edit_window.protocol("WM_DELETE_WINDOW", on_close_edit_window)

    # Поля
    tk.Label(edit_window, text="Гость:", font=("Arial", 14)).pack(pady=5)

    guest_id, guest_name = booking_data[1].split(" - ", 1)
    var_guest = tk.StringVar(value=f"{guest_id} - {guest_name}")
    guest_options = load_guests()
    guest_menu = ttk.Combobox(edit_window, textvariable=var_guest, values=guest_options, font=("Arial", 14), state="readonly")
    guest_menu.pack()

    tk.Label(edit_window, text="Номер:", font=("Arial", 14)).pack(pady=5)

    room_number, room_type = booking_data[2].split(" - ", 1)
    var_room = tk.StringVar(value=f"{room_number} - {room_type}")
    room_options = load_rooms()
    room_menu = ttk.Combobox(edit_window, textvariable=var_room, values=room_options, font=("Arial", 14), state="readonly")
    room_menu.pack()

    tk.Label(edit_window, text="Дата заезда:", font=("Arial", 14)).pack(pady=5)
    entry_checking_date = tk.Entry(edit_window, font=("Arial", 14))
    entry_checking_date.insert(0, booking_data[3])
    entry_checking_date.pack()
    entry_checking_date.bind("<KeyRelease>", lambda event, entry=entry_checking_date: format_date_input(event, entry))

    tk.Label(edit_window, text="Дата выезда:", font=("Arial", 14)).pack(pady=5)
    entry_checkout_date = tk.Entry(edit_window, font=("Arial", 14))
    entry_checkout_date.insert(0, booking_data[4])
    entry_checkout_date.pack()
    entry_checkout_date.bind("<KeyRelease>", lambda event, entry=entry_checkout_date: format_date_input(event, entry))

    tk.Label(edit_window, text="Статус:", font=("Arial", 14)).pack(pady=5)
    var_status = tk.StringVar(value=booking_data[5])
    status_options = ["Забронировано", "Проживание", "Выполнено", "Отменено"]
    status_menu = ttk.Combobox(edit_window, textvariable=var_status, values=status_options, font=("Arial", 14), state="readonly")
    status_menu.pack()

    tk.Label(edit_window, text="Примечания:", font=("Arial", 14)).pack(pady=5)
    entry_notes = tk.Entry(edit_window, font=("Arial", 14))
    entry_notes.insert(0, booking_data[6])
    entry_notes.pack()

    tk.Button(edit_window, text="Сохранить изменения", font=("Arial", 14), command=save_changes).pack(pady=20)


# Интерфейс для создания счета
def calculate_bill(tree):
    selected_booking = tree.selection()
    if not selected_booking:
        messagebox.showwarning("Предупреждение", "Выберите бронь для расчета!")
        return

    booking_id, status = tree.item(selected_booking[0], "values")[0:2]

    # Данные о стоимости номера
    query = '''
        SELECT r.price
        FROM Bookings b
        JOIN Rooms r ON b.room_number = r.room_number
        WHERE b.booking_id = ?
    '''
    booking_details = execute_query(DB_PATH, query, (booking_id,))

    if not booking_details:
        messagebox.showerror("Ошибка", "Данные о брони не найдены!")
        return

    price_per_day = booking_details[0][0]

    # Новое окно
    calculate_window = tk.Toplevel()
    calculate_window.transient(booking_window)
    setup_window(calculate_window, "Расчет стоимости", 400, 300)

    tk.Label(calculate_window, text="Количество дней проживания:", font=("Arial", 14)).pack(pady=10)

    days_var = tk.StringVar()
    days_entry = tk.Entry(calculate_window, textvariable=days_var, font=("Arial", 14))
    days_entry.pack(pady=10)

    tk.Label(calculate_window, text=f"Цена за номер в сутки: {price_per_day} ₽", font=("Arial", 14)).pack(pady=10)

    def perform_calculation():
        try:
            days_text = days_var.get()
            if not days_text.isdigit():
                raise ValueError("Введите положительное целое число!")

            days = int(days_text)
            if days <= 0:
                raise ValueError("Количество дней должно быть больше 0!")

            # Расчет стоимости
            room_total = days * price_per_day

            services_query = '''
                SELECT s.service_id, s.price, s.service_type
                FROM Booking_Services bs
                JOIN Services s ON bs.service_id = s.service_id
                WHERE bs.booking_id = ?
            '''
            services = execute_query(DB_PATH, services_query, (booking_id,))
            services_total = 0

            for service_id, service_price, service_type in services:
                if service_type == "Разовая":
                    services_total += service_price
                elif service_type == "Ежедневная":
                    services_total += service_price * days

            total_amount = room_total + services_total

            insert_query = '''
                INSERT INTO Bills (booking_id, total_amount, payment_status)
                VALUES (?, ?, 'Не оплачен')
            '''
            execute_query(DB_PATH, insert_query, (booking_id, total_amount))

            messagebox.showinfo("Успех", f"Счет успешно создан!\nОбщая стоимость: {total_amount} ₽")
            calculate_window.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    tk.Button(calculate_window, text="Рассчитать", font=("Arial", 14), command=perform_calculation).pack(pady=20)

    def on_close_calculate_window():
        calculate_window.destroy()

    calculate_window.protocol("WM_DELETE_WINDOW", on_close_calculate_window)


# Интерфейс управления услугами в брони
def manage_services(tree):
    selected_booking = tree.selection()
    if not selected_booking:
        messagebox.showwarning("Предупреждение", "Выберите бронь для управления услугами!")
        return

    booking_id = tree.item(selected_booking[0], "values")[0]  # ID брони

    def save_service_changes():
        try:
            delete_query = "DELETE FROM Booking_Services WHERE booking_id = ?"
            execute_query(DB_PATH, delete_query, (booking_id,))

            insert_query = "INSERT INTO Booking_Services (booking_id, service_id) VALUES (?, ?)"
            for row_id in services_tree.get_children():
                row_data = services_tree.item(row_id, "values")
                service_id = row_data[0]
                selected = row_data[5] == "✔"

                if selected:
                    execute_query(DB_PATH, insert_query, (booking_id, service_id))

            messagebox.showinfo("Успех", "Изменения успешно сохранены!")
            services_window.destroy()
            load_bookings(tree)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {e}")

    def load_service_data_with_checkbox(search_query=""):
        for row in services_tree.get_children():
            services_tree.delete(row)

        query = '''
            SELECT 
                s.service_id, 
                s.service_name, 
                s.price, 
                s.description, 
                s.service_type, 
                CASE WHEN bs.service_id IS NOT NULL THEN 1 ELSE 0 END AS selected
            FROM Services s
            LEFT JOIN Booking_Services bs ON s.service_id = bs.service_id AND bs.booking_id = ?
            WHERE s.availability = 1 AND s.service_name LIKE ?
        '''
        services = execute_query(DB_PATH, query, (booking_id, f"%{search_query}%"))

        for service in services:
            services_tree.insert("", "end", values=(
                service[0],
                service[1],
                service[2],
                service[3],
                service[4],
                "✔" if service[5] else ""
            ))

    def toggle_checkbox(event):
        selected_item = services_tree.selection()
        if not selected_item:
            return

        item_id = selected_item[0]
        item_values = services_tree.item(item_id, "values")
        current_status = item_values[5]
        new_status = "" if current_status == "✔" else "✔"
        new_values = (*item_values[:5], new_status)
        services_tree.item(item_id, values=new_values)

    # Создание окна
    services_window = tk.Toplevel()
    services_window.transient(booking_window)
    services_window.resizable(False, False)
    setup_window(services_window, "Управление услугами", 1000, 600)

    tk.Label(services_window, text=f"Услуги для брони: {booking_id}", font=("Arial", 20, "bold")).pack(pady=20)

    columns = ("ID", "Название", "Цена", "Описание", "Тип", "Выбрано")
    services_tree = ttk.Treeview(services_window, columns=columns, show="headings", height=15)

    for col in columns:
        if col == "ID":
            services_tree.column(col, width=50, anchor="center")
        elif col == "Название":
            services_tree.column(col, width=150, anchor="w")
        elif col == "Цена":
            services_tree.column(col, width=100, anchor="center")
        elif col == "Описание":
            services_tree.column(col, width=300, anchor="w")
        elif col == "Тип":
            services_tree.column(col, width=100, anchor="center")
        elif col == "Выбрано":
            services_tree.column(col, width=80, anchor="center")
        services_tree.heading(col, text=col)

    scrollbar = ttk.Scrollbar(services_window, orient="vertical", command=services_tree.yview)
    services_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    services_tree.pack(pady=20, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(services_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Сохранить изменения", font=("Arial", 14), command=save_service_changes).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Закрыть", font=("Arial", 14), command=services_window.destroy).grid(row=0, column=1, padx=10)

    # Поисковая панель
    search_frame = tk.Frame(services_window)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Поиск услуг:", font=("Arial", 14)).grid(row=0, column=0, padx=10)

    search_entry = tk.Entry(search_frame, font=("Arial", 14))
    search_entry.grid(row=0, column=1, padx=10)

    def on_close_services_window():
        services_window.destroy()

    services_window.protocol("WM_DELETE_WINDOW", on_close_services_window)

    def on_search_change(event):
        search_query = search_entry.get()
        load_service_data_with_checkbox(search_query)

    search_entry.bind("<KeyRelease>", on_search_change)

    load_service_data_with_checkbox()

    # Изменение чекбокса
    services_tree.bind("<ButtonRelease-1>", toggle_checkbox)


# Интерфейс управления бронями
def open_booking_management(root):
    root.withdraw()

    global booking_window
    booking_window = tk.Toplevel()
    setup_window(booking_window, "Управление бронями", 1000, 600)

    tk.Label(booking_window, text="Управление бронями", font=("Arial", 20, "bold")).pack(pady=20)

    def on_close():
        booking_window.destroy()
        root.deiconify()

    booking_window.protocol("WM_DELETE_WINDOW", on_close)

    columns = ("ID", "Гость", "Номер", "Дата заезда", "Дата выезда", "Статус", "Примечания")
    tree = ttk.Treeview(booking_window, columns=columns, show="headings", height=15)

    tree.column("ID", width=40)
    tree.column("Гость", width=200)
    tree.column("Номер", width=150)
    tree.column("Дата заезда", width=120)
    tree.column("Дата выезда", width=120)
    tree.column("Статус", width=120)
    tree.column("Примечания", width=250, stretch=True)

    for col in columns:
        tree.heading(col, text=col)

    scrollbar = ttk.Scrollbar(booking_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.pack(pady=20, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(booking_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Добавить бронь", font=("Arial", 14),
              command=lambda: add_booking(tree)).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Удалить бронь", font=("Arial", 14),
              command=lambda: delete_booking(tree)).grid(row=0, column=1, padx=10)
    tk.Button(button_frame, text="Редактировать бронь", font=("Arial", 14),
              command=lambda: edit_booking(tree)).grid(row=0, column=2, padx=10)
    tk.Button(button_frame, text="Услуги", font=("Arial", 14),
              command=lambda: manage_services(tree)).grid(row=0, column=3, padx=10)
    tk.Button(button_frame, text="Рассчитать", font=("Arial", 14),
              command=lambda: calculate_bill(tree)).grid(row=0, column=4, padx=10)

    search_frame = tk.Frame(booking_window)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Поиск:", font=("Arial", 14)).grid(row=0, column=0, padx=10)

    search_entry = tk.Entry(search_frame, font=("Arial", 14))
    search_entry.grid(row=0, column=1, padx=10)

    def on_search_change(event):
        search_query = search_entry.get()
        load_bookings(tree, search_query)

    search_entry.bind("<KeyRelease>", on_search_change)

    load_bookings(tree)
