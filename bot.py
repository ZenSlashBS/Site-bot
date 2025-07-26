# bot.py
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ForceReply
import os
from db import add_category, get_categories, add_product, get_admins, add_admin, remove_admin, get_user_logs

TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = int(os.environ['ADMIN_ID'])  # This is now MAIN_ADMIN

MAIN_ADMIN = ADMIN_ID

bot = telebot.TeleBot(TOKEN)

user_states = {}  # {user_id: {'state': 'step', 'data': {...}}}

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in get_admins():
        return
    markup = InlineKeyboardMarkup(row_width=1)
    if uid == MAIN_ADMIN:
        markup.add(InlineKeyboardButton("👥 Users", callback_data="users"))
    markup.add(InlineKeyboardButton("➕ Add Product", callback_data="add_product"))
    markup.add(InlineKeyboardButton("🆕 New Category", callback_data="new_category"))
    bot.reply_to(message, "👋 Welcome! Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.from_user.id in get_admins() and m.chat.type == 'private')
def handle_steps(message):
    uid = message.from_user.id
    if uid not in user_states:
        return
    state = user_states[uid]['state']
    data = user_states[uid].get('data', {})

    if state == 'new_category':
        name = message.text.strip()
        add_category(name, uid)
        bot.reply_to(message, f"✅ Category '{name}' added.")
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
                data['is_creators'] = cats[num-1][1] == 'Creators'
                bot.reply_to(message, "Enter product title:", reply_markup=ForceReply())
                user_states[uid]['state'] = 'add_title'
            else:
                bot.reply_to(message, "❌ Invalid selection.")
        except:
            bot.reply_to(message, "❌ Invalid selection.")
        return

    if state == 'add_new_category':
        name = message.text.strip()
        cat_id = add_category(name, uid)
        data['category_id'] = cat_id
        data['is_creators'] = name == 'Creators'
        bot.reply_to(message, "📒 Enter product title:", reply_markup=ForceReply())
        user_states[uid]['state'] = 'add_title'
        return

    if state == 'add_title':
        data['title'] = message.text.strip()
        bot.reply_to(message, "📝 Enter product bio/description:", reply_markup=ForceReply())
        user_states[uid]['state'] = 'add_bio'
        return

    if state == 'add_bio':
        data['bio'] = message.text.strip()
        if data.get('is_creators', False):
            bot.reply_to(message, "☎️ Enter contact link (e.g : https://t.me/HazexPy):", reply_markup=ForceReply())
            user_states[uid]['state'] = 'add_contact'
        else:
            bot.reply_to(message, "🏷️ Enter price (Only number):", reply_markup=ForceReply())
            user_states[uid]['state'] = 'add_price'
        return

    if state == 'add_contact':
        data['contact_link'] = message.text.strip()
        bot.reply_to(message, "🔗 Enter image URL Use This Bot : @HostImg_bot", reply_markup=ForceReply())
        user_states[uid]['state'] = 'add_image'
        return

    if state == 'add_price':
        try:
            data['price'] = float(message.text.strip())
            bot.reply_to(message, "🔗 Enter image URL Use This Bot : @HostImg_bot", reply_markup=ForceReply())
            user_states[uid]['state'] = 'add_image'
        except:
            bot.reply_to(message, "❌ Invalid price. Enter number:")
        return

    if state == 'add_image':
        image_url = message.text.strip()
        if image_url.startswith('http') and (image_url.endswith('.jpg') or image_url.endswith('.png') or image_url.endswith('.gif')):
            data['image_path'] = image_url
            if data.get('is_creators', False):
                price = data.get('price', 0)
                contact_link = data.get('contact_link', None)
                add_product(data['title'], data['bio'], price, data['image_path'], data['category_id'], 0, 0, uid, contact_link)
                bot.reply_to(message, "✅ Creator added!")
                del user_states[uid]
            else:
                markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add("Discount", "Trending", "Both", "None")
                bot.reply_to(message, "Select tags:", reply_markup=markup)
                user_states[uid]['state'] = 'add_tags'
        else:
            bot.reply_to(message, "❌ Invalid image URL. Please enter a valid link ending with .jpg, .png, etc.")
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
        elif text == 'None':
            pass
        price = data.get('price', 0)
        contact_link = data.get('contact_link', None)
        add_product(data['title'], data['bio'], price, data['image_path'], data['category_id'], discount, trending, uid, contact_link)
        bot.reply_to(message, "✅ Product added!")
        del user_states[uid]
        return

    if state == 'add_discount':
        try:
            discount = float(message.text.strip())
            trending = user_states[uid]['temp']['trending']
            price = data.get('price', 0)
            contact_link = data.get('contact_link', None)
            add_product(data['title'], data['bio'], price, data['image_path'], data['category_id'], discount, trending, uid, contact_link)
            bot.reply_to(message, "✅ Product added!")
            del user_states[uid]
        except:
            bot.reply_to(message, "❌ Invalid number.")
        return

    if state == 'add_user_id':
        try:
            new_id = int(message.text.strip())
            add_admin(new_id)
            bot.reply_to(message, f"✅ User {new_id} added.")
            del user_states[uid]
        except:
            bot.reply_to(message, "❌ Invalid user ID.")
        return

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.from_user.id
    if uid not in get_admins():
        return
    data = call.data

    if data == "add_product":
        cats = get_categories()
        if not cats:
            bot.answer_callback_query(call.id, "No categories yet. Create one first.", show_alert=True)
            return
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for i, (cid, name) in enumerate(cats, 1):
            markup.add(KeyboardButton(f"{i}. {name}"))
        markup.add(KeyboardButton("New category"))
        bot.send_message(call.message.chat.id, "Select category or create new:", reply_markup=markup)
        user_states[uid] = {'state': 'add_category', 'data': {}}
        bot.answer_callback_query(call.id)
        return

    if data == "new_category":
        bot.send_message(call.message.chat.id, "Enter the new category name:", reply_markup=ForceReply())
        user_states[uid] = {'state': 'new_category'}
        bot.answer_callback_query(call.id)
        return

    if uid != MAIN_ADMIN:
        return  # Only main admin for users management

    if data == "users":
        admins = get_admins()
        text = "👥 Allowed Users:"
        markup = InlineKeyboardMarkup(row_width=1)
        for a in admins:
            if a != MAIN_ADMIN:
                markup.add(InlineKeyboardButton(f"🧑 User {a}", callback_data=f"user:{a}"))
        markup.add(InlineKeyboardButton("➕ Add User", callback_data="add_user"))
        markup.add(InlineKeyboardButton("🔙 Back to Home", callback_data="home"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
        return

    if data.startswith("user:"):
        user_id = int(data.split(":")[1])
        logs = get_user_logs(user_id)
        text = f"🧑 User ID: {user_id}\n\n📋 Actions:"
        if logs:
            for action, details, ts in logs[:10]:  # Limit to recent 10
                text += f"\n• {ts}: {action} {details or ''}"
        else:
            text += "\nNo actions yet."
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("🗑 Remove User", callback_data=f"remove_user:{user_id}"))
        markup.add(InlineKeyboardButton("🔙 Back to Users", callback_data="users"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
        return

    if data == "add_user":
        bot.edit_message_text("📩 Send the user ID to add:", call.message.chat.id, call.message.id)
        user_states[uid] = {'state': 'add_user_id'}
        bot.answer_callback_query(call.id)
        return

    if data.startswith("remove_user:"):
        user_id = int(data.split(":")[1])
        if user_id == MAIN_ADMIN:
            bot.answer_callback_query(call.id, "Cannot remove main admin.", show_alert=True)
            return
        remove_admin(user_id)
        bot.answer_callback_query(call.id, "✅ User removed.")
        # Back to users list
        admins = get_admins()
        text = "👥 Allowed Users:"
        markup = InlineKeyboardMarkup(row_width=1)
        for a in admins:
            if a != MAIN_ADMIN:
                markup.add(InlineKeyboardButton(f"🧑 User {a}", callback_data=f"user:{a}"))
        markup.add(InlineKeyboardButton("➕ Add User", callback_data="add_user"))
        markup.add(InlineKeyboardButton("🔙 Back to Home", callback_data="home"))
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
        return

    if data == "home":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("👥 Users", callback_data="users"))
        markup.add(InlineKeyboardButton("➕ Add Product", callback_data="add_product"))
        markup.add(InlineKeyboardButton("🆕 New Category", callback_data="new_category"))
        bot.edit_message_text("👋 Welcome! Choose an option:", call.message.chat.id, call.message.id, reply_markup=markup)
        return
