from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from database.crud import get_user_by_username, create_user, save_refresh_token
from database.models import UserCreate
from database.schemas import UserOut
from database.security import verify_password
from database.token import create_access_token, create_refresh_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


# Роуты для регистрации и аутентификации

@router.post("/register/", response_model=UserOut)
async def register(user: UserCreate):
    db_user = await get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await create_user(user)


@router.post("/token/")
async def login_for_access_token(user: UserCreate):
    db_user = await get_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Создаем access и refresh токены
    access_token = create_access_token({"sub": db_user["username"]})
    refresh_token = create_refresh_token({"sub": db_user["username"]})

    # Сохраняем refresh токен в базе данных
    await save_refresh_token(db_user["username"], refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh/")
async def refresh_access_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload["sub"]
    db_user = await get_user_by_username(username)
    if not db_user or db_user.get("refresh_token") != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": username})
    return {"access_token": new_access_token}


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")
    return payload


@router.get("/protected/")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}
