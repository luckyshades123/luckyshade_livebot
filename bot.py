from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes,
    filters, ConversationHandler
)
from scraper import get_latest_result
from predictor import predict_next
import os

# ✅ Your Telegram Bot Token
BOT_TOKEN = '8176352759:AAGbbaNC7zSlzQHcM1yZny1XuL9ye-LCKSg'

CHOOSING_PERIOD = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to LuckyShade Real-Time Prediction Bot!\n"
        "Use /predict to start prediction.\n"
        "Supports: Win Go 1Min and 3Min modes."
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Please enter the last 3 digits of the Period Number:")
    return CHOOSING_PERIOD

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_digits = update.message.text.strip()
    if not last_digits.isdigit() or len(last_digits) != 3:
        await update.message.reply_text("❌ Invalid input. Please enter exactly 3 digits (e.g., 678).")
        return CHOOSING_PERIOD

    full_period, current_result = get_latest_result()
    if not full_period or not current_result:
        await update.message.reply_text("⚠️ Could not fetch latest result. Please try again.")
        return ConversationHandler.END

    if not full_period.endswith(last_digits):
        await update.message.reply_text("❌ Invalid period number.")
        return ConversationHandler.END

    predicted, confidence = predict_next()
    number, color, size = current_result

    if predicted.get('skip', False):
        await update.message.reply_text(f"Skip: {full_period[-3:]}")
    else:
        await update.message.reply_text(
            f"🧾 Result for Period {full_period}:\n"
            f"Number: {number}\n"
            f"🎨 Color: {color}\n"
            f"⚖ Size: {size}\n\n"
            f"🔮 Predicted Next:\n"
            f"{predicted['color']}\n"
            f"{predicted['size']}\n"
            f"{predicted['number']}\n\n"
            f"📊 Confidence: {confidence}%"
        )

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    prediction_flow = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={CHOOSING_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)]},
        fallbacks=[]
    )
    app.add_handler(prediction_flow)
    app.run_polling()

    # ✅ Webhook for Render
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/"
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL + BOT_TOKEN
    )

if __name__ == '__main__':
    main()
