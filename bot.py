
import logging
import random
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ቦት እና የአድሚን መረጃ ---
BOT_TOKEN = "8903382235:AAHHkZUSLAHzllDohjEDvt82sK5FS0QgfkQ"  # የእርስዎን ትክክለኛ Bot Token ያስገቡ
ADMIN_CHAT_ID = 554041467  # የእርስዎን Admin Telegram ID ያስገቡ

# --- የቁጥር መረጃዎችን በፋይል የማስቀመጫ እና የመጫኛ ስርአት ---
DATA_FILE = "ticket_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                pass
    # ነባሪ መረጃዎች (ፋይሉ ከሌለ)
    return {
        '50': {'prefix': 'A', 'current': 0, 'max': 250, 'price': 50, 'prize': '7,500 ብር'},
        '100': {'prefix': 'B', 'current': 0, 'max': 250, 'price': 100, 'prize': '15,000 ብር'},
        '150': {'prefix': 'C', 'current': 0, 'max': 250, 'price': 150, 'prize': '22,500 ብር'}
    }

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(ticket_counts, f)

ticket_counts = load_data()
user_pending_tickets = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 እንኳን ወደ ዕድል ራፍል (Edel Raffle) ቦት በሰላም መጡ!\n\n"
        "የዕጣ ቲኬት ለመግዛት ከታች ያለውን **'🎫 ቲኬት ለመግዛት'** የሚለውን ቁልፍ ይጫኑ።"
    )
    keyboard = [[InlineKeyboardButton("🎫 ቲኬት ለመግዛት", callback_data="buy_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "🎁 **የዕድል ራፍል 3 የተለያዩ የዕጣ ዓይነቶች እና የሽልማት ሰንጠረዥ፦**\n\n"
        "🔴 **1ኛ ዕጣ (የ 50 ብር መደብ)**\n"
        "• የቲኬት ዋጋ፦ 50 ብር (1 የዕጣ ቁጥር)\n"
        "🥇 1ኛ ዕጣ፦ 7,500 ብር | 🥈 2ኛ ዕጣ፦ 1,000 ብር\n"
        "🥉 3ኛ ዕጣ (ማጽናኛ)፦ ለ 5 ሰዎች (ለእያንዳንዳቸው 50 ብር)\n\n"
        "🟡 **2ኛ ዕጣ (የ 100 ብር መደብ)**\n"
        "• የቲኬት ዋጋ፦ 100 ብር (1 የዕጣ ቁጥር)\n"
        "🥇 1ኛ ዕጣ፦ 15,000 ብር | 🥈 2ኛ ዕጣ፦ 2,000 ብር\n"
        "🥉 3ኛ ዕጣ (ማጽናኛ)፦ ለ 5 ሰዎች (ለእያንዳንዳቸው 100 ብር)\n\n"
        "🟢 **3ኛ ዕጣ (የ 150 ብር መደብ)**\n"
        "• የቲኬት ዋጋ፦ 150 ብር (1 የዕጣ ቁጥር)\n"
        "🥇 1ኛ ዕጣ፦ 22,500 ብር | 🥈 2ኛ ዕጣ፦ 3,000 ብር\n"
        "🥉 3ኛ ዕጣ (ማጽናኛ)፦ ለ 5 ሰዎች (ለእያንዳንዳቸው 150 ብር)\n\n"
        "⚠️ ለእያንዳንዱ የዕጣ ዓይነት የተዘጋጀው 250 የዕጣ ቁጥሮች ብቻ ነው!\n\n"
        "💳 **የክፍያ አማራጮች (ቁጥሩን ነክተው ኮፒ ያድርጉ)፦**\n"
        "🏦 CBE: `1000090307928` (አስፋ መገርሳ)\n"
        
        "👇 ለመግዛት የሚፈልጉትን የዕጣ መደብ ይምረጡ፦"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔴 የ 50 ብር ዕጣ", callback_data="select_50")],
        [InlineKeyboardButton("🟡 የ 100 ብር ዕጣ", callback_data="select_100")],
        [InlineKeyboardButton("🟢 የ 150 ብር ዕጣ", callback_data="select_150")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cat = query.data.split('_')[1]
    info = ticket_counts[cat]

    if info['current'] >= info['max']:
        await query.edit_message_text(f"❌ የ {cat} ብር ዕጣ ቲኬት ሙሉ በሙሉ አልቋል! እባክዎን ሌላ መደብ ይምረጡ።")
        return

    context.user_data['selected_cat'] = cat
    text = (
        f"✅ የ **{cat} ብር ዕጣ** መርጠዋል።\n\n"
        f"እባክዎን የ {cat} ብር ክፍያ በቴሌብር ወይም በንግድ ባንክ ፈጽመው **የደረሰኝ ፎቶ (Screenshot)** እዚህ ይላኩ።"
    )
    await query.edit_message_text(text, parse_mode='Markdown')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    cat = context.user_data.get('selected_cat')

    if not cat:
        await update.message.reply_text("⚠️ እባክዎን አስቀድመው /start ብለው የዕጣ መደብ (የ 50፣ 100 ወይም 150 ብር) ይምረጡ።")
        return

    photo_id = update.message.photo[-1].file_id
    user_pending_tickets[user.id] = cat

    admin_text = (
        f"📥 **አዲስ የክፍያ ደረሰኝ ደርሷል!**\n\n"
        f"👤 ተጠቃሚ፦ {user.full_name} (@{user.username})\n"
        f"🆔 User ID: `{user.id}`\n"
        f"🎯 የተመረጠ ዕጣ፦ **የ {cat} ብር መደብ**"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ አጽድቅ (ቁጥር ስጥ)", callback_data=f"approve_{user.id}_{cat}")],
        [InlineKeyboardButton("❌ ውድቅ አድርግ", callback_data=f"reject_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_id, caption=admin_text, reply_markup=reply_markup, parse_mode='Markdown')
    await update.message.reply_text("📩 የክፍያ ደረሰኝዎ ደርሶናል! ክፍያው ተረጋግጦ የዕጣ ቁጥርዎ በቅርቡ ይላክልዎታል።")

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split('_')
    action = data[0]
    target_user_id = int(data[1])

    if action == "approve":
        cat = data[2]
        info = ticket_counts[cat]

        if info['current'] >= info['max']:
            await query.edit_message_caption(caption=f"❌ የ {cat} ብር ዕጣ ተሞልቷል! ቁጥር መስጠት አይቻልም።")
            return

        info['current'] += 1
        save_data()  # ቁጥሩ ሲጨምር በፋይል ውስጥ በራስ-ሰር እንዲቀመጥ ይደረጋል
        ticket_number = f"{info['prefix']}-{info['current']:03d}"

        user_msg = (
            f"🎉 **እንኳን ደስ አለዎት! ክፍያዎ ተረጋግጧል።**\n\n"
            f"🎫 የእርስዎ የዕጣ ቁጥር፦ **`{ticket_number}`**\n"
            f"🎯 የዕጣ መደብ፦ የ {cat} ብር (ሽልማት፦ {info['prize']})\n\n"
            f"መልካም ዕድል!"
        )
        await context.bot.send_message(chat_id=target_user_id, text=user_msg, parse_mode='Markdown')
        await query.edit_message_caption(caption=f"✅ የዕጣ ቁጥር **{ticket_number}** ለተጠቃሚው ተልኳል!")

    elif action == "reject":
        user_msg = "❌ የላኩት ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛ የክፍያ ደረሰኝ መላክዎን ያረጋግጡ።"
        await context.bot.send_message(chat_id=target_user_id, text=user_msg)
        await query.edit_message_caption(caption="❌ ክፍያው ውድቅ ተደርጓል።")

# --- አውቶማቲክ የዕጣ ማውጫ ትእዛዝ (/draw) ---
async def draw_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ ይህንን ትእዛዝ መጠቀም የሚችሉት አድሚን ብቻ ናቸው!")
        return

    args = context.args
    if not args or args[0] not in ['50', '100', '150']:
        await update.message.reply_text("⚠️ እባክዎን ትክክለኛ መደብ ይጥቀሱ። ဥပለቤ፦ `/draw 50` ወይም `/draw 100` ወይም `/draw 150`")
        return

    cat = args[0]
    info = ticket_counts[cat]
    current_count = info['current']

    if current_count < 7:
        await update.message.reply_text(f"❌ የ {cat} ብር ዕጣ አሸናፊ ለማውጣት ቢያንስ 7 ቲኬቶች መሸጥ አለባቸው! አሁን የተሸጠው {current_count} ቁጥር ብቻ ነው።")
        return

    sold_tickets = [f"{info['prefix']}-{i:03d}" for i in range(1, current_count + 1)]
    winners = random.sample(sold_tickets, 7)
    first_prize = winners[0]
    second_prize = winners[1]
    third_prizes = winners[2:7]

    result_text = (
        f"🏆 **የ {cat} ብር መደብ ዕጣ አሸናፊዎች ይፋ ሆነዋል!**\n"
        f"*(ከጠቅላላ የተሸጡ {current_count} ቲኬቶች ውስጥ የተመረጡ)*\n\n"
        f"🥇 **1ኛ አሸናፊ ({info['prize']}):**\n👉 `{first_prize}`\n\n"
        f"🥈 **2ኛ አሸናፊ:**\n👉 `{second_prize}`\n\n"
        f"🥉 **3ኛ አሸናፊዎች / ማጽናኛ (ለ 5 ሰዎች):**\n"
    )
    for t in third_prizes:
        result_text += f"• `{t}`\n"

    result_text += "\n🎉 አሸናፊዎችን ሁሉንም እንኳን ደስ አላችሁ ይላል!"
    await update.message.reply_text(result_text, parse_mode='Markdown')

# --- የዕጣ መደብ ወደ 0 ለመመለስ የሚያስችል ትእዛዝ (/reset) ---
async def reset_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ ይህንን ትእዛዝ መጠቀም የሚችሉት አድሚን ብቻ ናቸው!")
        return

    args = context.args
    if not args or args[0] not in ['50', '100', '150']:
        await update.message.reply_text("⚠️ እባክዎን ዳግም ማስጀመር (Reset ማድረግ) የሚፈልጉትን መደብ ይጥቀሱ። ဥပለቤ፦ `/reset 50`")
        return

    cat = args[0]
    ticket_counts[cat]['current'] = 0
    save_data()  # ዳታቤዙ ውስጥ ዜሮ ሆኖ እንዲቀመጥ ይደረጋል
    await update.message.reply_text(f"🔄 የ **{cat} ብር ዕጣ** ቁጥር ቆጠራ ሙሉ በሙሉ ወደ **0** ተመልሷል! አዲስ ዙር መጀመር ይቻላል።")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("draw", draw_winners))
    app.add_handler(CommandHandler("reset", reset_category))
    app.add_handler(CallbackQueryHandler(buy_menu, pattern="^buy_menu$"))
    app.add_handler(CallbackQueryHandler(select_category, pattern="^select_"))
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot runs successfully...")
    app.run_polling()
