from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Настройки MongoDB

MONGO_URI = os.getenv("MONGO_URI")  # Поменяй на свой URI
DATABASE_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
user_collection = database["users"]

# Настройки для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модели Pydantic для запросов и ответов
class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str

    class Config:
        orm_mode = True

# Функции для работы с MongoDB

async def get_user_by_username(username: str):
    user = await user_collection.find_one({"username": username})
    return user

async def create_user(user: UserCreate):
    user_dict = {"username": user.username, "password_hash": get_password_hash(user.password)}
    try:
        result = await user_collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        return user_dict
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username already registered")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

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

