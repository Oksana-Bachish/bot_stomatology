from aiogram.filters import Filter
from aiogram import types, Bot


# Фильтр типов чатов
class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:  # передаем список из типов чатов в которых будет работать роутер
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


#  Фильтр для проверки на администратора
class IsAdmin(Filter):
    def __init__(self):
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.my_admins_list   # получаем id пользователя, который пишет боту, и проверяет, есть ли он в списке админов. bot.my_admins_list - из app.py
