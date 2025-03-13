from fastapi import HTTPException, APIRouter

from database.crud import get_user_by_username, create_user
from database.models import UserCreate
from database.schemas import UserOut
from database.security import verify_password


router = APIRouter()

# Роуты для регистрации и аутентификации

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    db_user = await get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(user)


@router.post("/login")
async def login(user: UserCreate):
    db_user = await get_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "username": db_user["username"]}