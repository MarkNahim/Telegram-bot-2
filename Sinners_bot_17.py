from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatType, ParseMode
import re

TOKEN = '8026878396:AAGzEw7NTXmxIexW3aeEWX8kkkH7GUAItuE'
GROUP_ID = -1001350244365
ADMIN_IDS = [333636347]

def get_clickable_user(user):
    if user.username:
        return f"[@{user.username}](tg://user?id={user.id})"
    else:
        return f"[{user.first_name}](tg://user?id={user.id})"

# Команда /post - надсилання в групу
async def post_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Ти не адміністратор.")
        return

    message_text = update.message.text
    full_text = message_text[len("/post"):].strip()

    if not full_text:
        await update.message.reply_text("⚠️ Введи текст після /post.")
        return

    try:
        await context.bot.send_message(chat_id=GROUP_ID, text=full_text)
        await update.message.reply_text("✅ Повідомлення надіслано в групу.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка надсилання в групу: {e}")

# Обробка приватних повідомлень від користувачів
async def handle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = update.effective_user

    user_link = get_clickable_user(user)
    header_text = f"📩 Повідомлення від {user_link}\n🆔 [ID: {user.id}](tg://user?id={user.id})"

    if message.text:
        for admin in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin,
                text=f"{header_text}\n\n{message.text}",
                parse_mode=ParseMode.MARKDOWN
            )
        await message.reply_text("✅ Дякую! Я мені прийшло твоє повідомлення, але так як сервера працюють нестабільно то дочекайтесь з'єднання, не засмучуйтесь через це, адже я ще вчусь і є не стабільним.")

    elif message.photo:
        caption = message.caption or ""
        full_caption = f"{header_text}\n\n{caption}"
        for admin in ADMIN_IDS:
            await context.bot.send_photo(
                chat_id=admin,
                photo=message.photo[-1].file_id,
                caption=full_caption,
                parse_mode=ParseMode.MARKDOWN
            )
        await message.reply_text("📷 Гаразд,дякую! Я радий що ви поділись зі мною цією фотограію, але нажаль на даний момент мої сервера зараз отримуцють велику нагрузку, коли сервера стануть менш перегружені, я вам обов'язково відповім .")

    elif message.video:
        caption = message.caption or ""
        full_caption = f"{header_text}\n\n{caption}"
        for admin in ADMIN_IDS:
            await context.bot.send_video(
                chat_id=admin,
                video=message.video.file_id,
                caption=full_caption,
                parse_mode=ParseMode.MARKDOWN
            )
        await message.reply_text("🎥 Гаразд,дякую! Я радий що ви поділись зі мною цим відео, але нажаль на даний момент мої сервера зараз отримуцють велику нагрузку, коли сервера стануть менш перегружені, я вам обов'язково відповім.")

# Команда /reply - відповідаємо користувачу (текст)
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Тільки адміністратор може використовувати цю команду.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Використання: /reply user_id текст_повідомлення")
        return

    try:
        target_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Помилка: user_id має бути числом.")
        return

    reply_text = ' '.join(args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text=reply_text)
        await update.message.reply_text(f"✅ Відповідь надіслано користувачу {target_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при надсиланні відповіді: {e}")

# 🔁 Команда /replylink - відповісти на повідомлення в групі за посиланням
async def reply_by_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Тільки адміністратори можуть це робити.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⚠️ Використання: /replylink <посилання> <текст>")
        return

    link = args[0]
    reply_text = ' '.join(args[1:])

    # Отримуємо message_id з посилання
    match = re.search(r'/(\d+)$', link)
    if not match:
        await update.message.reply_text("❌ Не вдалося отримати ID повідомлення з посилання.")
        return

    message_id = int(match.group(1))

    try:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=reply_text,
            reply_to_message_id=message_id
        )
        await update.message.reply_text("✅ Відповідь надіслано у групу.")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка при відповіді: {e}")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Я штучний інтелект, створений для цього, аби піднімати актив групи. Якщо у вас є бажання по спілкуватись зі мною в приватних, пишіть сюди, але я ще не дуже розвинувся, тому постараюсь вам відповісти в найблищі терміни, та завжди буду радий з вами по спілкуватись у приватних повідомленнях.")

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("post", post_to_group))
app.add_handler(CommandHandler("reply", reply_to_user))
app.add_handler(CommandHandler("replylink", reply_by_link))

app.add_handler(MessageHandler(
    (filters.TEXT | filters.PHOTO | filters.VIDEO) & filters.ChatType.PRIVATE,
    handle_private
))

print("[✅ БОТ ЗАПУЩЕНИЙ]")
app.run_polling()
