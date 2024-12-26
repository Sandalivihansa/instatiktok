from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Telegram Bot Token and Channel Username
BOT_TOKEN = "7959483386:AAHJgAVAOZypnJAfDjhD8pdPfIXZLz7-Br4"  # Replace with your actual bot token
CHANNEL_USERNAME = "@slmusicmania"  # Replace with your actual channel username

# Initialize bot and dispatcher 
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Function to check if the user is subscribed to the channel
async def is_user_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        return False

# Start command handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    # Check if the user is subscribed to the channel
    subscribed = await is_user_subscribed(user_id)

    if not subscribed:
        await message.reply(
            "Please subscribe to our channel to use the bot. After subscribing, click /start again.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # Send a welcome message if the user is subscribed
    await message.reply("Welcome! You are now subscribed and can use the bot.")

# Handle incoming messages (can be customized as needed)
@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # Check if the user is subscribed before processing the message
    subscribed = await is_user_subscribed(user_id)

    if not subscribed:
        await message.reply(
            "You need to subscribe to the channel to use the bot. Please subscribe and click /start again."
        )
        return

    # Process the message if the user is subscribed
    await message.reply(f"Hello, {message.from_user.first_name}!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
