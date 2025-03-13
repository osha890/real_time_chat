from fastapi import FastAPI, HTTPException

from crud import get_user_by_username, create_user
from models import UserCreate
from schemas import UserOut
from security import verify_password

app = FastAPI()


# Роуты для регистрации и аутентификации

@app.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    db_user = await get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(user)


@app.post("/login")
async def login(user: UserCreate):
    db_user = await get_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "username": db_user["username"]}
