import asyncio
import os
from dotenv import load_dotenv # .env faylın oqıw ushın
from aiogram import Bot, Dispatcher, types

# 1. .env ishindegi maǵlıwmatlardı júkleymiz
load_dotenv()

async def main():
    # 2. Tokendi qol menen jazbaymiz, bálki sistemadan alamız
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        print("QÁTE: .env faylından BOT_TOKEN tabılmadı!")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    @dp.message()
    async def echo(message: types.Message):
        # Oqıwshı ne jazsa, sonı qaytarıp beredi (Echo bot)
        await message.answer(f"Siz jazdıńız: {message.text}")

    print("Test bot iske tústi...")
    
    # skip_updates=True: Bot óshik waqıtta jiberilgen eski xabarlardı tastap jiberedi
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())