import json
import os
import string
import locale
from datetime import datetime
from dateutil.relativedelta import relativedelta

from aiogram import F, types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

from database.orm_query import set_user, add_to_reserve, get_reserve, update_to_reserve, \
    remove_reserve, orm_update_user
from filters.chat_types import ChatTypeFilter

from handlers.menu_processing import get_menu_content
from kbds.inline import MenuCallBack, get_callback_btns
from kbds.reply import contact, select_date

user_private_router = Router()
user_private_router.message.filter(
    ChatTypeFilter(['private']))  # Фильтр из chat_types.py. Роутер будет работать только на личку


class Register(StatesGroup):
    first_name = State()
    last_name = State()
    contact = State()


class AppointmentDate(StatesGroup):
    date = State()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')
    await message.answer_photo(media.media, caption=media.caption,
                               reply_markup=reply_markup)


############## Запись к специалисту ################
async def reserve(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession, state: FSMContext):
    await callback.answer()
    user = await set_user(session, tg_id=callback.from_user.id)
    await add_to_reserve(session, user_id=callback.from_user.id, dentist_id=callback_data.dentist_id, date=None)
    if not user:  # если пользователь не зарегистрирован, производим регистрацию
        await get_registration(callback, state)
    else:
        await callback.message.answer(f'Подтведите Ваши личные данные: {user.first_name.capitalize()} '
                                          f'{user.last_name.capitalize()}. \nНомер телефона: {user.phone}',
                                          reply_markup=get_callback_btns(
                                              btns={
                                                  "Все верно": "correct_user_data",
                                                  "Изменить": f"change_user_data",
                                              }, sizes=(2,)),)


@user_private_router.callback_query(F.data.startswith('correct_user_data'))
async def get_correct_data(callback: CallbackQuery):
    await callback.message.answer('Данные подтверждены. '
                                  'Нажмите на кнопку "Календарь" для выбора даты записи', reply_markup=select_date)
    await callback.answer()


@user_private_router.callback_query(StateFilter(None), F.data.startswith('change_user_data'))
async def change_user_data(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите Ваше имя: ',
                                  reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Register.first_name)


############## Регистрация пользователя ################
async def get_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Для записи пройдите регистрацию.')
    await register(callback, state)


