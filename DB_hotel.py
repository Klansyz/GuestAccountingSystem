import sqlite3

DB_PATH = '/Users/klimvolokhov/PycharmProjects/GuestAccountingSystem/DB_hotel.db'

# Подключение к базе данных
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# Включение проверки внешних ключей
cursor.execute("PRAGMA foreign_keys = ON;")


# Создание таблицы "Администраторы базы данных"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Admins (
    admin_id INTEGER PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    phone VARCHAR(15),
    email VARCHAR(255)
);
''')


# Создание таблицы "Гости"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Guests (
    guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(255),
    passport VARCHAR(20)
);
''')


# Создание таблицы "Номера"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Rooms (
    room_number INTEGER PRIMARY KEY,
    room_type VARCHAR(50) NOT NULL,
    price REAL NOT NULL,
    availability BOOLEAN DEFAULT TRUE,
    CHECK (price >= 0)
);
''')


# Создание таблицы "Услуги"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name VARCHAR(100) NOT NULL,
    price REAL NOT NULL,
    description TEXT,
    service_type VARCHAR(50) CHECK(service_type IN ('Разовая', 'Ежедневная')) NOT NULL,
    availability BOOLEAN DEFAULT TRUE,
    CHECK (price >= 0)
);
''')


# Создание таблицы "Бронь"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL,
    room_number INTEGER NOT NULL,
    checking_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Забронировано',
    notes VARCHAR(500),
    FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
    FOREIGN KEY (room_number) REFERENCES Rooms(room_number) ON UPDATE CASCADE,
    CHECK (status IN ('Забронировано', 'Проживание', 'Выполнено', 'Отменено'))
);
''')


# Создание промежуточной таблицы "Брони -- Услуги"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Booking_Services (
    booking_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    FOREIGN KEY (service_id) REFERENCES Services(service_id),
    PRIMARY KEY (booking_id, service_id)  -- Составной первичный ключ
);
''')


# Создание таблицы "Счета"
cursor.execute('''
CREATE TABLE IF NOT EXISTS Bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'Не оплачен',
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),
    CHECK (total_amount > 0)
);
''')


# Добавление данных в таблицу "Админисраторы"
cursor.execute('''
INSERT INTO Admins (last_name, first_name, middle_name, password, login, phone, email)
VALUES 
('Иванов', 'Алексей', 'Сергеевич', '1', '1', '+7 (999) 123-45-67', 'ivanov.alexey@example.com'),
('Кузнецов', 'Дмитрий', 'Владимирович', '2', '2', '+7 (999) 987-65-43', 'kuznetsov.dmitry@example.com'),
('Смирнова', 'Анна', 'Игоревна', '3', '3', '+7 (999) 543-21-09', 'smirnova.anna@example.com');
''')

# Добавление данных в таблицу "Гости"
cursor.execute('''
INSERT OR IGNORE INTO Guests (guest_id, last_name, first_name, middle_name, phone, email, passport) VALUES 
 ('1', 'Иванов', 'Иван', 'Иванович', '+7 (982) 986-66-64', 'ivan.ivanov@example.com', '4970 977258'),
 ('2', 'Петрова', 'Ольга', 'Сергеевна', '+7 (928) 480-67-50', 'olga.petrova@example.com', '4273 802598'),
 ('3', 'Сидоров', 'Петр', 'Алексеевич', '+7 (999) 648-14-47', 'petr.sidorov@example.com', '4043 917074'),
 ('4', 'Воробьева', 'Вероника', 'Максимовна', '+7 (995) 777-28-73', 'veronika.borobyova@example.com', '4357 279861'),
 ('5', 'Петухова', 'Вера', 'Федоровна', '+7 (956) 484-46-19', 'vera.petuhova@example.com', '4721 328957'),
 ('6', 'Пахомов', 'Даниил', 'Иванович', '+7 (975) 756-63-51', 'daniil.pahomov@example.com', '4593 986718'),
 ('7', 'Лебедев', 'Михаил', 'Александрович', '+7 (958) 734-35-97', 'mihail.lebedev@example.com', '4088 240374'),
 ('8', 'Сухарев', 'Федор', 'Львович', '+7 (919) 773-23-30', 'fedor.suharev@example.com', '4614 178093'),
 ('9', 'Панкратов', 'Платон', 'Степанович', '+7 (949) 467-42-82', 'platon.pankratov@example.com', '4252 445071'),
 ('10', 'Рожкова', 'Мария', 'Ивановна', '+7 (937) 440-15-41', 'mariya.rozhkova@example.com', '4058 889889');
''')

# Добавление данных в таблицу "Номера"
cursor.execute('''
INSERT OR IGNORE INTO Rooms (room_number, room_type, price, availability) VALUES
 ('101', 'Стандартный', 1000.00, TRUE),
 ('102', 'Стандартный', 1000.00, TRUE),
 ('103', 'Стандартный', 1500.00, FALSE),
 ('104', 'Стандартный', 2000.00, TRUE),
 ('202', 'Люкс', 2500.00, TRUE),
 ('203', 'Люкс', 3000.00, FALSE),
 ('204', 'Люкс', 3500.00, TRUE),
 ('303', 'Апартаменты', 8000.00, TRUE),
 ('304', 'Апартаменты', 10000.00, TRUE);
''')

cursor.execute('''
INSERT INTO Services (service_name, price, description, service_type, availability)
VALUES ('Уборка номера', 500, 'Ежедневная уборка номера в течение пребывания', 'Ежедневная', TRUE),
       ('Трансфер', 1500, 'Трансфер от/до аэропорта', 'Разовая', TRUE),
       ('Завтрак', 350, 'Континентальный завтрак в ресторане отеля', 'Ежедневная', TRUE),
       ('Массаж', 1200, 'Массаж с использованием эфирных масел', 'Разовая', FALSE);
''')

conn.commit()
conn.close()

print("База данных успешно обновлена и заполнена.")
