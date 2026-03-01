import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


# ================= НАСТРОЙКИ =================

TOKEN = "7741414989:AAGaklBk54Q5kIecAd49CuDvcHgG_XPoqEE"  # ВСТАВЬ СВОЙ ТОКЕН

BOY_ID = 1989532058  # его Telegram ID
GIRL_ID = 5522901826  # твой Telegram ID

# =============================================

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Состояние квеста
current_day = 1
started = False

# Загадки (даты с 1 по 7 марта 2026 года)
riddles = {
    1: {
        "date": "2026-03-01",
        "question": "Привет, мой герой! 🥷🏼\n\n"
                    "С 1 марта начинается твой праздничный квест 🎊\n"
                    "Каждый день новая загадка и кусочек адреса.\n\n"
                    "Готов? ❤️\n\n"
                    "Загадка дня:\n"
                    "Я есть у каждого, но не каждый умеет мной пользоваться.\n"
                    "Ты включаешь меня в нужный момент?\n\n"
                    "Ответ напиши одним словом.",
        "answer": "мозг",
        "address_part": "Пушкинский р-н,"
    },
    2: {
        "date": "2026-03-02",
        "question": "🎉 День 2\n\n"
                    "Я ускоряюсь, когда ты волнуешься или смотришь на меня.\n"
                    "Что это?",
        "answer": "сердце",
        "address_part": "пос. Шушары,"
    },
    3: {
        "date": "2026-03-03",
        "question": "🎉 День 3\n\n"
                    "Оно бывает раз в году.\n"
                    "Все его ждут.\n"
                    "И совсем скоро это наступит у тебя.\n"
                    "Что это?",
        "answer": "день рождения",
        "address_part": "территория Пулковское,"
    },
    4: {
        "date": "2026-03-04",
        "question": "🎉 День 4\n\n"
                    "Она появляется у меня на лице при виде тебя.\n"
                    "Что это?",
        "answer": "улыбка",
        "address_part": "Переведенская"
    },
    5: {
        "date": "2026-03-05",
        "question": "🎉 День 5\n\n"
                    "Как называется месяц, в котором ты родился?",
        "answer": "март",
        "address_part": "ул.,"
    },
    6: {
        "date": "2026-03-06",
        "question": "🎉 День 6\n\n"
                    "Их задувают, когда загадывают желания.\n"
                    "Что это?",
        "answer": "свечи",
        "address_part": "6Б"
    },
    7: {
        "date": "2026-03-07",
        "question": "🎉 Финал\n\n"
                    "Ты готов приехать за своим сюрпризом?\n"
                    "Напиши: готов",
        "answer": "готов",
        "address_part": "Жду тебя здесь, время уточню позже ❤️"
    }
}


# ================= ОБРАБОТЧИК /start =================

@dp.message(CommandStart())
async def start_handler(message: Message):
    global started, current_day

    if message.from_user.id == BOY_ID:
        started = True
        current_day = 1  # Сбрасываем день
        await message.answer(
            "Квест активирован 🥷🏼\n\n"
            "Первая загадка придёт сегодня в 14:00 🎊"
        )
        # Уведомляем девушку
        await bot.send_message(
            GIRL_ID,
            f"🎮 Квест начат! Сегодня 1 марта - первая загадка в 14:00"
        )
    else:
        await message.answer("Этот бот не для тебя 😉")


# ================= ПРОВЕРКА ОТВЕТОВ =================

