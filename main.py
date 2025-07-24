# main.py
import os
import threading
from bot import bot
from app import app
from db import init_db

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if 'RAILWAY_PUBLIC_DOMAIN' in os.environ:
        app_url = f"https://{os.environ['RAILWAY_PUBLIC_DOMAIN']}"
        bot.remove_webhook()
        bot.set_webhook(url=app_url + '/webhook')
    else:
        # Local development: use polling
        threading.Thread(target=bot.infinity_polling, daemon=True).start()

    app.run(host='0.0.0.0', port=port, debug=False)
