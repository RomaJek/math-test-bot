import asyncio
from aiogram import Bot, Dispatcher, types

async def main():
    bot = Bot(token="8477736057:AAGRRqacsHRO8gmGyObdNWy53xwYXcbUJPw") # Tokenińdi jaz
    dp = Dispatcher()

    @dp.message()
    async def echo(message: types.Message):
        await message.answer("Men islep turman!")

    print("Test bot iske tústi...")
    await dp.start_polling(bot)

asyncio.run(main())