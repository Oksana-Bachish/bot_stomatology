import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from handlers.user_private import reg_first_name, Register, reg_contact, recording

@pytest.mark.asyncio
async def test_reg_first_name_invalid_data():
    """Тест валидации: имя содержит цифры и не должно быть сохранено"""

    mock_message = AsyncMock(spec=Message)
    mock_message.text = "Иван123"
    mock_message.answer = AsyncMock()

    mock_state = AsyncMock(spec=FSMContext)

    await reg_first_name(mock_message, mock_state)

    # Проверяем ответ пользователю и блокировку стейта
    mock_message.answer.assert_called_once_with(
        'Введите корректные данные (только буквенные значения)'
    )

    assert not mock_state.update_data.called
    assert not mock_state.set_state.called


@pytest.mark.asyncio
async def test_reg_first_name_success():
    """Тест успешной валидации: имя корректно, стейт обновлен"""

    mock_message = AsyncMock(spec=Message)
    mock_message.text = 'Александр'
    mock_message.answer = AsyncMock()

    mock_state = AsyncMock(spec=FSMContext)

    await reg_first_name(mock_message, mock_state)

    # Проверяем сохранение данных и переход на следующий шаг FSM
    mock_state.update_data.assert_called_once_with(first_name='Александр')
    mock_message.answer.assert_called_once_with('Введите фамилию')
    mock_state.set_state.assert_called_once_with(Register.last_name)


@pytest.mark.asyncio
async def test_reg_contact_success(mocker):
    """Тест успешного финала регистрации: данные пользователя сохраняются в БД."""

    # Изолируем функцию ORM от реальной базы данных
    mock_orm_update = mocker.patch('handlers.user_private.orm_update_user', new_callable=AsyncMock)

    # Имитируем входящее сообщение со вложенными структурами Telegram
    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()
    mock_message.contact = MagicMock()
    mock_message.contact.phone_number = '+79991112233'
    mock_message.from_user = MagicMock()
    mock_message.from_user.id = 123456789

    # Имитируем сохраненные на прошлых шагах FSM данные
    mock_state = AsyncMock(spec=FSMContext)
    mock_state.get_data.return_value = {
        'first_name': 'Александр',
        'last_name': 'Иванов',
        'contact': '+79991112233'
    }

    mock_session = AsyncMock()

    # Запуск тестируемого хэндлера
    await reg_contact(mock_message, mock_state, mock_session)

    # Проверка извлечения данных, вызова ORM и очистки стейта
    assert mock_state.get_data.called
    mock_orm_update.assert_called_once_with(
        mock_session,
        123456789,
        {'first_name': 'Александр', 'last_name': 'Иванов', 'contact': '+79991112233'}
    )
    assert mock_state.clear.called
    mock_message.answer.assert_any_call('Нажмите на кнопку "Календарь" для выбора даты', reply_markup=mocker.ANY)


@pytest.mark.asyncio
async def test_recording_success(mocker):
    '''Тест успешной записи на прием и вызова генерации JSON'''

    # Мокаем функции базы данных и утилиту записи JSON, чтобы изолировать тест
    mock_get_reserve = mocker.patch('handlers.user_private.get_reserve', new_callable=AsyncMock)
    mock_remove_reserve = mocker.patch('handlers.user_private.remove_reserve', new_callable=AsyncMock)
    mock_get_json = mocker.patch('handlers.user_private.get_json', new_callable=AsyncMock)

    # Настраиваем фейковый возврат из базы (объекты юзера, врача и брони)
    mock_user = MagicMock(first_name='Иван', last_name='Петров', phone='+79991112233')
    mock_dentist = MagicMock(name='Д-р Смирнов')
    mock_result = MagicMock(date='30/10/2026')
    mock_get_reserve.return_value = (mock_user, mock_dentist, mock_result)

    # Имитируем нажатие кнопки (CallbackQuery) от пользователя
    mock_callback = AsyncMock()
    mock_callback.from_user = MagicMock()
    mock_callback.from_user.id = 987654321

    mock_callback.message = AsyncMock()
    mock_callback.message.answer = AsyncMock()
    mock_callback.answer = AsyncMock()

    mock_session = AsyncMock()

    # Запускаем хэндлер
    await recording(mock_callback, mock_session)

    assert mock_remove_reserve.called
    assert mock_get_json.called

    # Проверяем, что бот отправил пользователю финальный текст
    mock_callback.message.answer.assert_called_once_with(
        'Ваш запрос принят. Скоро наш администратор свяжется с Вами для уточнения деталей записи'
    )
    assert mock_callback.answer.called
