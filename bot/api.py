# bot/api.py
from fastapi import FastAPI, Header, HTTPException
from aiogram import Bot

from db.crud.order import get_all_orders

app = FastAPI()
API_KEY = "mysecret123"  # секрет для внутреннего API

@app.post("/create-order")
async def create_order(order: dict, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    print(f"Received order: {order}")
    return {"status": "ok"}



@app.get('/getorders')
async def get_orders(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    orders = await get_all_orders()
    print(f"Fetched orders: {orders}")
    return {"orders": [order.__dict__ for order in orders]}
    