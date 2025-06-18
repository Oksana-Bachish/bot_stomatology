from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: str
    service: int | None = None
    page: int = 1
    dentist_id: int | None = None


# Баннер главного меню
def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Услуги 🦷": "services",
        "Специалисты 👩‍⚕️": "dentists",
        "О нас ℹ️": "about",
        "Контакты/адрес ☎": "contact",
    }
    for text, menu_name in btns.items():
        if menu_name == 'services':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


# Баннер услуг
def get_user_services_btns(*, level: int, services: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=level - 1, menu_name='main').pack()))
    for c in services:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level + 1, menu_name=c.name,
                                                                     service=c.id).pack()))
    return keyboard.adjust(*sizes).as_markup()


# Баннер выбранной услуги
def get_user_service_btns(*, level: int, service, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=1, menu_name='services').pack()))
    keyboard.add(InlineKeyboardButton(text='Выбрать специалиста',
                                      callback_data=MenuCallBack(level=3, menu_name=service.name,
                                                                 service=service.id).pack()))
    return keyboard.adjust(*sizes).as_markup()


# Баннер с информацией о специалисте
def get_dentists_btns(
        *,
        level: int,
        service: int,
        page: int,
        pagination_btns: dict,
        dentist_id: int,
        sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Назад',
                                      callback_data=MenuCallBack(level=1, menu_name='services').pack()))
    keyboard.add(InlineKeyboardButton(text='Записаться к специалисту 🗓',
                                      callback_data=MenuCallBack(level=level, menu_name='reserve',
                                                                 dentist_id=dentist_id).pack()))
    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                service=service,
                                                page=page + 1).pack()))
        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                service=service,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


# Завершение записи
end_recording = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ok', callback_data='end_recording')]], one_time_keyboard=True)


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()
