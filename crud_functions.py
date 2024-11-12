import sqlite3


def initiate_db():
    connetion = sqlite3.connect('product.db')
    cursor = connetion.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        url TEXT NOT NULL
    )""")
    products = [
        {'Название': 'Помидоры', 'Описание': 'Банка с помидорами', 'Цена': 100, 'url': "http://bit.ly/4flwaAo"},
        {'Название': 'Огурцы', 'Описание': 'Банка с огурцами', 'Цена': 200, 'url': "https://bit.ly/3UIk1NP"},
        {'Название': 'Смесь Амосова', 'Описание': 'Витаминный комплекс - смесь Амосова', 'Цена': 300,
         'url': "https://bit.ly/3UIk6RD"},
        {'Название': 'Икра', 'Описание': 'Банка с икрой', 'Цена': 400, 'url': "https://bit.ly/3CezWgj"}
    ]
    cursor.executemany("""
            INSERT INTO Products (title, description, price, url)
            VALUES (?, ?, ?, ?)
        """, [(product['Название'], product['Описание'], product['Цена'], product['url']) for product in products])
    connetion.commit()
    connetion.close()


def get_all_products():
    connetion = sqlite3.connect('product.db')
    cursor = connetion.cursor()
    cursor.execute("""SELECT * FROM Products""")
    table = cursor.fetchall()
    connetion.close()
    return table
