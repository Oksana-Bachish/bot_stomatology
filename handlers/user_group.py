from aiogram import  types, Router, Bot
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))     # обрабатываем работу бота в группах и супергруппах
user_group_router.edited_message.filter(ChatTypeFilter(['group', 'supergroup']))     # обрабатываем работу бота в группах и супергруппах, отредактированные сообщения


@user_group_router.message(Command('admin'))
async def get_admin(message: types.Message, bot: Bot):
    chat_id = message.chat.id         # получаем ИД чата
    admins_list = await bot.get_chat_administrators(chat_id)  # получаем список участников 'creator' и 'administrator' в чате
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == 'creator' or member.status == 'administrator'
    ]  # получаем список id из creator и admin
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:   # если это админ, удаляем команду admin в чате
        await message.delete()
