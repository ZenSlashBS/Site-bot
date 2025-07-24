# bot.py
import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from db import add_category, get_categories, add_product

TOKEN = os.environ['8249485083:AAFNoFTh4vIq25eMXdNbiCq2_WIKqbt7MNM']
ADMIN_ID = 7451959845  # int(os.environ['ADMIN_ID'])
CHANNEL_ID = -1002756865313  # int(os.environ['CHANNEL_ID'])

bot = telebot.TeleBot(TOKEN)

user_states = {}  # {user_id: {'state': 'step', 'data': {...}}}

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "Welcome! Use /add to add a product, /newcategory to add category.")

@bot.message_handler(commands=['newcategory'])
def new_category(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "Enter the new category name:", reply_markup=ForceReply())
    user_states[message.from_user.id] = {'state': 'new_category'}

@bot.message_handler(commands=['add'])
def add_start(message):
    if message.from_user.id != ADMIN_ID:
        return
    cats = get_categories()
    if not cats:
        bot.reply_to(message, "No categories yet. Create one with /newcategory first.")
        return
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i, (cid, name) in enumerate(cats, 1):
        markup.add(KeyboardButton(f"{i}. {name}"))
    markup.add(KeyboardButton("New category"))
    bot.reply_to(message, "Select category or create new:", reply_markup=markup)
    user_states[message.from_user.id] = {'state': 'add_category', 'data': {}}

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.chat.type == 'private')
def handle_steps(message):
    uid = message.from_user.id
    if uid not in user_states:
        return
    state = user_states[uid]['state']
    data = user_states[uid]['data']

    if state == 'new_category':
        name = message.text.strip()
        add_category(name)
        bot.reply_to(message, f"Category '{name}' added.")
        del user_states[uid]
        return

    if state == 'add_category':
        text = message.text.strip()
        cats = get_categories()
        if text == 'New category':
            bot.reply_to(message, "Enter new category name:", reply_markup=ForceReply())
            user_states[uid]['state'] = 'add_new_category'
            return
        try:
            num = int(text.split('.')[0])
            if 1 <= num <= len(cats):
                data['category_id'] = cats[num-1][0]
                bot.reply_to(message, "Enter product title:", reply_markup=ForceReply())
                user_states[uid]['state'] = 'add_title'
            else:
                bot.reply_to(message, "Invalid selection.")
        except:
            bot.reply_to(message, "Invalid selection.")
        return

    if state == 'add_new_category':
        name = message.text.strip()
        cat_id = add_category(name)
        data['category_id'] = cat_id
        bot.reply_to(message, "Enter product title:", reply_markup=ForceReply())
        user_states[uid]['state'] = 'add_title'
        return

    if state == 'add_title':
        data['title'] = message.text.strip()
        bot.reply_to(message, "Enter product bio/description:", reply_markup=ForceReply())
        user_states[uid]['state'] = 'add_bio'
        return

    if state == 'add_bio':
        data['bio'] = message.text.strip()
        bot.reply_to(message, "Enter price (number):", reply_markup=ForceReply())
        user_states[uid]['state'] = 'add_price'
        return

    if state == 'add_price':
        try:
            data['price'] = float(message.text.strip())
            bot.reply_to(message, "Send the product image as photo:")
            user_states[uid]['state'] = 'add_image'
        except:
            bot.reply_to(message, "Invalid price. Enter number:")
        return

    if state == 'add_image':
        if message.photo:
            file_id = message.photo[-1].file_id
            # Upload to channel
            sent_msg = bot.send_photo(CHANNEL_ID, file_id)
            # Get file info
            file_info = bot.get_file(file_id)
            image_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
            data['image_url'] = image_url
            # Now tags
            markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add("Discount", "Trending", "Both", "None")
            bot.reply_to(message, "Select tags:", reply_markup=markup)
            user_states[uid]['state'] = 'add_tags'
        else:
            bot.reply_to(message, "Please send a photo.")
        return

    if state == 'add_tags':
        text = message.text.strip()
        discount = 0
        trending = 0
        if text == 'Discount' or text == 'Both':
            bot.reply_to(message, "Enter discount percent (e.g. 20):", reply_markup=ForceReply())
            user_states[uid]['state'] = 'add_discount'
            user_states[uid]['temp'] = {'trending': 1 if text == 'Both' else 0}
            return
        elif text == 'Trending':
            trending = 1
        # Save
        add_product(data['title'], data['bio'], data['price'], data['image_url'], data['category_id'], discount, trending)
        bot.reply_to(message, "Product added!")
        del user_states[uid]
        return

    if state == 'add_discount':
        try:
            discount = float(message.text.strip())
            trending = user_states[uid]['temp']['trending']
            add_product(data['title'], data['bio'], data['price'], data['image_url'], data['category_id'], discount, trending)
            bot.reply_to(message, "Product added!")
            del user_states[uid]
        except:
            bot.reply_to(message, "Invalid number.")
        return

def run_bot():
    bot.infinity_polling()

# For edit/delete, can add later
