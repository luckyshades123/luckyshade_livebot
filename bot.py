# bot.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters,
    ConversationHandler
)
from scraper import get_latest_result
from predictor import predict_next
import logging, os

BOT_TOKEN = '8176352759:AAG96y16wUG4x3YgQsnf0JH81L5vg48gwbI'

logging.basicConfig(level=logging.INFO)

CHOOSING_MODE, CHOOSING_PERIOD = range(2)

# Store game mode temporarily
user_modes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to LuckyShade Real-Time Prediction Bot!\n"
        "Use /predict to get started.\n"
        "Supports: Win Go 1Min and 3Min modes."
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["1Min", "3Min"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🎮 Choose game mode:", reply_markup=reply_markup)
    return CHOOSING_MODE

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text.strip()
    if mode not in ["1Min", "3Min"]:
        await update.message.reply_text("❌ Please choose either '1Min' or '3Min'.")
        return CHOOSING_MODE

    user_id = update.effective_user.id
    user_modes[user_id] = mode

    await update.message.reply_text("📌 Now enter the last 3 digits of the Period Number:")
    return CHOOSING_PERIOD

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = user_modes.get(user_id, "1Min")  # Default fallback

    last_digits = update.message.text.strip()
    if not last_digits.isdigit() or len(last_digits) != 3:
        await update.message.reply_text("❌ Invalid input. Enter exactly 3 digits (e.g., 678).")
        return CHOOSING_PERIOD

    full_period, result = get_latest_result(mode=mode)
    if not full_period or not result:
        await update.message.reply_text("⚠️ Could not fetch result. Try again later.")
        return ConversationHandler.END

    if not full_period.endswith(last_digits):
        await update.message.reply_text("❌ Period mismatch. Try again.")
        return ConversationHandler.END

    prediction, confidence = predict_next(mode=mode)
    number, color, size = result

    if prediction.get('skip'):
        await update.message.reply_text(f"⚠️ Skip: {full_period[-3:]} (low confidence)")
    else:
        await update.message.reply_text(
            f"🧾 Period: {full_period}\n"
            f"Number: {number}\n🎨 Color: {color}\n⚖ Size: {size}\n\n"
            f"🔮 Prediction:\n{prediction['color']}\n{prediction['size']}\n{prediction['number']}\n\n"
            f"📊 Confidence: {confidence}%"
        )

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    prediction_conv = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={
            CHOOSING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode)],
            CHOOSING_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)],
        },
        fallbacks=[]
    )

    app.add_handler(prediction_conv)

    # Webhook for Render
    PORT = int(os.environ.get("PORT", 8443))
    HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://{HOST}/{BOT_TOKEN}",
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == '__main__':
    main()
