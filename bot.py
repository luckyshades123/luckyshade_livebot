# bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from predictor import predict_next
import threading, time, os, socket

# Keep port alive for Render
def keep_port_alive():
    s = socket.socket()
    s.bind(("0.0.0.0", int(os.environ.get("PORT", 10000))))
    s.listen(1)
    while True:
        time.sleep(1000)

threading.Thread(target=keep_port_alive).start()

BOT_TOKEN = '8176352759:AAGbbaNC7zSlzQHcM1yZny1XuL9ye-LCKSg'  # Replace this with your actual token
CHOOSING_PERIOD = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to LuckyShade Real-Time Prediction Bot!\nUse /predict to start.")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Enter last 3 digits of the Period Number:")
    return CHOOSING_PERIOD

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_digits = update.message.text.strip()
    if not last_digits.isdigit() or len(last_digits) != 3:
        await update.message.reply_text("❌ Please enter exactly 3 digits (e.g., 789).")
        return CHOOSING_PERIOD

    predicted, confidence = predict_next()

    if predicted["skip"]:
        await update.message.reply_text(f"⚠️ Skip: {last_digits}\n📊 Confidence: {confidence}%")
    else:
        await update.message.reply_text(
            f"🔮 Prediction (Before Result)\n"
            f"Period Ending: {last_digits}\n"
            f"🎨 Color: {predicted['color']}\n"
            f"⚖ Size: {predicted['size']}\n"
            f"#️⃣ Number: {predicted['number']}\n"
            f"📊 Confidence: {confidence}%"
        )

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    conv = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={CHOOSING_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)]},
        fallbacks=[]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == '__main__':
    main()
