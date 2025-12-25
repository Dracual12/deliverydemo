import asyncio
import logging
from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.DEBUG)  # Включи дебаг!

bot = Bot(token="8384631612:AAH2yPnSaCTXWLfdex8Ia12_Y21LZkxsd5g")
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    import time
    start = time.time()
    await message.answer(f"Тест: {time.time() - start:.2f}с")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
