
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes
from datetime import datetime
import json
import matplotlib.pyplot as plt

# ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = '8064087816:AAFiKQUtVU1XsCSYMgupYc3ZtGfvz_4oU9c'
DATA_FILE = "scores.json"

def load_scores():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_scores(scores):
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    if now.hour == 13 and now.minute == 37:
        user = update.message.from_user
        scores = load_scores()
        user_id = str(user.id)
        user_name = user.first_name
        if user_id not in scores:
            scores[user_id] = {"name": user_name, "points": 0, "dates": []}
        today = now.strftime("%Y-%m-%d")
        if today not in scores[user_id]["dates"]:
            scores[user_id]["points"] += 1
            scores[user_id]["dates"].append(today)
            save_scores(scores)
            await update.message.reply_text(f"🎯 {user_name}, ты получил 1 балл за 13:37!")

async def show_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    sorted_users = sorted(scores.items(), key=lambda x: x[1]["points"], reverse=True)
    message = "🏆 Рейтинг 13:37:\n"
    for i, (uid, user) in enumerate(sorted_users, 1):
        message += f"{i}. {user['name']}: {user['points']} баллов\n"
    await update.message.reply_text(message)

async def show_graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Пока нет данных для графика.")
        return
    names = [data["name"] for data in scores.values()]
    points = [data["points"] for data in scores.values()]
    plt.figure(figsize=(8, 4))
    plt.bar(names, points, color="skyblue")
    plt.title("Баллы за 13:37")
    plt.ylabel("Баллы")
    plt.xticks(rotation=45)
    plt.tight_layout()
    graph_path = "graph.png"
    plt.savefig(graph_path)
    plt.close()
    await update.message.reply_photo(photo=open(graph_path, "rb"))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.add_handler(CommandHandler("рейтинг", show_scores))
app.add_handler(CommandHandler("график", show_graph))
app.run_polling()
