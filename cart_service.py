from database import Database


class CartService:
    def __init__(self):
        self.db = Database()

    def add_to_cart(self, user_id, product_id):
        cur = self.db.get_connection().cursor()
        # Проверяем, есть ли уже товар
        cur.execute(
            "SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE id = %s",
                (existing[0],)
            )
        else:
            cur.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, 1)",
                (user_id, product_id)
            )
        self.db.get_connection().commit()
        cur.close()

    def get_cart(self, user_id):
        cur = self.db.get_connection().cursor()
        cur.execute("""
            SELECT p.id, p.name, p.description, p.price, p.discount, c.quantity 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """, (user_id,))
        items = []
        for row in cur.fetchall():
            price = float(row[3])
            discount = float(row[4])
            final_price = price * (1 - discount / 100)
            items.append({
                "product_id": row[0],
                "name": row[1],
                "description": row[2] if row[2] else "",
                "price": price,
                "discount": discount,
                "final_price": final_price,
                "quantity": row[5],
                "total": final_price * row[5]
            })
        cur.close()
        return items

    def get_cart_count(self, user_id):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT SUM(quantity) FROM cart WHERE user_id = %s", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        return result if result else 0

    def get_cart_total(self, user_id):
        items = self.get_cart(user_id)
        return sum(item["total"] for item in items)

    def remove_from_cart(self, user_id, product_id):
        cur = self.db.get_connection().cursor()
        cur.execute(
            "DELETE FROM cart WHERE user_id = %s AND product_id = %s",
            (user_id, product_id)
        )
        self.db.get_connection().commit()
        cur.close()

    def clear_cart(self, user_id):
        cur = self.db.get_connection().cursor()
        cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        self.db.get_connection().commit()
        cur.close()

    def create_order(self, user_id):
        items = self.get_cart(user_id)
        if not items:
            return False

        total = self.get_cart_total(user_id)
        cur = self.db.get_connection().cursor()

        # Создаем заказ
        cur.execute(
            "INSERT INTO orders (user_id, total_sum) VALUES (%s, %s) RETURNING id",
            (user_id, total)
        )
        order_id = cur.fetchone()[0]

        # Добавляем позиции
        for item in items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, price_at_order) VALUES (%s, %s, %s)",
                (order_id, item["product_id"], item["final_price"])
            )

        # Очищаем корзину
        cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

        self.db.get_connection().commit()
        cur.close()
        return True