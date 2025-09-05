from fastapi import FastAPI, Depends, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth import create_access_token, verify_password, fake_users_db
from backend.deps import get_current_user
from fastapi.responses import JSONResponse
import requests

app = FastAPI()



# Подключаем фронтенд
app.mount("/static", StaticFiles(directory="frontend"), name="static")

BOT_API_URL = "http://bot:8001" # URL контейнера бота
BOT_API_KEY = "mysecret123"  # секрет для внутреннего API

@app.get("/")
def read_index():
    return FileResponse("frontend/index.html")

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")  # логируем через uvicorn

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print("Login endpoint called")  # <--- новый print
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        print(f"Failed login attempt for user: {form_data.username}")
        return {"error": "Invalid credentials"}
    token = create_access_token({"sub": form_data.username})
    print(f"Generated token for {form_data.username}: {token}")
    return {"access_token": token, "token_type": "bearer"}




@app.get("/secure-data")
def secure_data(user: dict = Depends(get_current_user)):
    print(f"Accessing secure data for user: {user['username']}")
    return {"msg": f"Hello, {user['username']}! This is protected."}



@app.post("/create-order")
def create_order(order_name: str = Form(...), user: dict = Depends(get_current_user)):
    # 1. Сохраняем заказ в базу (например, SQLite / Postgres)
    order_data = {"order_name": order_name, "user": user["username"]}

    # 2. Отправляем данные на бот через API
    resp = requests.post(
        f"{BOT_API_URL}/create-order",
        json=order_data,
        headers={"X-API-KEY": BOT_API_KEY}
    )
    if resp.status_code != 200:
        return {"status": "error", "detail": resp.text}

    return {"status": "ok", "order": order_data}


@app.get("/getorders")
def proxy_get_orders(user: dict = Depends(get_current_user)):
    """
    Получаем список заказов из бота и проксируем пользователю
    """
    try:
        resp = requests.get(
            f"{BOT_API_URL}/getorders",
            headers={"X-API-KEY": BOT_API_KEY}
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

    if resp.status_code != 200:
        return JSONResponse(
            status_code=resp.status_code,
            content={"status": "error", "detail": resp.text}
        )

    return resp.json()