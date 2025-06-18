from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_info_pages, orm_change_banner_image, orm_get_services, \
    orm_get_dentists, orm_delete_dentist, orm_update_dentist, orm_add_dentist, orm_change_service_image, orm_get_dentist
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Добавить специалиста',
    'Удалить/Изменить информацию о специалисте',
    'Добавить/Изменить изображение услуги',
    "Добавить/Изменить баннер",
    placeholder='Выберите действие',
    sizes=(2,),
)


class AddDentist(StatesGroup):
    name = State()
    education = State()
    medical_category = State()
    service = State()
    professional_skills = State()
    image = State()

    dentist_for_change = None

    texts = {
        'AddProduct:name': 'Введите имя заново:',
        'AddProduct:education': 'Введите образование заново:',
        'AddProduct:medical_category': 'Введите категорию заново:',
        "AddProduct:service": "Выберите услугу  заново ⬆️",
        'AddProduct:professional_skills': 'Введите профессиональные навыки заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...:',
    }


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('Что Вы хотите сделать?', reply_markup=ADMIN_KB)


############## Удалить/Изменить информацию о специалисте ##############
@admin_router.message(F.text == 'Удалить/Изменить информацию о специалисте')
async def admin_features(message: types.Message, session: AsyncSession):
    services = await orm_get_services(session)
    btns = {service.name: f'service_{service.id}' for service in services}
    await message.answer("Выберите услугу: ", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('service_'))
async def starring_at_dentist(callback: types.CallbackQuery, session: AsyncSession):
    service_id = callback.data.split('_')[-1]
    for dentist in await orm_get_dentists(session, int(service_id)):
        await callback.message.answer_photo(
            dentist.image,
            caption=f"{dentist.name}\n"
                    f"{dentist.education}\n"
                    f"{dentist.medical_category}"
                    f"Оказываемые услуги: {dentist.professional_skills}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить": f"delete_{dentist.id}",
                    "Изменить": f"change_{dentist.id}",
                },
                sizes=(2,)
            ),
        )
    await callback.answer()
    await callback.message.answer("ОК, вот список специалистов ⏫")


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_dentist_callback(callback: types.CallbackQuery, session: AsyncSession):
    dentist_id = callback.data.split('_')[-1]  # получаем id специалиста
    await orm_delete_dentist(session, int(dentist_id))
    await callback.answer('Специалист удален')
    await callback.message.answer('Специалист удален!')


@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    dentist_id = callback.data.split('_')[-1]
    dentist_for_change = await orm_get_dentist(session, int(dentist_id))
    AddDentist.dentist_for_change = dentist_for_change
    await callback.answer()
    await callback.message.answer('Введите имя специалиста', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddDentist.name)


############## Микро FSM для загрузки/изменения баннеров ##############
class AddBanner(StatesGroup):
    image = State()


@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить баннер')
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f'Отправьте фото баннера. \n В описании укажите для какой страницы: \n {", ".join(pages_names)}')
    await state.set_state((AddBanner.image))


# Добавляем/изменяем изображение баннера
@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите верное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Баннер добавлен/изменен.")
    await state.clear()


# ловим некоррекный ввод
@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message):
    await message.answer("Отправьте фото баннера или отмена")


############## Микро FSM для изменения изображения услуг ##############
class AddService(StatesGroup):
    image = State()


@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить изображение услуги')
async def add_service_image(message: types.Message, state: FSMContext, session: AsyncSession):
    service_names = [service.name for service in await orm_get_services(session)]
    await message.answer(f'Отправьте фото услуги. \n В описании укажите для какой страницы: \n {", ".join(service_names)}')
    await state.set_state(AddService.image)


