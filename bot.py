import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === Настройки ===
TELEGRAM_BOT_TOKEN = "7604760601:AAELL1UilnhovMnjJdskoC1Qhx35FtKN-zI"
DEEPL_API_KEY = "354a537f-a56a-44c8-88f1-0b19cb13917b:fx"

logging.basicConfig(level=logging.INFO)

# === Определение языка (англ ⇄ японский) ===
def detect_target_lang(text):
    for ch in text:
        if '\u3040' <= ch <= '\u30ff' or '\u4e00' <= ch <= '\u9faf':
            return "EN"  # если японский — переводим на английский
    return "JA"  # иначе — на японский

# === Очистка и подготовка текста ===
def preprocess_text(text):
    text = " ".join(text.strip().split())  # убираем лишние пробелы
    if not text.endswith((".", "!", "?", "。", "！", "？")):
        text += "."  # добавляем точку, чтобы DeepL не считал текст незавершённым
    return text

# === Перевод через DeepL ===
def translate_with_deepl(text: str) -> str:
    text = preprocess_text(text)
    target_lang = detect_target_lang(text)

    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": DEEPL_API_KEY,
        "text": text,
        "target_lang": target_lang,
        "split_sentences": "0",            # переводить весь текст как одно целое
        "preserve_formatting": "1",        # сохранить формат
        "formality": "more"                # более официальный/дословный перевод
    }

    response = requests.post(url, data=params)
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        return f"[Ошибка перевода: {response.text}]"

# === Обработка всех текстовых сообщений ===
async def handle_all_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    if text.startswith("/"):  # пропускаем команды
        return

    translation = translate_with_deepl(text)
    await message.reply_text(translation)

# === Запуск бота ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_all_text))
    print("🤖 Бот запущен с режимом дословного перевода (DeepL)")
    app.run_polling()
