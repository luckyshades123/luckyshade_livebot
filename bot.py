# bot.py

from telegram import Update, ReplyKeyboardMarkup, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters,
    ConversationHandler
)
from scraper import get_latest_result
from predictor import predict_next
import logging, os, asyncio, nest_asyncio, socket, threading, time

# ✅ Fake port listener for Render Free Plan
def keep_port_alive():
    s = socket.socket()
    s.bind(("0.0.0.0", int(os.environ.get("PORT", 10000))))
    s.listen(1)
    while True:
        time.sleep(1000)

threading.Thread(target=keep_port_alive, daemon=True).start()

# ✅ Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = '8176352759:AAG96y16wUG4x3YgQsnf0JH81L5vg48gwbI'

CHOOSING_MODE, CHOOSING_PERIOD = range(2)
user_modes = {}

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to LuckyShade Real-Time Prediction Bot!\n"
        "Use /predict to start.\nSupports: Win Go 1Min and 3Min."
    )

# ✅ /predict
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([["1Min", "3Min"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🎮 Choose game mode:", reply_markup=reply_markup)
    return CHOOSING_MODE

# ✅ Game mode selection
async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text.strip()
    if mode not in ["1Min", "3Min"]:
        await update.message.reply_text("❌ Choose either '1Min' or '3Min'.")
        return CHOOSING_MODE

    user_modes[update.effective_user.id] = mode
    await update.message.reply_text("📌 Now enter the last 3 digits of the Period Number:")
    return CHOOSING_PERIOD

# ✅ Handle period input
async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = user_modes.get(user_id, "1Min")

    last_digits = update.message.text.strip()
    if not last_digits.isdigit() or len(last_digits) != 3:
        await update.message.reply_text("❌ Enter exactly 3 digits (e.g., 678).")
        return CHOOSING_PERIOD

    full_period, result = await get_latest_result(mode=mode)
    if not full_period or not result:
        await update.message.reply_text("⚠️ Could not fetch result. Try again.")
        return ConversationHandler.END

    if not full_period.endswith(last_digits):
        await update.message.reply_text("❌ Period mismatch. Try again.")
        return ConversationHandler.END

    prediction, confidence = await predict_next(mode=mode)
    number, color, size = result

    if prediction.get("skip"):
        await update.message.reply_text(f"⚠️ Skip: {full_period[-3:]} (Low Confidence)")
    else:
        await update.message.reply_text(
            f"🧾 Period: {full_period}\n"
            f"Number: {number}\n🎨 Color: {color}\n⚖ Size: {size}\n\n"
            f"🔮 Prediction:\n{prediction['color']}\n{prediction['size']}\n{prediction['number']}\n\n"
            f"📊 Confidence: {confidence}%"
        )

    return ConversationHandler.END

# ✅ Safe Render-compatible polling entry
async def run_bot():
    await Bot(token=BOT_TOKEN).delete_webhook(drop_pending_updates=True)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("predict", predict)],
        states={
            CHOOSING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode)],
            CHOOSING_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

# ✅ Main
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(run_bot())
