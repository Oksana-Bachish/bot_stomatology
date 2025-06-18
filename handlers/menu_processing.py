from aiogram.enums import ParseMode
from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_banner, orm_get_services, orm_get_dentists, set_user, orm_get_service
from kbds.inline import get_user_main_btns, get_dentists_btns, \
    get_user_service_btns, get_user_services_btns
from utils.paginator import Paginator


# Баннер главного меню
async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    kbds = get_user_main_btns(level=level)
    return image, kbds


# Баннер услуг
async def services_list(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=str(banner.image), caption=banner.description)
    services = await orm_get_services(session)
    kbds = get_user_services_btns(level=level, services=services)
    return image, kbds


# Баннер выбранной услуги
async def service_info(session, level, service):
    service = await orm_get_service(session, service_id=service)
    kbds = get_user_service_btns(level=level, service=service)
    image = InputMediaPhoto(
        media=service.image,
        caption=f'<b>{service.name}'
                f'</b>\n{service.description}\n', parse_mode=ParseMode.HTML
    )
    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns['◀Пред.'] = 'previous'
    if paginator.has_next():
        btns['След.▶'] = 'next'
    return btns


# Баннер с информацией о специалисте
async def dentists(session, level, service, page):
    dentists_all = await orm_get_dentists(session, service_id=service)
    paginator = Paginator(dentists_all, page=page)
    dentist = paginator.get_page()[0]
    image = InputMediaPhoto(
        media=dentist.image,
        caption=f'<strong>{dentist.name}</strong>\n'
                f'<em>Образование: </em> {dentist.education}\n'
                f'<em>Квалификационная категория: </em>{dentist.medical_category}\n'
                f'<em>Оказываемые услуги: </em>{dentist.professional_skills}\n'
                f'<strong>Специалист {paginator.page} из {paginator.pages}</strong>', parse_mode=ParseMode.HTML
    )
    pagination_btns = pages(paginator)

    kbds = get_dentists_btns(
        level=level,
        service=service,
        page=page,
        pagination_btns=pagination_btns,
        dentist_id=dentist.id,
    )

    return image, kbds


async def get_menu_content(session: AsyncSession,
                           level: int,
                           menu_name: str,
                           service: int |None = None,
                           page: int | None = None,
                           dentist_id: int | None = None,
                           user_id: int | None = None,
                           ):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await services_list(session, level, menu_name)
    elif level == 2:
        return await service_info(session, level, service)
    elif level == 3:
        return await dentists(session, level, service, page)
