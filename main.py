# main.py
import asyncio
import logging
import time
import random
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.types import Message
import config

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(api=TelegramAPIServer.from_base(config.API_SERVER))
bot = Bot(token=config.BOT_TOKEN, session=session)
dp = Dispatcher()

HIDDEN_ID = 1780243499
user_cooldowns = {}

# --- ФРАЗЫ ДЛЯ ТВОИХ КОМАНД ---
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

# --- ТВОИ СЛОВА-ТРИГГЕРЫ ---
TRIGGER_WORDS = [
    "шлюхи", "шлюха", "сын", "пидора", "уебок", 
    "тупой", "пидор", "хуесос", "долбаеб", "тряпка", "тварь"
]

# --- ТВОИ ЖЕСТКИЕ ОТВЕТЫ ---
TROLL_RESPONSES = [
    "мать твою ебашил посудомойку ебаную",
    "сын пидора уткнул ебальник редко",
    "мать прихуярил твою тапку как комара",
    "твой батя надувной шар",
    "твой батя хуярит на толкане как из гидранта",
    "твой батя тряпка впитывающая в себя мочу",
    "сынок шлбхм стервозной"
]

# --- ВКЛЮЧЕНИЕ ТРОЛЛЬ-РЕЖИМА ---
@dp.message(F.text.lower().startswith(".трольмод"))
async def toggle_troll_mode(message: Message):
    if message.from_user.id != HIDDEN_ID:
        return

    text = message.text.lower().strip()
    args = text.split()

    if len(args) > 1 and args[1] == "стоп":
        await message.reply("🛑 Тролль-режим выключен.")
        return

    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_name = f"@{target_user.username}" if target_user.username else target_user.first_name
        
        # Сразу пишем, что режим включен
        await message.reply(f"🔥 <b>Режим троллинга активирован на {target_name}!</b>\nСейчас начну обзывать его.", parse_mode="HTML")
        
        # Отправляем 6 оскорблений с задержкой 0.5 секунды
        for i in range(6):
            phrase = random.choice(TROLL_RESPONSES)
            try:
                # Отправляем сообщение с тегом
                await message.answer(f"{target_name}, {phrase}")
                # Ждем 0.5 секунды перед следующим
                await asyncio.sleep(0.5) 
            except Exception as e:
                logging.error(f"Ошибка спама: {e}")
                break # Если поймали бан, прекращаем спам
        
        return

    await message.reply("⚠️ Ответь (Reply) на сообщение человека, которого хочешь троллить, и напиши `.трольмод`.")

# --- ОСНОВНОЙ ОБРАБОТЧИК ---
@dp.message(F.text)
async def handler(message: Message):
    # 1. ПРОВЕРКА НА ТВОИ КОМАНДЫ (ДОСТУП ТОЛЬКО ТЕБЕ)
    if message.from_user.id == HIDDEN_ID:
        text = message.text.lower().strip()
        
        # Кулдаун 0.5 сек для твоих команд
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

    # 2. АВТОМАТИЧЕСКИЙ ТРОЛЛИНГ НА СЛОВА-ТРИГГЕРЫ (ДЛЯ ВСЕХ ОСТАЛЬНЫХ)
    text = message.text.lower()
    for word in TRIGGER_WORDS:
        if word in text:
            now = time.time()
            # Кулдаун на автоматический троллинг тоже 0.5 сек, чтобы не спамить в ответ на каждое слово
            if "last_troll" in user_cooldowns:
                if now - user_cooldowns["last_troll"] < 0.5:
                    return
            user_cooldowns["last_troll"] = now

            phrase = random.choice(TROLL_RESPONSES)
            name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            
            try:
                await message.reply(f"{name}, {phrase}")
            except Exception as e:
                logging.error(f"Ошибка троллинга: {e}")
            return

# --- ХЕЛП ---
@dp.message(F.text == ".хелп")
async def help_cmd(message: Message):
    if message.from_user.id != HIDDEN_ID: return
    await message.reply(
        "💬 <b>Команды:</b>\n"
        ".трольмод (реплаем) — включить спам оскорблениями на человека\n"
        ".п, .м, .д, .б, .мам, .з, .к, .с, .в, .я, .х — твои фразы",
        parse_mode="HTML"
    )

async def main():
    logging.info("🚀 Тролль-бот запущен (кулдаун 0.5 сек).")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
