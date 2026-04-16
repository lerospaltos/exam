from database import Database


class ProductService:
    def __init__(self):
        self.db = Database()

    def get_all_products(self):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT id, name, description, price, discount FROM products")
        products = []
        for row in cur.fetchall():
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2] if row[2] else "",
                "price": float(row[3]),
                "discount": float(row[4]),
                "final_price": float(row[3]) * (1 - float(row[4]) / 100)
            })
        cur.close()
        return products

    def search_products(self, search_text):
        cur = self.db.get_connection().cursor()
        cur.execute(
            "SELECT id, name, description, price, discount FROM products WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s)",
            (f"%{search_text}%", f"%{search_text}%")
        )
        products = []
        for row in cur.fetchall():
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2] if row[2] else "",
                "price": float(row[3]),
                "discount": float(row[4]),
                "final_price": float(row[3]) * (1 - float(row[4]) / 100)
            })
        cur.close()
        return products

    def filter_by_discount(self, discount_range):
        cur = self.db.get_connection().cursor()
        if discount_range == "0-15":
            sql = "SELECT id, name, description, price, discount FROM products WHERE discount >= 0 AND discount < 15"
        elif discount_range == "15-25":
            sql = "SELECT id, name, description, price, discount FROM products WHERE discount >= 15 AND discount < 25"
        elif discount_range == "25+":
            sql = "SELECT id, name, description, price, discount FROM products WHERE discount >= 25"
        else:
            sql = "SELECT id, name, description, price, discount FROM products"

        cur.execute(sql)
        products = []
        for row in cur.fetchall():
            products.append({
                "id": row[0],
                "name": row[1],
                "description": row[2] if row[2] else "",
                "price": float(row[3]),
                "discount": float(row[4]),
                "final_price": float(row[3]) * (1 - float(row[4]) / 100)
            })
        cur.close()
        return products