# main.py
import asyncio
import logging
import time
import random
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import Message
from aiogram.filters import CommandStart
import config

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(api=TelegramAPIServer.from_base(config.API_SERVER))
bot = Bot(token=config.BOT_TOKEN, session=session)
dp = Dispatcher()

# ТВОЙ ID (владелец)
OWNER_ID = 1780243499

# Список твоих фраз для троллинга
TROLL_RESPONSES = [
    "мать твою ебашил посудомойку ебаную",
    "сын пидора уткнул ебальник редко",
    "мать прихуярил твою тапку как комара",
    "твой батя надувной шар",
    "твой батя хуярит на толкане как из гидранта",
    "твой батя тряпка впитывающая в себя мочу",
    "сынок шлбхм стервозной"
]

# Твои фразы для команд
PHRASES = {
    ".п": "Че папе?",
    ".м": "Че маме?",
    ".д": "Че деду в ракету?",
    ".б": "Че бабушке в кастрюлю?",
    ".мам": "Че мамке в поварешку?",
    ".з": "Я в зеркальной броне, ты в зеркальном мире, на тебе клеймо лжи.",
    ".к": "Че кенту?",
    ".с": "Че сучке?",
    ".в": "Че вове?",
    ".я": "Че я?",
    ".х": "Че хомяку?",
}

# Слова-триггеры для автоответа
TRIGGER_WORDS = [
    "шлюхи", "шлюха", "сын", "пидора", "уебок", 
    "тупой", "пидор", "хуесос", "долбаеб", "тряпка", "тварь"
]

user_cooldowns = {}

# --- СТАРТ ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id == OWNER_ID:
        await message.reply(
            "👑 <b>Добро пожаловать, Владелец!</b>\n"
            "Вы имеете полный доступ к командам.\n\n"
            "💬 <b>Доступные команды:</b>\n"
            "• <code>.трольмод @юзер</code> — заспамить оскорблениями\n"
            "• <code>.п, .м, .д, .б, .мам, .з, .к, .с, .в, .я, .х</code> — твои фразы",
            parse_mode="HTML"
        )
    else:
        await message.reply("⛔ Доступ запрещен. Я работаю только для владельца.")

# --- ТРОЛЛЬМОД ---
@dp.message(F.text.lower().startswith(".трольмод"))
async def troll_mode(message: Message):
    # Доступ только владельцу
    if message.from_user.id != OWNER_ID:
        return

    # Получаем аргументы
    args = message.text.split()
    
    # Если написали .трольмод без юзернейма
    if len(args) < 2:
        await message.reply("⚠️ Укажи юзернейм: <code>.трольмод @username</code>", parse_mode="HTML")
        return
        
    target_username = args[1].replace("@", "")
    
    await message.reply(f"🔥 <b>Тролль-режим запущен на @{target_username}!</b>\nСейчас начну спамить.", parse_mode="HTML")
    
    # Начинаем спам всеми фразами по очереди
    for phrase in TROLL_RESPONSES:
        try:
            # Отправляем сообщение с тегом
            await message.answer(f"@{target_username}, {phrase}", parse_mode="HTML")
            # Ждем 0.5 секунды
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(f"Ошибка спама: {e}")
            # Если бот упал в бан, прекращаем
            break
            
    await message.answer(f"✅ Троллинг @{target_username} завершен.")

# --- ФРАЗЫ И АВТОТРОЛЛИНГ ---
@dp.message(F.text)
async def handler(message: Message):
    # 1. Логика для владельца (команды)
    if message.from_user.id == OWNER_ID:
        text = message.text.lower().strip()
        
        # Кулдаун 0.5 сек для команд
        now = time.time()
        if message.from_user.id in user_cooldowns:
            if now - user_cooldowns[message.from_user.id] < 0.5:
                return
        user_cooldowns[message.from_user.id] = now

        if text in PHRASES:
            try:
                await message.reply(PHRASES[text])
            except Exception as e:
                logging.error(f"Ошибка: {e}")
        return

    # 2. Автотроллинг для всех остальных
    text = message.text.lower()
    for word in TRIGGER_WORDS:
        if word in text:
            now = time.time()
            if "last_troll" in user_cooldowns:
                if now - user_cooldowns["last_troll"] < 0.5:
                    return
            user_cooldowns["last_troll"] = now

            # Выбираем случайную фразу
            phrase = random.choice(TROLL_RESPONSES)
            name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            
            try:
                await message.reply(f"{name}, {phrase}")
            except Exception as e:
                logging.error(f"Ошибка автотроллинга: {e}")
            return

# --- ЗАПУСК ---
async def main():
    logging.info("🚀 Тролль-бот запущен.")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
