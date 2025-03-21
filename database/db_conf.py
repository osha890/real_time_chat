import os
from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# Настройки MongoDB
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("MONGO_DB_NAME")
client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=3000)
database = client[str(DATABASE_NAME)]

user_collection = database["users"]
messages_collection = database["messages"]
