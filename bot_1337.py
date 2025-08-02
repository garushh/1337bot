import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import matplotlib.pyplot as plt

# Получаем токен и настройки из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8443))

# Файл для хранения баллов
SCORES_FILE = "scores.json"

# Загрузка данных
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Сохранение данных
def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

# Проверка времени — 13:37
def is_1337():
    now = datetime.now()
    return now.hour == 13 and now.minute == 37

# Обработка обычного сообщения
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = str(update.effective_chat.id)
    user_id = str(user.id)
    username = user.full_name

    if not is_1337():
        return  # Не 13:37 — игнорируем

    scores = load_scores()
    if chat_id not in scores:
        scores[chat_id] = {}

    today = datetime.now().strftime("%Y-%m-%d")
    if today in scores[chat_id].get(user_id, {}):
        return  # Уже получал балл сегодня

    scores[chat_id].setdefault(user_id, {})[today] = username
    save_scores(scores)

    count = len(scores[chat_id][user_id])
    await update.message.reply_text(f"🎯 {username}, ты получил 1 балл! Всего баллов: {count}")

# Команда /rating
async def show_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    scores = load_scores()

    if chat_id not in scores or not scores[chat_id]:
        await update.message.reply_text("Пока нет баллов 💤")
        return

    user_scores = {
        list(data.values())[0]: len(data)
        for data in scores[chat_id].values()
    }

    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    lines = [f"{i+1}. {name} — {pts} баллов" for i, (name, pts) in enumerate(sorted_scores)]
    await update.message.reply_text("\n".join(lines))

# Команда /chart
async def show_graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    scores = load_scores()

    if chat_id not in scores or not scores[chat_id]:
        await update.message.reply_text("Пока нечего показать 📉")
        return

    names = []
    points = []
    for uid, entries in scores[chat_id].items():
        name = list(entries.values())[0]
        names.append(name)
        points.append(len(entries))

    fig, ax = plt.subplots()
    ax.barh(names, points)
    ax.set_xlabel("Баллы")
    ax.set_title("🏆 Рейтинг 13:37")

    plt.tight_layout()
    chart_path = "/tmp/chart.png"
    plt.savefig(chart_path)
    plt.close()

    with open(chart_path, "rb") as img:
        await update.message.reply_photo(photo=img)

# Запуск бота через webhook
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("rating", show_scores))
    app.add_handler(CommandHandler("chart", show_graph))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print(f"✅ Бот запускается по webhook: {WEBHOOK_URL}")

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
