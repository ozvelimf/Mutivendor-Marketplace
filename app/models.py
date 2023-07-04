import sqlite3
from passlib.hash import sha256_crypt
import math

class db():
    def __init__(self) -> None:
        self.con = sqlite3.connect("e_ticaret.db") 
        self.cur = self.con.cursor()
    def register(self, form):
        

        # Kayıt edilecek kullanıcı verileri
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        address = form.address.data
        city = form.city.data
        country = form.country.data
        phone = form.phone.data
        password = sha256_crypt.encrypt(form.password.data)

        # Veritabanına verileri kayıt etme

        query = '''INSERT INTO Users (first_name, last_name, username, email, address, city, country, phone, password)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        params = (first_name, last_name, username, email, address, city, country, phone, password)

        self.cur.execute(query, params)
        self.con.commit()

    def login(self, form):
        username = form.username.data
        password_entered = form.password.data

        query = f"SELECT * FROM Users WHERE username = '{username}'"
        self.cur.execute(query)
        data = self.cur.fetchone()
        if data is not None:
            password = data[4]
            if sha256_crypt.verify(password_entered, password):
                update_query = "UPDATE Users SET last_login = datetime('now', 'localtime') WHERE user_id = ?"
                self.cur.execute(update_query, (data[0],))
                self.con.commit()
                return [True, data[0], data[2]]
            else:
                return False
        else:
            return False
        
    def latest_products(self):
        query = '''SELECT * FROM Products ORDER BY product_id DESC LIMIT 5'''
        self.cur.execute(query)
        latest_products = self.cur.fetchall()

        query2 = '''SELECT Products.product_id, Product_Images.image_path 
        FROM Products 
        JOIN Product_Images ON Products.product_id = Product_Images.product_id 
        WHERE Products.product_id IN (SELECT product_id FROM Products ORDER BY product_id DESC LIMIT 5) 
        ORDER BY Products.product_id DESC
        '''

        self.cur.execute(query2)
        product_images = self.cur.fetchall()
        product_data = []
        for product, image in zip(latest_products, product_images):
            # Ürün verilerini ayrıştırma
            product_id, name, description, price, quantity, brand_id, category_id = product
            # Ürün resimlerini düzenleme
            image_path = image[1]

            product_data.append({
                'id': product_id,
                'name': name,
                'description': description,
                'price': int(price),
                'quantity': quantity,
                'brand': brand_id,
                'category_id' : category_id,
                'image': image_path
            })
        return product_data

    def get_brands(self):
        query = '''SELECT * FROM Brands ORDER BY brand_id DESC'''
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_cart_for_home(self, user_id):
        query = f'''SELECT * FROM Cart WHERE user_id = "{user_id}"'''
        self.cur.execute(query)
        cart_data = self.cur.fetchall()
        total_price = 0
        for i in cart_data:
            query2 = f'''SELECT price FROM Products WHERE product_id = "{i[2]}"'''
            self.cur.execute(query2)
            product_price = self.cur.fetchone()
            total_price = total_price + (product_price[0] *i[3])

        total_price = f"{int(total_price):,}".replace(",", ".")
        return [len(cart_data), total_price]

    def get_cart(self, user_id):
        query = f'''SELECT * FROM Cart WHERE user_id = "{user_id}"'''
        self.cur.execute(query)
        data = self.cur.fetchall()
        product_data = []
        for cart in data:
            cart_id, userid, product_id, quantity = cart
            query2 = f'''SELECT image_path FROM Product_Images WHERE product_id = "{product_id}"'''
            self.cur.execute(query2)
            image = self.cur.fetchone()
            image_path = image[0]

            query3 = f'''SELECT * FROM Products WHERE product_id = "{product_id}"'''
            self.cur.execute(query3)
            data_product = self.cur.fetchone()
            product_id2, name, description, price, quantity1, brand_id, category_id = data_product
            total_price = int(price) * quantity
            product_data.append({
                'id': product_id,
                'name': name,
                'price': f"{int(price):,}".replace(",", "."),
                'quantity': quantity,
                'image': image_path,
                'total_price': f"{total_price:,}".replace(",", "."),
                'cart_id': cart_id
            })
        
        return product_data

    def get_product(self,  user_id=0, product_id=0):
        query = f'''SELECT * FROM Products WHERE product_id = "{product_id}"'''
        self.cur.execute(query)
        product_id, name, description, price, quantity, brand_id, category_id = self.cur.fetchone()
        description_list = description.split('/')

        query2 = f'''SELECT image_path FROM Product_Images WHERE product_id = "{product_id}"'''
        self.cur.execute(query2)
        image_path = self.cur.fetchone()[0]

        query3 = f''' SELECT category_name FROM Categories WHERE category_id = "{category_id}"'''
        self.cur.execute(query3)
        category_name = self.cur.fetchone()[0]
        product_data = ({
                'product_id': product_id,
                'name': name,
                'price': f"{int(price):,}".replace(",", "."),
                'description': description_list,
                'image': image_path,
                'category': category_name,
                'favorite' : self.fav_verification(user_id, product_id)
            })
        
        return product_data

    def get_products(self, user_id = 0, page=1, per_page=12):
        count_query = '''SELECT COUNT(*) FROM Products'''
        self.cur.execute(count_query)
        total_count = self.cur.fetchone()[0]
        total_pages = math.ceil(total_count / per_page)
        offset = (page - 1) * per_page
        
        query = f'''SELECT * FROM Products ORDER BY product_id DESC LIMIT {per_page} OFFSET {offset}'''
        self.cur.execute(query)
        products = self.cur.fetchall()
        product_data = []
        for product in products:
            product_id, name, description, price, quantity, brand_id, category_id = product
            query2 = f'''SELECT image_path FROM Product_Images WHERE product_id = "{product_id}"'''
            self.cur.execute(query2)
            image_path = self.cur.fetchone()[0]
            product_data.append({
                'id': product_id,
                'name': name,
                'price': f"{int(price):,}".replace(",", "."),
                'image': image_path,
                'favorites': self.fav_verification(user_id, product_id)
            })

        return product_data, total_pages
    
    def addcart(self, user_id, product_id, quantity):
        self.cur.execute('SELECT quantity FROM Cart WHERE user_id = ? AND product_id = ?', (user_id, product_id))
        result = self.cur.fetchone()

        if result:
            current_quantity = result[0]
            new_quantity = current_quantity + quantity
            self.cur.execute('UPDATE Cart SET quantity = ? WHERE user_id = ? AND product_id = ?', (new_quantity, user_id, product_id))
        else:
            self.cur.execute('INSERT INTO Cart (user_id, product_id, quantity) VALUES (?, ?, ?)', (user_id, product_id, quantity))

        self.con.commit()

    def removecart(self, cart_id):
        query = f'''DELETE FROM Cart WHERE cart_id = "{cart_id}"'''
        self.cur.execute(query)
        self.con.commit()

    def get_favorites(self,user_id):
        query = f'''SELECT * FROM Favorites WHERE user_id = "{user_id}"'''
        self.cur.execute(query)
        result = self.cur.fetchall()
        if len(result) == 0:
            return []
        else:
            product_data = list()
            for row in result:
                favorite_id, userid, product_id = row
                self.cur.execute(f'SELECT product_name, price FROM Products WHERE product_id = "{product_id}"')
                name, price = self.cur.fetchone()
                
                self.cur.execute(f'SELECT image_path FROM Product_Images WHERE product_id = "{product_id}"')
                image_path = self.cur.fetchone()[0]
                product_data.append({
                    'product_id' : product_id,
                    'favorite_id' : favorite_id,
                    'name' : name,
                    'price': f"{int(price):,}".replace(",", "."),
                    'image': image_path
                })

            return product_data

    def removefav(self, id):
        query = f'''DELETE FROM Favorites WHERE favorite_id = "{id}"'''
        self.cur.execute(query)
        self.con.commit()

    def fav_verification(self,user_id, product_id):
        if user_id == 0:
            return [False]
        else:
            self.cur.execute(f'SELECT * FROM Favorites WHERE user_id = "{user_id}" AND product_id = "{product_id}"')
            result = self.cur.fetchone()
            if result is None:
                return [False]
            else:
                return [True, result[0]]
            
    def addfav(self, user_id, product_id):
        self.cur.execute('INSERT INTO Favorites (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
        self.con.commit()
    
    def get_categories(self):
        self.cur.execute('SELECT * FROM Categories')
        return self.cur.fetchall()

    def close(self):
        self.con.close()