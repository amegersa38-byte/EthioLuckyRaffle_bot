import os
import requests
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Telegram & Chapa መረጃዎች
TELEGRAM_BOT_TOKEN = "8903382235:AAHHkZUSLAHzllDohjEDvt82sK5FS0QgfkQ"
CHAPA_SECRET_KEY = "የእርስዎ_Chapa_Secret_Key_እዚህ_ይግባ"  # ከChapa ያገኙት Secret Key

app = Flask(__name__)

# 1. /start ትእዛዝ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    welcome_text = (
        f"ሰላም {user_first_name}! 👋\n"
        f"እንኳን ወደ ኢትዮ ላኪ የዕጣ ቦት (Ethio Lucky Raffle) በደህና መጡ! 🎯\n\n"
        f"ቲኬት ለመግዛት ከታች ያለውን አዝራር ይጫኑ።"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎫 የዕጣ ቲኬት ግዛ", callback_data="buy_ticket")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# 2. Chapa Webhook (ክፍያ ሲረጋገጥ አውቶሜቲክ ቲኬት መላኪያ)
@app.route('/chapa-webhook', methods=['POST'])
def chapa_webhook():
    data = request.json
    if data and data.get('status') == 'success':
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "failed"}), 400

@app.route('/')
def home():
    return "Ethio Lucky Raffle Bot is Running Live!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
