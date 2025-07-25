# main.py
import os
import threading
from bot import bot, MAIN_ADMIN
from app import app
from db import init_db, add_admin

init_db()

# Add main admin if not exists
add_admin(MAIN_ADMIN)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app_url = "https://site-bot-production.up.railway.app"  # Hardcoded subdomain for webhook
    bot.remove_webhook()
    bot.set_webhook(url=app_url + '/webhook')
    app.run(host='0.0.0.0', port=port, debug=False)
