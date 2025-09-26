from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm

from backend.auth import create_access_token, verify_password, fake_users_db
from backend.deps import get_current_user
from backend.schemas import OrderRequest, SupplierRequest

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

@app.get("/drivers")
def read_index():
    return FileResponse("frontend/drivers.html")

@app.get("/suppliers")
def read_index():
    return FileResponse("frontend/suppliers.html")

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")  # логируем через uvicorn
logging.info("awdawdawwwwwwwwwwwwwwwww")

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



from datetime import datetime

@app.post("/create-order")
def create_order(order: OrderRequest, user: dict = Depends(get_current_user)):
    print("✅ Order получен:", order.dict())
    print("✅ User:", user)

    logging.info(order)

    order_data = order.dict()
    order_data["user"] = user["username"]

    # сериализуем datetime в строку
    if isinstance(order_data["datetime"], datetime):
        order_data["datetime"] = order_data["datetime"].isoformat()

    print("✅ Отправляем в бота:", order_data)

    try:
        resp = requests.post(
            f"{BOT_API_URL}/create-order",
            json=order_data,
            headers={"X-API-KEY": BOT_API_KEY},
            timeout=5
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bot API error: {e}")

    print("✅ Ответ от бота:", resp.status_code, resp.text)

    if resp.status_code != 200:
        return {"status": "error", "detail": resp.text}

    return {"status": "ok", "order": order_data}

@app.post("/update-order")
def create_order(order: OrderRequest, user: dict = Depends(get_current_user)):
    print("✅ Order получен:", order.dict())
    print("✅ User:", user)

    logging.info(order)

    order_data = order.dict()
    order_data["user"] = user["username"]

    # сериализуем datetime в строку
    if isinstance(order_data["datetime"], datetime):
        order_data["datetime"] = order_data["datetime"].isoformat()

    print("✅ Отправляем в бота:", order_data)

    try:
        resp = requests.post(
            f"{BOT_API_URL}/update-order",
            json=order_data,
            headers={"X-API-KEY": BOT_API_KEY},
            timeout=5
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bot API error: {e}")

    print("✅ Ответ от бота:", resp.status_code, resp.text)

    if resp.status_code != 200:
        return {"status": "error", "detail": resp.text}

    return {"status": "ok", "order": order_data}


@app.post("/create-supplier")
def create_order(supplier: SupplierRequest, user: dict = Depends(get_current_user)):
    print("✅ Order получен:", supplier.dict())
    print("✅ User:", user)

    order_data = supplier.dict()
    order_data["user"] = user["username"]

    print("✅ Отправляем в бота:", order_data)

    try:
        resp = requests.post(
            f"{BOT_API_URL}/create-supplier",
            json=order_data,
            headers={"X-API-KEY": BOT_API_KEY},
            timeout=5
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Bot API error: {e}")

    print("✅ Ответ от бота:", resp.status_code, resp.text)

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



@app.get("/getdrivers")
def proxy_get_drivers(user: dict = Depends(get_current_user)):
    """
    Получаем список заказов из бота и проксируем пользователю
    """
    try:
        resp = requests.get(
            f"{BOT_API_URL}/getdrivers",
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


@app.get("/getsuppliers")
def proxy_get_drivers(user: dict = Depends(get_current_user)):
    """
    Получаем список поставщиков из бота и проксируем пользователю
    """
    try:
        resp = requests.get(
            f"{BOT_API_URL}/getsuppliers",
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

@app.post("/cancel-order/{order_id}")
def cancel_order(order_id: int, user: dict = Depends(get_current_user)):
    """
    Отменяем заказ через бота
    """
    try:
        resp = requests.post(
            f"{BOT_API_URL}/cancel-order/{order_id}",
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

    # Успешно
    return {"status": "ok", "order_id": order_id}



@app.get("/driverphoto")
def driverphoto():
    return FileResponse("frontend/driverphoto.jpg")