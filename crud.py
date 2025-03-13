from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from database import user_collection
from models import UserCreate
from security import get_password_hash


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
