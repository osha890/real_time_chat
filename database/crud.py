from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from .db_conf import user_collection, message_collection
from .models import UserCreate
from .security import get_password_hash


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


async def save_refresh_token(username, refresh_token):
    await user_collection.update_one(
        {"username": username},
        {"$set": {"refresh_token": refresh_token}}
    )

async def save_message_doc(message):
    await message_collection.insert_one(message)