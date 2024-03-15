from fastapi import APIRouter, Depends
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations.database import get_async_session

from typing import List, Annotated
from fastapi import HTTPException

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, ReturnedSeller, ReturnedSellerWithBooks, DeleteSeller, UpdatedSeller
from src.schemas.books import ReturnedBookForSeller

sellers_router = APIRouter(tags=["sellers"], prefix="/seller")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Ручка для создания продавца в базе данных
@sellers_router.post("/create", response_model=ReturnedSeller)
async def create_seller(seller: IncomingSeller, session: DBSession):
    async with session() as session:
        new_seller = Seller(first_name=seller.first_name, last_name=seller.last_name, email=seller.email)
        new_seller.set_password(seller.password)
        session.add(new_seller)
        await session.commit()
        await session.refresh(new_seller)
        return new_seller

# Ручка для получения всех продавцов
@sellers_router.get("/", response_model=List[ReturnedSeller])
async def get_all_sellers(session: DBSession):
    async with session() as session:
        sellers = await session.execute(select(Seller).order_by(Seller.id))
        sellers_list = sellers.scalars().all()
        return sellers_list

# Ручка для просмотра данных о конкретном продавце
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller_by_id(seller_id: int, session: DBSession):
    async with session() as session:
        seller = await session.get(Seller, seller_id)
        if seller is None:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Исключаем пароль из ответа
        returned_seller = ReturnedSellerWithBooks(id=seller.id, first_name=seller.first_name, last_name=seller.last_name, email=seller.email)

        # Достаем все книги конкретного продавца
        books = []
        for book in seller.books:
            returned_book = ReturnedBookForSeller(id=book.id, title=book.title, author=book.author, year=book.year, count_pages=book.count_pages, seller_id=seller.id)
            books.append(returned_book)
        
        returned_seller.books = books
        
        return returned_seller

# Ручка для обновления данных о продавце 
@sellers_router.put("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def update_seller(seller_id: int, seller_data: UpdatedSeller, session: DBSession):
    async with session() as session:
        seller = await session.get(Seller, seller_id)
        if seller is None:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Обновляем данные
        seller.first_name = seller_data.first_name
        seller.last_name = seller_data.last_name
        seller.email = seller_data.email

        await session.commit()
        
        # Исключаем пароль в целях безопасности 
        returned_seller = ReturnedSellerWithBooks(id=seller.id, first_name=seller.first_name, last_name=seller.last_name, email=seller.email)

        # Достаем все книги конкретного продавца
        books = []
        for book in seller.books:
            returned_book = ReturnedBookForSeller(id=book.id, title=book.title, author=book.author, year=book.year, count_pages=book.count_pages, seller_id=seller.id)
            books.append(returned_book)
        
        returned_seller.books = books
        
        return returned_seller
    
# Ручка для удаления данных о продавце 
@sellers_router.delete("/")
async def delete_seller(data: DeleteSeller, session: DBSession):
    async with session() as session:
        seller = await session.get(Seller, data.id)
        if seller is None or seller.email != data.email:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Delete all books associated with this seller
        for book in seller.books:
            await session.delete(book)
        
        await session.delete(seller)
        await session.commit()

        return {"message": "Seller and associated books deleted successfully"}