# Добавляем/изменяем изображение услуги
@admin_router.message(AddService.image, F.photo)
async def add_service(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [service.name for service in await orm_get_services(session)]
    if for_page not in pages_names:
        await message.answer(f"Введите верное название страницы, например:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_service_image(session, for_page, image_id,)
    await message.answer("Фото услуги добавлено/изменено.")
    await state.clear()


############## Микро FSM для добавления/изменения данных о специалисте ##############
@admin_router.message(StateFilter(None), F.text == 'Добавить специалиста')  # StateFilter(None) - проверяем, что у пользователя нет активных состояний
async def add_dentist(message: types.Message, state: FSMContext):
    await message.answer('Введите Имя врача', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddDentist.name)  # шаг 1. становимся в ожидание, когда пользователь введет имя специалиста


# Обрабатываем команду 'отмена'
@admin_router.message(StateFilter('*'), F.text.casefold() == 'отмена')   # ('*') - любое состояние пользователя
async def chancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:     # если нет активного диалога (состояния), завершаем
        return
    if AddDentist.dentist_for_change:
        AddDentist.dentist_for_change = None
    await state.clear()  # если активное состояние есть, очищаем
    await message.answer('Действия отменены', reply_markup=ADMIN_KB)


# Обрабатываем команду 'назад'
@admin_router.message(StateFilter('*'), Command('назад'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def chancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()    # получаем текущее состояние
    if current_state == AddDentist.name:
        await message.answer('Предыдущего шага нет, или введите имя специалиста или напишите - отмена')
        return
    previous = None  # название предыдущего state
    for step in AddDentist.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)  # устанавливаем значение previous
            await message.answer(f'Ок, Вы вернулись к прошлому шагу \n {AddDentist.texts[previous.state]}')
            return
        previous = step

    await message.answer('Ок, вы вернулись к прошлому шагу')


@admin_router.message(AddDentist.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == '.' and AddDentist.dentist_for_change:  # если админ вводит . - то сохраняется старое значение
        await state.update_data(name=AddDentist.dentist_for_change.name)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer('Имя врача не должно превышать 150 символов. \n Введите заново')
            return

        await state.update_data(name=message.text)
    await message.answer('Введите учреждение образования, которое окончил специалист')
    await state.set_state(AddDentist.education)  # шаг 2. становимся в ожидание, когда пользователь введет учреждение образования специалиста


@admin_router.message(AddDentist.name)  # убираем все фильтры, кроме фильтра состояния, на тот случай, если пользователь ввел не текст
async def add_name(message: types.Message):
    await message.answer('Вы ввели не допустимые данные, введите имя специалиста')


@admin_router.message(AddDentist.education, F.text)
async def add_education(message: types.Message, state: FSMContext):
    if message.text == '.' and AddDentist.dentist_for_change:
        await state.update_data(education=AddDentist.dentist_for_change.education)
    else:
        if 5 >= len(message.text):
            await message.answer('Слишком короткое название. \n Введите заново')
            return
        await state.update_data(education=message.text)
    await message.answer('Введите квалификационную категорию специалиста')
    await state.set_state(AddDentist.medical_category)  # шаг 3. становимся в ожидание, когда пользователь введет квалификационную категорию специалиста


@admin_router.message(AddDentist.education)
async def add_education(message: types.Message):
    await message.answer('Вы ввели не допустимые данные, введите характеристику специалиста')


@admin_router.message(AddDentist.medical_category, F.text)
async def add_medical_category(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.' and AddDentist.dentist_for_change:
        await state.update_data(medical_category=AddDentist.dentist_for_change.medical_category)
    else:
        if 5 >= len(message.text):
            await message.answer('Слишком короткое название. \n Введите заново')
            return
        await state.update_data(medical_category=message.text)
    services = await orm_get_services(session)
    btns = {service.name: str(service.id) for service in services}
    await message.answer("Выберите услугу", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddDentist.service)  # шаг 4. становимся в ожидание, когда пользователь введет услуги, которые оказывает специалист


@admin_router.message(AddDentist.medical_category)
async def add_medical_category(message: types.Message):
    await message.answer('Вы ввели не допустимые данные, введите квалификационную категорию специалиста')


@admin_router.callback_query(AddDentist.service)
async def category_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [service.id for service in await orm_get_services(session)]:
        await callback.answer()
        await state.update_data(service=callback.data)
        await callback.message.answer('Теперь введите профессиональные навыки специалиста.')
        await state.set_state(AddDentist.professional_skills)  # шаг 5. становимся в ожидание, когда пользователь введет профессиональные навыки специалиста
    else:
        await callback.message.answer('Выберите услугу из кнопок.')
        await callback.answer()


#Ловим любые некорректные действия, кроме нажатия на кнопку выбора категории
@admin_router.message(AddDentist.service)
async def category_choice2(message: types.Message):
    await message.answer("Выберите услугу из кнопок.")


@admin_router.message(AddDentist.professional_skills, F.text)
async def add_professional_skills(message: types.Message, state: FSMContext):
    if message.text == '.' and AddDentist.dentist_for_change:
        await state.update_data(professional_skills=AddDentist.dentist_for_change.professional_skills)
    else:
        await state.update_data(professional_skills=message.text)
    await message.answer('Загрузите фото специалиста')
    await state.set_state(AddDentist.image)   # шаг 6. становимся в ожидание, когда пользователь загрузит фото специалиста


@admin_router.message(AddDentist.professional_skills)
async def add_professional_skills(message: types.Message):
    await message.answer('Вы ввели не допустимые данные, введите цену услуги')


@admin_router.message(AddDentist.image, or_f(F.photo, F.text == '.'))
async def add_image(message: types.Message, state: FSMContext, session:
                    AsyncSession):
    if message.text and message.text == '.':
        await state.update_data(image=AddDentist.dentist_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()     # получаем словарь с данными
    try:
        if AddDentist.dentist_for_change:
            await orm_update_dentist(session, AddDentist.dentist_for_change.id, data)
        else:
            await orm_add_dentist(session, data)
        await message.answer('Специалист добавлен/изменен', reply_markup=ADMIN_KB)
        await state.clear()     # очищаем состояние пользователя и удаляем все данные из машины состояний
    except Exception as e:
        await message.answer(
            f'Ошибка: \n{str(e)}\n Обратитесь к программисту для устранения неполадок', reply_markup=ADMIN_KB
        )
        await state.clear()
    AddDentist.dentist_for_change = None
