
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from scraper import fetch_latest_result
from predictor import generate_prediction

BOT_TOKEN = "REPLACE_WITH_YOUR_TOKEN"
CHOOSING_MODE, WAITING_FOR_PERIOD = range(2)
user_modes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Win Go 1Min", "Win Go 3Min"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🎮 Choose Game Mode:", reply_markup=reply_markup)
    return CHOOSING_MODE

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text
    user_modes[update.effective_user.id] = mode
    await update.message.reply_text("📌 Please enter the last 3 digits of the Period Number:")
    return WAITING_FOR_PERIOD

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    short_period = update.message.text.strip()
    user_id = update.effective_user.id
    mode = user_modes.get(user_id, "Win Go 1Min")
    full_period, result_data = fetch_latest_result(mode, short_period)
    prediction = generate_prediction(result_data)
    await update.message.reply_text("
        f"🧾 Result for Period {full_period}:
"
        f"Number: {result_data['number']}
"
        f"🎨 Color: {result_data['color']}
"
        f"⚖ Size: {result_data['size']}

"
        f"🔮 Predicted Next:
"
        f"{prediction['color']}
"
        f"{prediction['size']}

"
        f"📊 Confidence: {prediction['confidence']}%"
    )
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode)],
            WAITING_FOR_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)]
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
