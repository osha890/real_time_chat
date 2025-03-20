from fastapi import HTTPException, APIRouter, Depends
from pymongo.errors import PyMongoError

from api.services.user_service import get_current_user_payload
from database.crud import get_user_by_username, save_user, save_refresh_token
from database.models import UserCreate
from database.schemas import UserOut
from database.security import verify_password
from database.token import create_access_token, create_refresh_token, verify_token

router = APIRouter()


# Роуты для регистрации и аутентификации

@router.post("/register/", response_model=UserOut)
async def register(user: UserCreate):
    """Регистрация нового пользователя"""
    try:
        db_user = await get_user_by_username(user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        saved_user = await save_user(user)
        return saved_user
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.post("/token/")
async def login_for_access_token(user: UserCreate):
    """Логин. Возвращает access token и refresh token"""
    try:
        db_user = await get_user_by_username(user.username)
        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Создаем access и refresh токены
        access_token = create_access_token({"sub": db_user["username"]})
        refresh_token = create_refresh_token({"sub": db_user["username"]})

        # Сохраняем refresh токен в базе данных
        await save_refresh_token(db_user["username"], refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.post("/refresh/")
async def refresh_access_token(refresh_token: str):
    """Обновление access токена"""
    try:
        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        username = payload["sub"]
        db_user = await get_user_by_username(username)
        if not db_user or db_user.get("refresh_token") != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token({"sub": username})
        return {"access_token": new_access_token}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"{str(e)}")


@router.get("/protected/")
async def protected_route(current_user: dict = Depends(get_current_user_payload)):
    """Проверка авторизации"""

    return {"message": "This is a protected route", "user": current_user}
