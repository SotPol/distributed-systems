# order_service/service.py
from .repository import OrderRepository
import pika

class OrderService:
    @staticmethod
    def create_order(data):
        order = OrderRepository.add_order(data)
        # Відправка повідомлення в RabbitMQ для асинхронної обробки
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='orders')
        channel.basic_publish(exchange='', routing_key='orders', body=str(order))
        connection.close()
        return order
