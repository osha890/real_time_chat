from pydantic import BaseModel


class UserOut(BaseModel):
    username: str

    class Config:
        from_attributes = True