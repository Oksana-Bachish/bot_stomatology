from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


contact = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить контакт', request_contact=True)]],
                              resize_keyboard=True, input_field_placeholder='Нажмите кнопку ниже')

registration = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Зарегистрироваться')]], resize_keyboard=True,
                                   one_time_keyboard=True)

select_date = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Календарь')]], resize_keyboard=True,
                                  one_time_keyboard=True)


def get_keyboard(
        *btns: str,
        placeholder: str = None,
        sizes: tuple[int, int, int] = (2, ),
):
    keyboard = ReplyKeyboardBuilder()
    for index, text in enumerate(btns, start=0):
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )
