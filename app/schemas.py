from datetime import datetime
from typing import *

from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import Date


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class FoodBase(BaseModel):
    food_name: str
    proteins: int
    carbs: int
    fats: int


class CreateFood(FoodBase):
    pass


class LogBase(BaseModel):
    when: str
