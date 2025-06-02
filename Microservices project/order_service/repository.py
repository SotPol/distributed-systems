# order_service/repository.py
import psycopg2

conn = psycopg2.connect(dbname="orders", user="postgres", password="pass", host="postgres")
cursor = conn.cursor()

class OrderRepository:
    @staticmethod
    def add_order(data):
        # Збереження замовлення в таблиці orders
        cursor.execute("INSERT INTO orders(product, quantity) VALUES (%s, %s) RETURNING id",
                       (data["product"], data["quantity"]))
        order_id = cursor.fetchone()[0]
        conn.commit()
        return {"order_id": order_id, "status": "created"}
