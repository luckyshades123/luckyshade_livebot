from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from scraper import get_latest_result
from predictor import predict_next

# ✅ Your actual bot token inserted below (keep it private)
BOT_TOKEN = '8176352759:AAGbbaNC7zSlzQHcM1yZny1XuL9ye-LCKSg'

SELECT_MODE, HANDLE_PERIOD = range(2)
user_modes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Win Go 1Min", "Win Go 3Min"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("👋 Welcome to LuckyShade Bot!\nChoose your game mode:", reply_markup=reply_markup)
    return SELECT_MODE

async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_modes[update.effective_chat.id] = update.message.text
    await update.message.reply_text("📌 Please enter the last 3 digits of the Period Number (e.g., 678):")
    return HANDLE_PERIOD

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    mode = user_modes.get(user_id, "Win Go 1Min")
    suffix = update.message.text.strip()
    if not suffix.isdigit() or len(suffix) != 3:
        await update.message.reply_text("❌ Please enter exactly 3 digits (e.g., 678)")
        return HANDLE_PERIOD

    prefix = "2506010"
    full_period = prefix + suffix

    result_data = get_latest_result(full_period, mode)
    if not result_data:
        await update.message.reply_text(f"Skip: {suffix}")
        return ConversationHandler.END

    result_number, result_color, result_size = result_data

    await update.message.reply_text(
        f"🧾 Result for Period {full_period}:\n"
        f"Number: {result_number}\n"
        f"🎨 Color: {result_color}\n"
        f"⚖ Size: {result_size}"
    )

    prediction, confidence = predict_next(result_number, result_color, result_size)
    pred_color, pred_size, pred_number = prediction

    await update.message.reply_text(
        f"🔮 Predicted Next:\n"
        f"{pred_color}\n"
        f"{pred_size}\n"
        f"🎯 Number: {pred_number}\n\n"
        f"📊 Confidence: {confidence}%"
    )
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_mode)],
            HANDLE_PERIOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_period)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
