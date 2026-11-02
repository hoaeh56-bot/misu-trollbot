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

OWNER_ID = 1780243499

# --- БАЗА ПОЛНОЦЕННЫХ ОСКОРБЛЕНИЙ ---
TROLL_RESPONSES = [
    "{name}, ты самонадеянный интеллектуальный банкрот, возомнивший себя вершиной полемического мастерства.",
    "{name}, твоя аргументация напоминает диссертацию, написанную в состоянии когнитивного коллапса.",
    "{name}, ты настолько увлекся конструированием собственной исключительности, что утратил способность отличать реальное превосходство от иллюзии.",
    "{name}, твои высказывания — это эклектика псевдоинтеллектуальных претензий и логических несоответствий.",
    "{name}, ты не подвергаешь собственные убеждения критическому анализу, считая себя самопровозглашенным гением.",
    "{name}, ты подменяешь аргументацию демонстративной категоричностью, а содержательный ответ — риторическими маневрами.",
    "{name}, ты не способен осознать разницу между агрессивной манерой общения и действительным превосходством.",
    "{name}, ты существуешь в комфортной интеллектуальной герметичности, где любое возражение — это личное поражение.",
    "{name}, твоя система самооценки — это замкнутый механизм, производящий исключительно подтверждения собственной правоты.",
    "{name}, мы дадим тебе отпор посредством последовательного разбора твоих тезисов.",
    "{name}, каждое твое противоречие будет обозначено, а необоснованный вывод потребует доказательств.",
    "{name}, за твоей внешней уверенностью не обнаруживается достаточной аргументационной базы.",
    "{name}, ты столкнешься с неудобной перспективой, при которой громкие заявления перестают работать.",
    "{name}, можешь оставить при себе театральные декларации о собственном превосходстве.",
    "{name}, твоя репутация держится исключительно на искусственно раздутом образе.",
    "{name}, когда исчезает возможность прятаться за словесной эквилибристикой, остается только качество мышления.",
    "{name}, тупейший отморозок, ты представляешь собой жалкое сочетание человеческих качеств.",
    "{name}, твоя личность — это антропологический провал, демонстрирующий деградацию характера.",
    "{name}, ты мелочный, завистливый, высокомерный и патологически самовлюбленный субъект.",
    "{name}, твое самомнение не соответствует ни интеллектуальным способностям, ни моральным качествам.",
    "{name}, ты настолько ничтожен в своих суждениях, что воспринимаешь комплексы как доказательство исключительности.",
    "{name}, твоя личность — отвратительная совокупность лицемерия и эмоциональной незрелости.",
    "{name}, ты не обладаешь ни достоинством, ни харизмой, ни внутренним стержнем.",
    "{name}, ты демонстрируешь поразительную концентрацию наглости и самодовольства.",
    "{name}, каждое твое высказывание подтверждает, насколько поверхностным является твой внутренний мир.",
    "{name}, ты собрал в себе все наиболее неприятные человеческие качества.",
    "{name}, твоя неспособность признавать ошибки настолько очевидна, что оправдания выглядят как жалкая инсценировка.",
    "{name}, ты не умеешь вести достойную дискуссию, воспринимая несогласие как личное унижение.",
    "{name}, твоя моральная несостоятельность сочетается с отсутствием деликатности.",
    "{name}, ты обыкновенный самодовольный хам с завышенной самооценкой.",
    "{name}, твоя персона не заслуживает тех масштабов внимания, которые ты пытаешься себе присвоить.",
    "{name}, ты предсказуем в своей мелочности, и твои попытки казаться оригинальным обречены.",
    "{name}, твоя индивидуальность растворяется в повторении чужих комплексов и дешевого высокомерия.",
    "{name}, ты считаешь подобное поведение проявлением силы, но это лишь эмоциональная незрелость.",
    "{name}, ты не производишь впечатление человека с твердыми принципами, ты нуждаешься в признании.",
    "{name}, ты готов пожертвовать остатками достоинства ради иллюзии превосходства.",
    "{name}, сынок шалавы, ты представляешь собой настолько жалкое и отвратительное зрелище, что даже понятие посредственности меняет смысл.",
]

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
    ".крест": "Че крестному в церкви?",
    ".батя": "Че бате в шланг с дерьмом?",
    ".пилон": "Че маме на пилоне?",
    ".трус": "Че малышом в трусах?",
    ".подгуз": "Че с говном в подгузниках?",
}

MASS_PHRASES = [v for k, v in PHRASES.items() if k != ".з"]

TRIGGER_WORDS = [
    "шлюхи", "шлюха", "сын", "пидора", "уебок", 
    "тупой", "пидор", "хуесос", "долбаеб", "тряпка", "тварь"
]

user_cooldowns = {}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id == OWNER_ID:
        await message.reply(
            "👑 <b>Добро пожаловать, Владелец!</b>\n"
            "Вы имеете полный доступ к командам.\n\n"
            "💬 <b>Команды:</b>\n"
            "• <code>.трольмод @юзер</code> — заспамить оскорблениями\n"
            "• <code>.выброс</code> — высыпать все 'Че...' фразы\n"
            "• <code>.п, .м, .д, .б, .мам, .з, .к, .с, .в, .я, .х</code> — твои фразы\n"
            "• <code>.крест, .батя, .пилон, .трус, .подгуз</code> — новые фразы",
            parse_mode="HTML"
        )
    else:
        await message.reply("⛔ Доступ запрещен.")

@dp.message(F.text.lower() == ".выброс")
async def mass_drop(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    random.shuffle(MASS_PHRASES)
    
    for phrase in MASS_PHRASES:
        try:
            await message.answer(phrase)
            await asyncio.sleep(0.2) # КД 0.2 СЕК
        except Exception as e:
            logging.error(f"Ошибка выброса: {e}")
            break

@dp.message(F.text.lower().startswith(".трольмод"))
async def troll_mode(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Укажи юзернейм: <code>.трольмод @username</code>", parse_mode="HTML")
        return
        
    target_username = args[1].replace("@", "")
    target_tag = f"@{target_username}"
    
    random.shuffle(TROLL_RESPONSES)
    
    for response in TROLL_RESPONSES:
        try:
            text_to_send = response.format(name=target_tag)
            await message.answer(text_to_send, parse_mode="HTML")
            await asyncio.sleep(0.2) # КД 0.2 СЕК
        except Exception as e:
            logging.error(f"Ошибка спама: {e}")
            break

@dp.message(F.text)
async def handler(message: Message):
    if message.from_user.id == OWNER_ID:
        text = message.text.lower().strip()
        now = time.time()
        if message.from_user.id in user_cooldowns:
            if now - user_cooldowns[message.from_user.id] < 0.2:
                return
        user_cooldowns[message.from_user.id] = now

        if text in PHRASES:
            try:
                await message.reply(PHRASES[text])
            except Exception as e:
                logging.error(f"Ошибка: {e}")
        return

    text = message.text.lower()
    for word in TRIGGER_WORDS:
        if word in text:
            now = time.time()
            if "last_troll" in user_cooldowns:
                if now - user_cooldowns["last_troll"] < 0.2:
                    return
            user_cooldowns["last_troll"] = now

            phrase = random.choice(TROLL_RESPONSES)
            name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            
            try:
                await message.reply(phrase.format(name=name))
            except Exception as e:
                logging.error(f"Ошибка автотроллинга: {e}")
            return

async def main():
    logging.info("🚀 Тролль-бот запущен (КД 0.2 сек).")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