@user_private_router.message(F.text == 'Зарегистрироваться')
async def register(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите Ваше имя:', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Register.first_name)


@user_private_router.message(Register.first_name, F.text)
async def reg_first_name(message: Message, state: FSMContext):
    symbols = string.digits + string.punctuation
    symbols = symbols.replace('-', '')
    if len(message.text) > 20 or any(i in symbols for i in message.text):
        await message.answer('Введите корректные данные (только буквенные значения)')
        return
    await state.update_data(first_name=message.text)
    await message.answer('Введите фамилию')
    await state.set_state(Register.last_name)


@user_private_router.message(Register.last_name, F.text)
async def reg_last_name(message: Message, state: FSMContext):
    symbols = string.digits + string.punctuation
    symbols = symbols.replace('-', '')
    if len(message.text) > 20 or any(i in symbols for i in message.text):
        await message.answer('Введите корректные данные (только буквенные значения)')
        return
    await state.update_data(last_name=message.text)
    await message.answer('Отправьте номер телефона', reply_markup=contact)
    await state.set_state(Register.contact)


@user_private_router.message(Register.contact, F.contact)
async def reg_contact(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(contact=message.contact.phone_number)
    data = await state.get_data()
    await orm_update_user(session, message.from_user.id, data)
    await message.answer(f'Ваши данные успешно сохранены.', reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await message.answer('Нажмите на кнопку "Календарь" для выбора даты', reply_markup=select_date)


@user_private_router.message(Register.contact)
async def reg_contact_manual(message: Message, state: FSMContext, session: AsyncSession):
    phone = message.text.strip()
    if not phone.startswith('+') or len(phone) < 10:
        await message.answer('Введите корректный номер телефона')
        return
    await state.update_data(contact=phone)
    data = await state.get_data()
    await orm_update_user(session, message.from_user.id, data)
    await message.answer('Ваши данные успешно сохранены.', reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await message.answer('Нажмите на кнопку "Календарь" для выбора даты', reply_markup=select_date)


################### Календарь для выбора даты записи ####################
@user_private_router.message(F.text.lower() == 'календарь')
async def nav_cal_handler_date(message: Message, state: FSMContext):
    calendar = SimpleCalendar(
        locale=locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8'), show_alerts=True
    )
    calendar.set_dates_range(datetime.now(), datetime.now() + relativedelta(months=+1))
    await message.answer(
        "Пожалуйста, выберите дату: ",
        reply_markup=await calendar.start_calendar(year=datetime.now().year, month=datetime.now().month)
    )
    await state.set_state(AppointmentDate.date)


@user_private_router.callback_query(AppointmentDate.date, SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback,
                                  state: FSMContext, session: AsyncSession):
    calendar = SimpleCalendar(
        locale=locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8'), show_alerts=True
    )
    calendar.set_dates_range(datetime.now(), datetime.now() + relativedelta(months=+1))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Вы выбрали {date.strftime("%d/%m/%Y")}', reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(date=date.strftime("%d/%m/%Y"), user_id=callback_query.from_user.id)
        await update_to_reserve(session, callback_query.from_user.id, date.strftime("%d/%m/%Y"))
        await state.clear()
        await completes_recording(callback_query, session)


################### Обработка данных записи ###################
async def completes_recording(callback: CallbackQuery, session: AsyncSession):
    user_info, dentist, result = await get_reserve(session, user_id=callback.from_user.id)
    await callback.message.answer(f'Подтвердите введенные данные. Запись для {user_info.first_name.capitalize()} '
                                  f'{user_info.last_name.capitalize()}. \nВрач: {dentist.name}. Дата: {result.date}',
                                  reply_markup=get_callback_btns(
                                      btns={
                                          "Все верно": "ok",
                                          "Отмена": "canceling",
                                      },
                                      sizes=(2,)
                                  ),)


@user_private_router.callback_query(F.data.startswith('ok'))
async def recording(callback: CallbackQuery, session: AsyncSession):
    user_info, dentist, result = await get_reserve(session, user_id=callback.from_user.id)
    reservetion_data = []
    reservetion_data.append({f'Reserve': {
        'Пациент': f'{user_info.first_name.capitalize()} {user_info.last_name.capitalize()}',
        'id пациента': callback.from_user.id,
        'Номер телефона пациента': f'{user_info.phone}',
        'Врач': f'{dentist.name}',
        'Дата приема': f'{result.date}',
        'Дата и время записи': datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
    }, )
    await remove_reserve(session, user_id=callback.from_user.id)
    await get_json(reservetion_data)
    await callback.message.answer(
        f'Ваш запрос принят. Скоро наш администратор свяжется с Вами для уточнения деталей записи')
    await callback.answer()


@user_private_router.callback_query(F.data.startswith('canceling'))
async def canceling_appointment(callback: CallbackQuery):
    await callback.message.answer(
        f'Запись отменена. Чтобы начать заново, нажмите \t /start')
    await callback.answer()


################### Запись данных в json ####################
async def get_json(reservetion_data):
    try:
        with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/json_files/reservetion_data.json',
                  encoding='utf-8') as file:
            data = json.load(file)
            data.append(reservetion_data[0])
        await save_json(data)
    except FileNotFoundError:
        await save_json(reservetion_data)


async def save_json(data):
    with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/json_files/reservetion_data.json',
              'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


################### Завершение записи пользователя ####################
@user_private_router.callback_query(F.data.startswith('end_recording'))
async def recording(callback: CallbackQuery, ):
    await callback.message.answer(
        f'Ваш запрос принят. Скоро наш администратор свяжется с Вами для уточнения деталей записи')


############################### Получаем клавиатуру пользователя #################################
@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession, state: FSMContext):
    if callback_data.menu_name == 'reserve':
        await reserve(callback, callback_data, session, state)
        return  # выходим из хендлера
    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        service=callback_data.service,
        page=callback_data.page,
        dentist_id=callback_data.dentist_id,
        user_id=callback.from_user.id,
    )
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
