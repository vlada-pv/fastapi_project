from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from typing import List

from .books import ReturnedBookForSeller

__all__ = ["IncomingSeller", "ReturnedSeller", "UpdatedSeller", "ReturnedAllSellers", "ReturnedSellerWithBooks", "DeleteSeller"]

class BaseSeller(BaseModel):
    first_name: str 
    last_name: str 
    email: str

class IncomingSeller(BaseSeller):
    password: str 

class ReturnedSeller(BaseSeller):
    id: int

class UpdatedSeller(BaseModel):
    first_name: str
    last_name: str
    email: str

class ReturnedSellerWithBooks(ReturnedSeller):
    books: List[ReturnedBookForSeller] = []

class DeleteSeller(BaseModel):
    id: int
    email: str