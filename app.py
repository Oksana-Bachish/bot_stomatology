import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker

from handlers.user_group import user_group_router
from handlers.user_private import user_private_router
from handlers.admin_private import admin_router

session = AiohttpSession()
bot = Bot(token=os.getenv('TOKEN', default=DefaultBotProperties(parse_mode=ParseMode.HTML)), session=session)     #parse_mode - добавляет редактирвание текста
admins = os.getenv("ADMINS", "")
bot.my_admins_list = [int(x) for x in admins.split(",") if x]  # -  список администраторов бота

dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)  # Dispatcher() - главный роутер, отвечает за фильтрацию всех событий, приходящих к боту

dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def on_startup(bot):
    # await drop_db()  # Удаляем БД
    await create_db()  # Создааем БД


async def on_shutdown(bot):
    await bot.session.close()
    print('Бот лёг')


async def main():
    dp.startup.register(on_startup)  # действия, при запуске бота
    dp.shutdown.register(on_shutdown)  # действия, при остановке бота
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)  # пропускает обновления, когда бот не был онлайн
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())  # запускает работу бота


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')

