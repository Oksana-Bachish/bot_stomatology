from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Banner, User, Service, Dentist, Reserve


# Работа с баннерами
async def orm_add_banner_description(session: AsyncSession, data: dict):
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


# Услуги
async def orm_get_services(session: AsyncSession):
    query = select(Service)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_create_services(session: AsyncSession, services: dict):
    query = select(Service)
    result = await session.execute(query)
    if result.first():   # если категория существует - выходим
        return
    session.add_all([Service(name=name, description=description) for name, description in services.items()])  # если категорий нет, сохраняем
    await session.commit()


async def orm_get_service(session: AsyncSession, service_id):
    query = select(Service).where(Service.id == int(service_id))
    result = await session.execute(query)
    return result.scalar()


async def orm_change_service_image(session: AsyncSession, name: str, image: str):
    query = update(Service).where(Service.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


# Админ-панель: добавить/изменить/удалить врача
async def orm_add_dentist(session: AsyncSession, data: dict):
    obj = Dentist(
        name=data['name'],
        education=data['education'],
        medical_category=data['medical_category'],
        professional_skills=data['professional_skills'],
        image=data['image'],
        service_id=int(data['service']))
    session.add(obj)
    await session.commit()


async def orm_get_dentists(session: AsyncSession, service_id):
    query = select(Dentist).where(Dentist.service_id == int(service_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_dentist(session: AsyncSession, dentist_id: int):
    query = select(Dentist).where(Dentist.id == dentist_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_dentist(session: AsyncSession, dentist_id: int, data):
    query = update(Dentist).where(Dentist.id == dentist_id).values(
        name=data['name'],
        education=data['education'],
        medical_category=data['medical_category'],
        professional_skills=data['professional_skills'],
        image=data['image'],
        service_id=int(data['service']))
    await session.execute(query)
    await session.commit()


async def orm_delete_dentist(session: AsyncSession, dentist_id: int):
    query = delete(Dentist).where(Dentist.id == dentist_id)
    await session.execute(query)
    await session.commit()


# Работа с данными пользователя
async def orm_update_user(session: AsyncSession, tg_id: int, data: dict):
    query = update(User).where(User.tg_id == tg_id).values(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['contact'],
    )
    await session.execute(query)
    await session.commit()


async def set_user(session: AsyncSession, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        session.add(User(tg_id=tg_id))
        await session.commit()
        return False
    else:
        return user


# Запись на прием
async def add_to_reserve(session: AsyncSession, user_id: int, dentist_id: int, date: str | None):
    session.add(Reserve(user_id=user_id, dentist_id=dentist_id, date=date))
    await session.commit()


async def update_to_reserve(session: AsyncSession, user_id: int, date: str):
    query = update(Reserve).where(Reserve.user_id == user_id).values(date=date)
    await session.execute(query)
    await session.commit()


async def get_reserve(session: AsyncSession, user_id):
    dentist = await session.scalar(select(Dentist).join(Reserve, Dentist.id == Reserve.dentist_id))
    user = await session.scalar(select(User).join(Reserve, User.tg_id == Reserve.user_id))
    query = select(Reserve).where(Reserve.user_id == user_id)
    result = await session.execute(query)
    return user, dentist, result.scalar()


async def orm_get_user_reserve(session: AsyncSession, user_id):
    query = select(Reserve).where(Reserve.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def remove_reserve(session, user_id):
    await session.execute(delete(Reserve).where(Reserve.user_id == user_id))
    await session.commit()