@dp.message(F.text)
async def check_answer(message: Message):
    global current_day, started

    # Проверяем, что сообщение от нужного пользователя
    if message.from_user.id != BOY_ID:
        return

    if not started:
        await message.answer("Квест ещё не начат. Напиши /start")
        return

    if current_day > 7:
        await message.answer("🎉 Квест уже завершён! Спасибо за игру!")
        return

    if current_day not in riddles:
        return

    correct_answer = riddles[current_day]["answer"].lower().strip()
    user_answer = message.text.lower().strip()

    if user_answer == correct_answer:
        part = riddles[current_day]["address_part"]

        await message.answer(
            f"💫 Отлично! Ты разгадал загадку! ❤️\n\n"
            f"Держи кусочек пазла 🧩:\n\n{part}"
        )

        # Уведомляем девушку
        await bot.send_message(
            GIRL_ID,
            f"✅ Он ответил правильно на день {current_day} (марта)"
        )

        # Проверяем, не последний ли это день
        if current_day == 7:
            # Собираем полный адрес
            full_address = ''
            for d in range(1, 8):
                if d in riddles:
                    full_address += riddles[d]['address_part']
            
            await message.answer(
                "✨ И вот он — финал твоего праздничного квеста ✨\n\n"
                "Ты прошёл все загадки и собрал адрес ❤️\n\n"
                f"📍 <b>Полный адрес:</b>\n{full_address}"
            )
            
            # Уведомляем девушку о завершении
            await bot.send_message(
                GIRL_ID,
                f"🏆 Квест завершён! 7 марта - он собрал весь адрес:\n{full_address}"
            )

        current_day += 1

    else:
        await message.answer(
            "Почти… Подумай ещё ❤️"
        )


# ================= АВТО-ОТПРАВКА ЗАГАДОК =================

async def send_daily_riddle():
    """Отправляет загадку на текущий день"""
    global current_day, started
    
    today = datetime.now().strftime("%Y-%m-%d")
    current_date = datetime.now().strftime("%d.%m.%Y")
    logging.info(f"Проверка загадок на {today}")
    
    if not started:
        logging.info("Квест не активирован")
        return
    
    # Ищем загадку на сегодня
    for day, data in riddles.items():
        if data["date"] == today:
            if day <= 7:  # Проверяем, что день не превышает 7
                await bot.send_message(BOY_ID, data["question"])
                await bot.send_message(
                    GIRL_ID,
                    f"📨 Отправлена загадка на {current_date} (день {day})"
                )
                logging.info(f"Отправлена загадка на день {day}")
                return
    
    logging.info("На сегодня загадок нет")


# ================= КОМАНДА ДЛЯ ПРОВЕРКИ (ОПЦИОНАЛЬНО) =================

@dp.message(F.text == "/status")
async def status_command(message: Message):
    """Проверка статуса квеста (только для девушки)"""
    if message.from_user.id == GIRL_ID:
        today = datetime.now().strftime("%Y-%m-%d")
        await message.answer(
            f"📊 <b>Статус квеста:</b>\n\n"
            f"Активирован: {'✅' if started else '❌'}\n"
            f"Текущий день: {current_day}\n"
            f"Сегодня: {today}\n"
            f"Загадок всего: {len(riddles)}"
        )


# ================= ЗАПУСК =================

async def on_startup():
    """Действия при запуске бота"""
    logging.info("Бот запущен")
    # Отправляем уведомление девушке о запуске бота
    await bot.send_message(
        GIRL_ID,
        "🤖 Бот для квеста (1-7 марта) запущен и готов к работе!\n"
        "Используй /status для проверки состояния"
    )

async def on_shutdown():
    """Действия при остановке бота"""
    logging.info("Бот остановлен")
    await bot.send_message(
        GIRL_ID,
        "🔄 Бот остановлен"
    )

async def main():
    # Удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Настраиваем планировщик
    scheduler.add_job(
        send_daily_riddle,
        trigger=CronTrigger(hour=14, minute=0),  # Отправка в 14:00 каждый день
        id="daily_riddle",
        replace_existing=True
    )
    scheduler.start()
    logging.info("Планировщик запущен")
    
    # Уведомление о запуске
    await on_startup()
    
    try:
        # Запускаем поллинг
        await dp.start_polling(bot)
    finally:
        await on_shutdown()
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())