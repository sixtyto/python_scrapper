import mysql.connector
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Database:
    def __init__(self, host=getenv('HOST'), port=getenv('PORT'), user=getenv('DB_USER'), password=getenv('DB_PASSWORD'), database=getenv('DATABASE')):
        self.cnx = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.cnx.cursor(buffered=True)
        print(self.cnx)

    def __del__(self):
        self.cursor.close()
        self.cnx.close()

    def get_offer_id(self, url):
        self.cursor.execute('SELECT id FROM offers WHERE Offer_URL=%s', (url,))
        return self.cursor.fetchone()

    def update_database(self, offer_id, price, timestamp, rating):
        print(f"updating {offer_id}: {price}, {rating}, {timestamp}")
        self.cursor.execute('INSERT INTO economies (offer_id, price, rating, updatedAt) VALUES (%s, %s, %s, %s)',
                            (offer_id, price, rating, timestamp))
        self.cnx.commit()

    def add_new_record(self, name, ean, link, image_url, seller, brand, dimensions, weight, category, subcategory,
                       price, rating, timestamp):
        print(f"adding {ean}: {link}")
        self.cursor.execute('SELECT id FROM products WHERE ean=%s', (ean,))
        product_id = self.cursor.fetchone()
        if not product_id:
            self.cursor.execute('INSERT INTO products (name, ean, product_img, brand, dimensions, weight, category, subcategory, price, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                                (name, ean, image_url, brand, dimensions, weight, category, subcategory, price, rating))
            self.cnx.commit()
        self.cursor.execute('INSERT INTO offers (offer_url, seller, product_id) VALUES(%s, %s, %s)',
                            (link, seller, product_id[0]))
        self.cnx.commit()
        self.cursor.execute('SELECT id FROM offers WHERE Offer_URL=%s', (link,))
        offer_id = self.cursor.fetchone()
        self.cursor.execute('INSERT INTO economies (offer_id, price, rating, updatedAt) VALUES (%s, %s, %s, %s)',
                            (offer_id[0], price, rating, timestamp))
        self.cnx.commit()

    def get_cart_urls(self):
        self.cursor.execute("SELECT productsId FROM followed_products")
        ids = self.cursor.fetchall()
        urls = []
        for ID in ids:
            self.cursor.execute("SELECT offer_url FROM offers WHERE product_id = %s", (ID,))
            urls.append((ID, self.cursor.fetchall()))
        results = []
        for item in urls:
            offer_id = item[0]
            for url in item[1]:
                results.append((offer_id, url))
        return results

    def add_cart_amount(self, offer_id, amount, timestamp):
        self.cursor.execute('INSERT INTO carts (amount, updateAt, offersId) VALUES(%s, %s, %s)',
                            (amount, timestamp, offer_id))
        self.cnx.commit()
