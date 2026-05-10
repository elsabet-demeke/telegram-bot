from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import os
from datetime import datetime

# =========================
# CONFIG
# =========================

TOKEN = "8427301208:AAFKlj2Omzymyo7KeYMVGTnHRxH8IxDGLEo"
ADMIN_ID = 5110535270

# =========================
# MENU
# =========================

main_menu = [
    ["1. የህንጻ ኪራይ ጥያቄ"],
    ["2. የካሬ ጭማሪ/ቅናሽ"],
    ["3. የኪራይ ዋጋ ማሻሻያ"],
    ["4. ዕቅድ"],
    ["5. ሪፖርት"]
]

plan_menu = [
    ["📅 ዓመታዊ ዕቅድ"],
    ["♻️ የተሻሻለ ዕቅድ"],
    ["⬅️ ተመለስ"]
]

report_menu = [
    ["📊 የ 1ኛ ሩብ ዓመት ሪፖርት"],
    ["📊 የ 6 ወር ሪፖርት"],
    ["📊 የ 9 ወር ሪፖርት"],
    ["📊 ዓመታዊ ሪፖርት"],
    ["📊 ደራሽ ስራዎች ሪፖርት"],
    ["⬅️ ተመለስ"]
]

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "እንኳን ወደ የመንግስት ህንፃ  አስተዳደር ስታንዳርዳይዜሽን ዳይሬክቶሬት አገልግሎት መስጫ ቦት በደህና መጡ\n\nእባክዎ አገልግሎት ይምረጡ",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# =========================
# MESSAGE HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "4. ዕቅድ":
        context.user_data["mode"] = "plan"
        await update.message.reply_text(
            " እባክዎ የዕቅድ አይነት ይምረጡ",
            reply_markup=ReplyKeyboardMarkup(plan_menu, resize_keyboard=True)
        )
        return

    if text == "5. ሪፖርት":
        context.user_data["mode"] = "report"
        await update.message.reply_text(
            " እባክዎ የሪፖርት አይነት ይምረጡ",
            reply_markup=ReplyKeyboardMarkup(report_menu, resize_keyboard=True)
        )
        return

    if text == "⬅️ ተመለስ":
        context.user_data.clear()
        await update.message.reply_text(
            "ወደ ዋና ማውጫ",
            reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        )
        return

    forms = {
        "1. የህንጻ ኪራይ ጥያቄ": "building_rent_form.docx",
        "2. የካሬ ጭማሪ/ቅናሽ": "square_form.docx",
        "3. የኪራይ ዋጋ ማሻሻያ": "price_form.docx",
    }

    if text in forms:
        await update.message.reply_document(
            document=open(forms[text], "rb"),
            caption="📄 እባክዎ ቅጹን አውርደው ይሙሉ እና ይመልሱ"
        )
        return

    plan_options = ["📅 ዓመታዊ ዕቅድ", "♻️ የተሻሻለ ዕቅድ"]

    if text in plan_options:
        context.user_data["type"] = "PLAN"
        context.user_data["subtype"] = text
        await update.message.reply_text("📎 እባክዎ Word/Excel ፋይል ያስገቡ (Plan)")
        return

    report_options = [
        "📊 የ 1ኛ ሩብ ዓመት ሪፖርት",
        "📊 የ 6 ወር ሪፖርት",
        "📊 የ 9 ወር ሪፖርት",
        "📊 ዓመታዊ ሪፖርት",
        "📊 ደራሽ ስራዎች ሪፖርት"
    ]

    if text in report_options:
        context.user_data["type"] = "REPORT"
        context.user_data["subtype"] = text
        await update.message.reply_text("📎 እባክዎ Word/Excel ፋይል ያስገቡ (Report)")
        return

# =========================
# FILE HANDLER (FIXED)
# =========================

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    user = update.message.from_user
    document = update.message.document
    file = await document.get_file()

    # ✅ FIXED TIME FORMAT (NO INVALID CHARACTERS)
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date = datetime.now().strftime("%Y-%m-%d")

    safe_username = (user.username or "user").replace(" ", "_")

    filename = f"{safe_username}_{time}_{document.file_name}"
    path = os.path.join("uploads", filename)

    await file.download_to_drive(path)

    doc_type = context.user_data.get("type", "UNKNOWN")
    subtype = context.user_data.get("subtype", "UNKNOWN")

    # ✅ RELIABLE REPLY
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ ፋይል በትክክል ደርሷል"
    )

    await context.bot.send_document(
        chat_id=ADMIN_ID,
        document=open(path, "rb"),
        caption=f"""
📩 NEW SUBMISSION

📅 Date: {date}
⏰ Time: {time}

👤 User: @{user.username}
🆔 ID: {user.id}

📌 Type: {doc_type}
📌 Selection: {subtype}

📄 File: {document.file_name}
"""
    )

    context.user_data.clear()

# =========================
# RUN APP
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

print("Bot is running...")

app.run_polling()