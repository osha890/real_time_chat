from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from .db_conf import user_collection, messages_collection
from .models import UserCreate
from .security import get_password_hash


# Функции для работы с MongoDB

async def get_user_by_username(username: str):
    user = await user_collection.find_one({"username": username})
    return user


async def save_user(user: UserCreate):
    user_dict = {"username": user.username, "password_hash": get_password_hash(user.password)}
    try:
        result = await user_collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        return user_dict
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Username already registered")


async def save_refresh_token(username: str, refresh_token: str):
    await user_collection.update_one(
        {"username": username},
        {"$set": {"refresh_token": refresh_token}}
    )


async def save_message_doc(message: dict):
    result = await messages_collection.insert_one(message)
    return result


async def update_message_to_delivered(message_doc_id: str):
    # Помечаем сообщение как "доставленное"
    await messages_collection.update_one(
        {"_id": message_doc_id}, {"$set": {"delivered": True}}
    )


async def get_undelivered_messages(username: str):
    messages = await messages_collection.find({"recipient": username, "delivered": False}).to_list(100)
    return messages


async def get_chat_messages_by_chat_id(chat_id: str):
    messages = await messages_collection.find({"chat_id": chat_id}).to_list(100)
    return messages
