import psycopg2
import csv

conn = psycopg2.connect(
    host='localhost',
    database='pp2',
    user='pp2',
    password='pp2pass'
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);
""")
conn.commit()

def insert_from_console():
    name = input("Введите имя: ")
    phone = input("Введите телефон: ")
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print("Добавлено!")

def insert_from_csv():
    file_path = input("Введите путь к CSV-файлу: ")
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                            (row['name'], row['phone']))
        conn.commit()
        print("Данные из CSV загружены!")
    except Exception as e:
        print("Ошибка при загрузке CSV:", e)

def update_user():
    name = input("Введите имя пользователя для обновления: ")
    new_name = input("Новое имя (оставьте пустым, если не менять): ")
    new_phone = input("Новый телефон (оставьте пустым, если не менять): ")
    if new_name:
        cur.execute("UPDATE phonebook SET name = %s WHERE name = %s", (new_name, name))
    if new_phone:
        cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, new_name or name))
    conn.commit()
    print("Обновление выполнено!")

def query_data():
    print("1 - Поиск по имени")
    print("2 - Поиск по телефону")
    choice = input("Выберите: ")
    if choice == '1':
        name = input("Введите имя: ")
        cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", (f"%{name}%",))
    elif choice == '2':
        phone = input("Введите телефон: ")
        cur.execute("SELECT * FROM phonebook WHERE phone ILIKE %s", (f"%{phone}%",))
    else:
        print("Неверный выбор")
        return
    results = cur.fetchall()
    print("Результаты:")
    for row in results:
        print(row)

def delete_user():
    print("1 - Удалить по имени")
    print("2 - Удалить по телефону")
    choice = input("Выберите: ")
    if choice == '1':
        name = input("Введите имя: ")
        cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))
    elif choice == '2':
        phone = input("Введите телефон: ")
        cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
    else:
        print("Неверный выбор")
        return
    conn.commit()
    print("Удаление выполнено!")

def main():
    while True:
        print("\nPHONEBOOK MENU")
        print("1 - Добавить запись вручную")
        print("2 - Загрузить из CSV")
        print("3 - Обновить запись")
        print("4 - Найти запись")
        print("5 - Удалить запись")
        print("6 - Выйти")
        choice = input("Ваш выбор: ")

        if choice == '1':
            insert_from_console()
        elif choice == '2':
            insert_from_csv()
        elif choice == '3':
            update_user()
        elif choice == '4':
            query_data()
        elif choice == '5':
            delete_user()
        elif choice == '6':
            break
        else:
            print("Неверный ввод")

    cur.close()
    conn.close()
    print("Выход. Соединение закрыто.")

if __name__ == '__main__':
    main()
