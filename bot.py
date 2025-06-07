# bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from scraper import get_latest_result
from predictor import predict_next

BOT_TOKEN = "8176352759:AAGbbaNC7zSlzQHcM1yZny1XuL9ye-LCKSg"

CHOOSING_PERIOD = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to LuckyShade Real-Time Prediction Bot!\n"
        "Use /predict to begin.\nSupports: Win Go 1Min & 3Min"
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Please enter the last 3 digits of the Period Number:")
    return CHOOSING_PERIOD

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    if not user_input.isdigit() or len(user_input) != 3:
        await update.message.reply_text("❌ Please enter exactly 3 digits.")
        return CHOOSING_PERIOD

    full_period, result = get_latest_result()
    if not full_period or not result:
        await update.message.reply_text("⚠ Could not fetch latest result. Try again.")
        return ConversationHandler.END

    if not full_period.endswith(user_input):
        await update.message.reply_text("❌ Invalid period number.")
        return ConversationHandler.END

    prediction, confidence = predict_next()

    if prediction == "SKIP":
        await update.message.reply_text(f"⏭️ Skip: {full_period[-3:]}")
        return ConversationHandler.END

    number, color, size = result

    await update.message.reply_text(
        f"🧾 Result for Period {full_period}:\n"
        f"Number: {number}\n🎨 Color: {color}\n⚖ Size: {size}\n\n"
        f"🔮 Predicted Next:\n{prediction['color']}\n{prediction['size']}\n{prediction['number']}\n\n"
        f"📊 Confidence: {confidence}%"
    )
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    predict_handler = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={CHOOSING_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)]},
        fallbacks=[]
    )

    app.add_handler(predict_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
