from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List



class AccountBase(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AccountUpdate(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class AccountOut(BaseModel):
    message: str
    data: AccountBase

    class Config:
        from_attributes = True
