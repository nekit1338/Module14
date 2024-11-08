import sqlite3

connetion = sqlite3.connect('not_telegram.db')
cursor = connetion.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, email TEXT NOT NULL, "
    "age INTEGER NOT NULL, balance INTEGER NOT NULL)")

for i in range(1, 11):
    cursor.execute("INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)",
                   (f'User{i}', f'example{i}@gmail.com', i * 10, 1000))

cursor.execute(f"UPDATE Users SET balance = balance - 500 WHERE id % 2 != 0")
cursor.execute("DELETE FROM Users WHERE id % 3 = 1")

cursor.execute("SELECT username, email, age, balance FROM Users WHERE age !=60")
users = cursor.fetchall()
for i in users:
    print(f"Имя: {i[0]} | Почта: {i[1]} | Возраст: {i[2]} | Баланс : {i[3]}")
cursor.connection.commit()
cursor.connection.close()
