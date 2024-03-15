import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.sellers import Seller
from src.models.books import Book

# Тест на ручку создания продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    # Отправляем POST-запрос на создание продавца
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "password": "securepassword"
    }
    response = await async_client.post("/sellers/create", json=data)

    assert response.status_code == 200
    seller_data = response.json()
    assert "id" in seller_data
    assert seller_data["first_name"] == data["first_name"]
    assert seller_data["last_name"] == data["last_name"]
    assert seller_data["email"] == data["email"]

    # Проверяем, что продавец был успешно создан в базе данных
    created_seller = await Seller.get(seller_data["id"])
    assert created_seller is not None
    assert created_seller.first_name == data["first_name"]
    assert created_seller.last_name == data["last_name"]
    assert created_seller.email == data["email"]


# Тест на ручку для получения всех продавцов 
@pytest.mark.asyncio
async def test_get_all_sellers(async_client):
    # Создаем несколько продавцов для теста
    sellers_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "password": "securepassword"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "janesmith@example.com",
            "password": "anotherpassword"
        }
    ]
    for seller_data in sellers_data:
        await Seller.create(**seller_data)

    # Отправляем GET-запрос на получение всех продавцов
    response = await async_client.get("/sellers/")

    assert response.status_code == 200
    sellers_list = response.json()
    assert len(sellers_list) == len(sellers_data)

    # Проверяем, что все созданные продавцы присутствуют в ответе
    for i, seller_data in enumerate(sellers_data):
        assert sellers_list[i]["first_name"] == seller_data["first_name"]
        assert sellers_list[i]["last_name"] == seller_data["last_name"]
        assert sellers_list[i]["email"] == seller_data["email"]
    
# Тест на ручку для просмотра данных о конкретном продавце
@pytest.mark.asyncio
async def test_get_seller_by_id(async_client):
    # Создаем продавца и его книги для теста
    seller_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "password": "securepassword"
    }
    seller = await Seller.create(**seller_data)

    books_data = [
        {
            "title": "Book 1",
            "author": "Author 1",
            "year": 2021,
            "count_pages": 100
        },
        {
            "title": "Book 2",
            "author": "Author 2",
            "year": 2022,
            "count_pages": 150
        }
    ]
    for book_data in books_data:
        await Book.create(seller_id=seller.id, **book_data)

    # Отправляем GET-запрос на получение данных о продавце по его ID
    response = await async_client.get(f"/sellers/{seller.id}")

    assert response.status_code == 200
    seller_info = response.json()

    # Проверяем корректность данных о продавце и его книгах
    assert seller_info["id"] == seller.id
    assert seller_info["first_name"] == seller_data["first_name"]
    assert seller_info["last_name"] == seller_data["last_name"]
    assert seller_info["email"] == seller_data["email"]
    
    assert len(seller_info["books"]) == len(books_data)
    for i, book_data in enumerate(books_data):
        assert seller_info["books"][i]["title"] == book_data["title"]
        assert seller_info["books"][i]["author"] == book_data["author"]
        assert seller_info["books"][i]["year"] == book_data["year"]
        assert seller_info["books"][i]["count_pages"] == book_data["count_pages"]


# Тест на ручку для обновления данных о продавце
@pytest.mark.asyncio
async def test_update_seller(async_client):
    # Создаем продавца для теста
    seller_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "password": "securepassword"
    }
    seller = await Seller.create(**seller_data)

    # Подготавливаем данные для обновления продавца
    updated_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "janesmith@example.com"
    }

    # Отправляем PUT-запрос на обновление данных о продавце
    response = await async_client.put(f"/sellers/{seller.id}", json=updated_data)

    assert response.status_code == 200
    updated_seller_info = response.json()

    # Проверяем корректность обновленных данных о продавце
    assert updated_seller_info["id"] == seller.id
    assert updated_seller_info["first_name"] == updated_data["first_name"]
    assert updated_seller_info["last_name"] == updated_data["last_name"]
    assert updated_seller_info["email"] == updated_data["email"]

    # Проверяем, что пароль не возвращается в данных о продавце
    assert "password" not in updated_seller_info

    # Проверяем, что данные о книгах продавца также были обновлены
    for book_info in updated_seller_info["books"]:
        assert book_info["seller_id"] == seller.id

    # Проверяем, что данные в базе данных действительно обновились
    updated_seller = await Seller.get(seller.id)
    assert updated_seller.first_name == updated_data["first_name"]
    assert updated_seller.last_name == updated_data["last_name"]
    assert updated_seller.email == updated_data["email"]


# Тест на ручку для обновления данных о продавце
@pytest.mark.asyncio
async def test_delete_seller(async_client):
    # Создаем продавца для теста
    seller_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "password": "securepassword"
    }
    seller = await Seller.create(**seller_data)

    # Подготавливаем данные для удаления продавца
    delete_data = {
        "id": seller.id,
        "email": seller.email
    }

    # Отправляем DELETE-запрос на удаление продавца
    response = await async_client.delete("/sellers/", json=delete_data)

    assert response.status_code == 200
    response_data = response.json()

    # Проверяем успешное удаление продавца и связанных с ним книг
    assert response_data["message"] == "Seller and associated books deleted successfully"

    # Проверяем, что продавец больше не существует в базе данных
    deleted_seller = await Seller.get(seller.id)
    assert deleted_seller is None

    # Проверяем, что все книги продавца также были удалены
    associated_books = await Book.query.where(Book.seller_id == seller.id).gino.all()
    assert len(associated_books) == 0