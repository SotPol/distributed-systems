from fastapi import FastAPI
from service import OrderService

app = FastAPI()

@app.post("/orders")
def post_order(order: dict):
    return OrderService.create_order(order)
