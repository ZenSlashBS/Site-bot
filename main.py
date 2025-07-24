# main.py
import os
import threading
from bot import run_bot
from app import app
from db import init_db

init_db()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
