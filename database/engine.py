import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.models import Base
from database.orm_query import orm_add_banner_description, orm_create_services

from common.texts_for_db import description_for_info_pages, about_service

engine = create_async_engine(os.getenv('DB_URL'), echo=True)  # подключение PostgreSQL созд. движок

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # expire_on_commit=False - возможность использования сессии повторно, чтобы она не закрывалась


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создает все таблицы в БД

    async with session_maker() as session:
        await orm_create_services(session, about_service)
        await orm_add_banner_description(session, description_for_info_pages)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # удаляет все таблицы из БД
