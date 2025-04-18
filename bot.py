import logging
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === Получаем токены из переменных окружения ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# === Проверка: если токены не заданы — остановить запуск
if not TELEGRAM_BOT_TOKEN or not DEEPL_API_KEY:
    raise ValueError("❗️ TELEGRAM_BOT_TOKEN и DEEPL_API_KEY должны быть заданы в переменных окружения.")

# === Логирование
logging.basicConfig(level=logging.INFO)

# === Язык: определение направления перевода
def detect_target_lang(text):
    for ch in text:
        if '\u3040' <= ch <= '\u30ff' or '\u4e00' <= ch <= '\u9faf':
            return "EN"  # если японский — переводим на английский
    return "JA"  # иначе — на японский

# === Подготовка текста
def preprocess_text(text):
    text = " ".join(text.strip().split())  # убираем лишние пробелы
    if not text.endswith((".", "!", "?", "。", "！", "？")):
        text += "."
    return text

# === Перевод через DeepL
def translate_with_deepl(text: str) -> str:
    text = preprocess_text(text)
    target_lang = detect_target_lang(text)

    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang,
        "split_sentences": "0",
        "preserve_formatting": "1",
        "formality": "more"
    }

    response = requests.post(url, data=params)
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        return f"[Ошибка перевода: {response.text}]"

# === Обработка входящих сообщений
async def handle_all_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    if text.startswith("/"):  # пропускаем команды
        return

    translation = translate_with_deepl(text)
    await message.reply_text(translation)

# === Запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_all_text))
    print("🤖 Бот запущен с переменными окружения и дословным переводом")
    app.run_polling()
