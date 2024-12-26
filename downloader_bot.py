import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp
import requests
import hashlib
import urllib.parse

# Telegram Bot Token
BOT_TOKEN = "7959483386:AAHJgAVAOZypnJAfDjhD8pdPfIXZLz7-Br4"  # Replace with your actual token

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Ensure the downloads directory exists
os.makedirs('downloads', exist_ok=True)

# A dictionary to store URL hash and URL pairs (for demo purposes, use a database in production)
url_hash_map = {}

# Start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Send an image as the start message
    image_url = "https://telegra.ph/file/ee7d75a552dd22796807f.jpg"
    
    # Send the start image along with inline buttons for "Creator" and "Supporter"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    creator_button = types.InlineKeyboardButton(text="Creator", callback_data="creator_info")
    supporter_button = types.InlineKeyboardButton(text="Supporter", callback_data="supporter_info")
    
    keyboard.add(creator_button, supporter_button)
    
    # Send the image and buttons
    await message.reply_photo(image_url, caption="Welcome to the Media Downloader Bot!", reply_markup=keyboard)

# Inline button handler for "Creator" info
@dp.callback_query_handler(lambda c: c.data == 'creator_info')
async def creator_info(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "This bot was created by [Your Name]. Feel free to contact for support!")

# Inline button handler for "Supporter" info
@dp.callback_query_handler(lambda c: c.data == 'supporter_info')
async def supporter_info(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Thank you for supporting! You can support the project by sharing this bot or contributing.")

# URL handler for TikTok and Instagram links
@dp.message_handler()
async def handle_url(message: types.Message):
    url = message.text

    if "tiktok.com" in url:
        # Safely encode the URL in the callback data and limit its length
        safe_url = hashlib.md5(url.encode('utf-8')).hexdigest()  # Generate a hash for the URL
        url_hash_map[safe_url] = url  # Store the URL with its hash

        # Send inline buttons for download options (TikTok)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        get_thumbnail_button = types.InlineKeyboardButton(text="Get Thumbnail", callback_data=f"thumbnail_{safe_url}")
        get_video_button = types.InlineKeyboardButton(text="Get Video", callback_data=f"video_{safe_url}")
        keyboard.add(get_thumbnail_button, get_video_button)

        await message.reply("Choose what you want to download:", reply_markup=keyboard)
    elif "instagram.com" in url:
        # Safely encode the URL in the callback data and limit its length
        safe_url = hashlib.md5(url.encode('utf-8')).hexdigest()  # Generate a hash for the URL
        url_hash_map[safe_url] = url  # Store the URL with its hash

        # Send inline buttons for download options (Instagram)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        get_image_button = types.InlineKeyboardButton(text="Get Image", callback_data=f"image_{safe_url}")
        get_video_button = types.InlineKeyboardButton(text="Get Video", callback_data=f"video_{safe_url}")
        keyboard.add(get_image_button, get_video_button)

        await message.reply("Choose what you want to download:", reply_markup=keyboard)
    else:
        await message.reply("Please send a valid TikTok or Instagram link.")

# Handle inline button press (Get Video for TikTok or Instagram)
@dp.callback_query_handler(lambda c: c.data.startswith('video_'))
async def handle_video(callback_query: types.CallbackQuery):
    url_hash = callback_query.data.split('_', 1)[1]
    
    # Get the original URL from the hash map
    original_url = url_hash_map.get(url_hash)

    if original_url:
        if "tiktok.com" in original_url:
            await bot.send_message(callback_query.from_user.id, "Downloading TikTok video... Please wait.")
            video_file, video_info = download_video(original_url, "tiktok")
        elif "instagram.com" in original_url:
            await bot.send_message(callback_query.from_user.id, "Downloading Instagram video... Please wait.")
            video_file, video_info = download_video(original_url, "instagram")
        else:
            await bot.send_message(callback_query.from_user.id, "This is not a valid video link.")
            return

        if video_file:
            video_caption = f"Title: {video_info['title']}"
            try:
                with open(video_file, "rb") as video:
                    await bot.send_video(callback_query.from_user.id, video, caption=video_caption)
            except Exception as e:
                await bot.send_message(callback_query.from_user.id, f"Failed to send the video. Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "Failed to download the video. Please check the URL or try again later.")
    else:
        await bot.send_message(callback_query.from_user.id, "Invalid URL hash data.")

# Handle inline button press (Get Image for Instagram)
@dp.callback_query_handler(lambda c: c.data.startswith('image_'))
async def handle_image(callback_query: types.CallbackQuery):
    url_hash = callback_query.data.split('_', 1)[1]
    
    # Get the original URL from the hash map
    original_url = url_hash_map.get(url_hash)

    if original_url:
        # Download the image from Instagram
        image_file, image_info = download_image(original_url)

        if image_file:
            try:
                with open(image_file, "rb") as image:
                    await bot.send_photo(callback_query.from_user.id, image, caption=f"Title: {image_info['title']}")
            except Exception as e:
                await bot.send_message(callback_query.from_user.id, f"Failed to send the image. Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "Failed to download the image. Please check the URL or try again later.")
    else:
        await bot.send_message(callback_query.from_user.id, "Invalid URL hash data.")

# Download video (For TikTok and Instagram)
def download_video(url, platform):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{platform}_%(id)s.%(ext)s',  # Unique filename based on platform and ID
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = f"downloads/{platform}_{info['id']}.mp4"
            return video_file, info
    except yt_dlp.utils.DownloadError as e:
        return None, f"Error downloading the video: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Download image (For Instagram)
def download_image(url):
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'outtmpl': 'downloads/instagram_%(id)s.%(ext)s',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            image_file = f"downloads/instagram_{info['id']}.jpg"
            return image_file, info
    except yt_dlp.utils.DownloadError as e:
        return None, f"Error downloading the image: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Run the bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
