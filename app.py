# app.py
from flask import Flask, render_template_string, request
from db import get_products, init_db, get_categories
from datetime import datetime, timedelta
from bot import bot, TOKEN
import telebot
import os
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    else:
        return 'Unauthorized', 403

@app.route('/')
def index():
    init_db()
    products = get_products()

    from collections import defaultdict
    grouped = defaultdict(list)
    for p in products:
        created_at = datetime.fromisoformat(p[6])
        is_new = (datetime.now() - created_at) < timedelta(hours=24)
        grouped[p[10]].append({
            'id':             p[0],
            'title':          p[1],
            'bio':            p[2],
            'price':          p[3],
            'image_path':     p[4],
            'discount_percent': p[7],
            'is_trending':    p[8],
            'is_new':         is_new,
            'contact_link':   p[9]
        })

    # build categories: all except Creators, sorted, then Creators last
    cats = [name for _, name in get_categories() if name != 'Creators']
    cats.sort()
    cats.append('Creators')

    return render_template_string(HTML_TEMPLATE,
                                 grouped=grouped,
                                 categories=cats)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Aarav's Marketplace</title>
  <link rel="icon" href="https://iili.io/FkCxdk7.jpg">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
  <style>
    /* --- existing global styles (gradient, header, cards, etc.) unchanged --- */

    /* Modal overlay */
    .modal {
      display: none;
      position: fixed;
      z-index: 1;
      left: 0; top: 0;
      width: 100%; height: 100%;
      background-color: rgba(0,0,0,0.4);
      backdrop-filter: blur(5px);
    }

    /* Modal container */
    .modal-content {
      position: relative;
      background: rgba(31,31,31,0.8);
      backdrop-filter: blur(10px);
      margin: 10% auto;
      padding: 0;
      border-radius: 20px;
      max-width: 600px;
      max-height: 80vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* Close button */
    .close {
      position: absolute;
      top: 15px; right: 20px;
      font-size: 28px; color: #aaa;
      cursor: pointer;
      z-index: 2;
    }
    .close:hover { color: #fff; }

    /* Product image */
    .modal-content img {
      width: 100%;
      height: auto;
      object-fit: cover;
      display: block;
      flex-shrink: 0;
    }

    /* Badges overlap the image */
    .modal-content .badges {
      position: absolute;
      top: 15px; left: 15px;
      display: flex;
      flex-direction: row;
      gap: 8px;
      z-index: 3;
    }

    .modal-content .badge {
      padding: 5px 10px;
      border-radius: 5px;
      font-size: 12px;
      color: #fff;
      white-space: nowrap;
    }
    .modal-content .discount { background: #e74c3c; }
    .modal-content .new      { background: #2ecc71; }
    .modal-content .trending {
      background: linear-gradient(45deg,#8e44ad,#3498db,#2ecc71);
      background-size: 300% 300%;
      animation: rainbow 4s ease infinite;
    }
    @keyframes rainbow {
      0%   { background-position: 0% 50%; }
      50%  { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* Title */
    .modal-content h2 {
      margin: 12px 20px 4px;
      font-size: 22px;
      color: #fff;
    }

    /* Bio text */
    .modal-body {
      padding: 0 20px;
      margin-bottom: 8px;
      overflow-y: auto;
      flex: 1 1 auto;
    }
    .modal-body p {
      margin: 0;
      line-height: 1.4;
      color: #ddd;
    }

    /* Footer: price & button */
    .modal-footer {
      padding: 0 20px 20px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .modal-footer .price {
      margin: 0;
      font-size: 18px;
      color: #00ff00;
    }
    .modal-footer .purchase {
      margin: 0;
      padding: 12px;
      font-size: 16px;
      border-radius: 8px;
    }

  </style>
</head>
<body>
  <!-- ... header, hero, categories carousel ... -->

  <!-- Modals -->
  {% for cat in categories %}
    {% for prod in grouped.get(cat, []) %}
      <div id="modal-{{ prod.id }}" class="modal">
        <div class="modal-content">
          <span class="close" onclick="closeModal('{{ prod.id }}')">×</span>

          <!-- Product image -->
          <img src="{{ prod.image_path }}" alt="{{ prod.title }}">

          <!-- Badges over image -->
          <div class="badges">
            {% if prod.discount_percent>0 %}
              <div class="badge discount">{{ prod.discount_percent }}% OFF</div>
            {% endif %}
            {% if prod.is_new %}
              <div class="badge new">NEW</div>
            {% endif %}
            {% if prod.is_trending %}
              <div class="badge trending">TRENDING</div>
            {% endif %}
          </div>

          <!-- Title -->
          <h2>{{ prod.title }}</h2>

          <!-- Bio -->
          <div class="modal-body">
            <p>{{ prod.bio }}</p>
          </div>

          <!-- Price & Purchase -->
          <div class="modal-footer">
            {% if cat != 'Creators' %}
              <div class="price">${{ '%.2f' % prod.price }}</div>
              <a class="purchase"
                 href="https://t.me/philoxnex?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title|urlencode }}">
                Purchase
              </a>
            {% else %}
              <a class="purchase" href="{{ prod.contact_link }}">Contact</a>
            {% endif %}
          </div>
        </div>
      </div>
    {% endfor %}
  {% endfor %}

  <script>
    function openModal(id) {
      document.getElementById('modal-' + id).style.display = 'block';
    }
    function closeModal(id) {
      document.getElementById('modal-' + id).style.display = 'none';
    }
    window.onclick = e => {
      if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
      }
    };

    // Sparkles from tube-light...
    function createSparkle() {
      const tube = document.querySelector('.tube-light');
      if (!tube) return;
      const rect = tube.getBoundingClientRect();
      const spark = document.createElement('div');
      spark.classList.add('sparkle');
      spark.style.left = (rect.left + Math.random() * rect.width) + 'px';
      spark.style.top  = (rect.top  + Math.random() * rect.height) + 'px';
      document.body.appendChild(spark);
      setTimeout(() => spark.remove(), 3000);
    }
    setInterval(createSparkle, 200);
  </script>
</body>
</html>
'''
