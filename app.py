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
            'id': p[0],
            'title': p[1],
            'bio': p[2],
            'price': p[3],
            'image_path': p[4],
            'discount_percent': p[7],
            'is_trending': p[8],
            'is_new': is_new,
            'contact_link': p[9]
        })

    # fetch all categories, put Creators last
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
  <title>HazexPy Shop</title>
  <link rel="icon" href="https://iili.io/FkiXi6x.jpg">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
  <style>
    body {
      background-color: #0f0f0f;
      color: #fff;
      font-family: 'Roboto',sans-serif;
      margin:0; padding:0;
      background-attachment:fixed;
      background-size:cover;
      background-image:
        radial-gradient(circle at top left, rgba(0,255,0,0.3),transparent 50%),
        radial-gradient(circle at bottom right, rgba(0,255,0,0.3),transparent 50%),
        linear-gradient(to right,#0f0f0f,#001a00);
      background-blend-mode:screen;
      animation:gradient-shift 10s ease infinite;
    }
    @keyframes gradient-shift {
      0%   {background-position:0% 50%;}
      50%  {background-position:100% 50%;}
      100% {background-position:0% 50%;}
    }
    .tube-light {
      position:fixed;
      top:50%; left:50%;
      transform:translate(-50%,-50%) rotate(45deg);
      width:300px; height:10px;
      background:#00ff00;
      box-shadow:0 0 20px #00ff00,0 0 40px #00ff00;
      opacity:0.8;
      animation:blink-error 2s infinite alternate;
      z-index:-1;
    }
    @keyframes blink-error {
      0%   {opacity:0.8; box-shadow:0 0 20px #00ff00;}
      20%  {opacity:0.4; box-shadow:0 0 10px #00ff00;}
      40%  {opacity:0.8;}
      60%  {opacity:0.2; box-shadow:0 0 5px #00ff00;}
      80%  {opacity:0.6;}
      100% {opacity:0.8; box-shadow:0 0 20px #00ff00;}
    }
    .sparkle {position:fixed;width:5px;height:5px;background:#00ff00;border-radius:50%;box-shadow:0 0 10px #00ff00;animation:sparkle-fall 3s linear infinite;z-index:-1;}
    @keyframes sparkle-fall {0%{transform:translate(0,0) scale(1);opacity:1;}100%{transform:translate(0,100vh) scale(0.5);opacity:0;}}
    header {display:flex;align-items:center;padding:20px;background:rgba(0,0,0,0.5);backdrop-filter:blur(10px);}
    .logo-container {display:flex;align-items:center;}
    .logo-img {width:40px;height:40px;border-radius:50%;margin-right:10px;}
    .logo-text {font-size:24px;color:#00ff00;text-shadow:0 0 10px #00ff00;animation:glow 2s ease infinite;}
    @keyframes glow {0%{text-shadow:0 0 5px #00ff00;}50%{text-shadow:0 0 15px #00ff00;}100%{text-shadow:0 0 5px #00ff00;}}
    .hero {text-align:center;padding:50px;background:rgba(15,15,15,0.7);backdrop-filter:blur(10px);margin:20px;border-radius:20px;}
    .category-name {font-size:20px;color:#f5f5f5;background:rgba(255,255,255,0.05);padding:8px 16px;border-radius:12px;display:inline-block;margin-bottom:15px;}
    .category {margin-bottom:40px;display:block;padding:20px;}
    .carousel {display:flex;overflow-x:auto;scrollbar-width:none;}
    .carousel::-webkit-scrollbar{display:none;}
    .card {min-width:250px;margin:10px;background:rgba(31,31,31,0.7);backdrop-filter:blur(10px);border-radius:10px;padding:10px;text-align:center;position:relative;transition:transform .3s;cursor:pointer;display:flex;flex-direction:column;border:1px solid rgba(255,255,255,0.1);}
    .card:hover {transform:scale(1.05);box-shadow:0 0 20px rgba(0,255,0,0.3);}
    .image-container {position:relative;}
    .card img {width:100%;height:200px;object-fit:cover;border-radius:10px;}
    .creators .card img {border-radius:50%;width:200px;height:200px;margin:0 auto;}
    .title {font-size:18px;font-weight:bold;margin-top:10px;}
    .bio {font-size:14px;white-space:pre-wrap;overflow:hidden;text-overflow:ellipsis;max-height:60px;}
    .price {font-size:16px;color:#00ff00;margin-bottom:0;}
    .badges {position:absolute;top:10px;left:10px;display:flex;flex-direction:column;gap:5px;z-index:1;}
    .badge {padding:5px 10px;border-radius:5px;font-size:12px;color:#fff;}
    .discount {background:#e74c3c;}
    .new {background:#2ecc71;}
    .trending {background:linear-gradient(45deg,#8e44ad,#3498db,#2ecc71);background-size:300% 300%;animation:rainbow 4s ease infinite;}
    @keyframes rainbow {0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
    .purchase {background:linear-gradient(to right,#00ff00,#00cc00);color:#000;padding:10px;border-radius:5px;text-decoration:none;margin-top:0;transition:box-shadow .3s;}
    .purchase:hover {box-shadow:0 0 10px #00ff00;}
    .modal {display:none;position:fixed;z-index:1;left:0;top:0;width:100%;height:100%;background-color:rgba(0,0,0,0.4);backdrop-filter:blur(5px);}
    .modal-content {background:rgba(31,31,31,0.8);backdrop-filter:blur(10px);margin:10% auto;padding:20px;border-radius:20px;max-width:600px;display:flex;flex-direction:column;max-height:80vh;overflow:hidden;position:relative;}
    .modal-body {overflow-y:auto;flex:1 1 auto;margin-bottom:20px;}
    .modal-footer {display:flex;flex-direction:column;gap:10px;}
    .close {position:absolute;top:15px;right:20px;font-size:28px;color:#aaa;cursor:pointer;}
    .close:hover{color:#fff;}
    .no-products {text-align:center;color:#aaa;padding:40px 0;}
    .modal .image-container {position:relative;}
    .modal .badges {position:absolute;top:10px;left:10px;display:flex;flex-direction:column;gap:5px;z-index:1;}
  </style>
</head>
<body>
  <div class="tube-light"></div>
  <header>
    <div class="logo-container">
      <img src="https://iili.io/FkCxdk7.jpg" class="logo-img" alt="Logo">
      <span class="logo-text">Aarav's Marketplace</span>
    </div>
  </header>
  <section class="hero">
    <h1>Shop Source Code</h1>
    <p>Shop Made by : @SikeNezReborn On Telegram ❤️</p>
  </section>

  {% for cat in categories %}
    {% set prods = grouped.get(cat, []) %}
    <div class="category{% if cat=='Creators' %} creators{% endif %}">
      <div class="category-name">{{ cat }}</div>
      {% if prods %}
        <div class="carousel">
          {% for prod in prods %}
            <div class="card"
                 onclick="event.target.closest('.card').querySelector('.purchase')!==event.target&&openModal('{{ prod.id }}')">
              <div class="image-container">
                <img src="{{ prod.image_path }}" alt="{{ prod.title }}">
                <div class="badges">
                  {% if prod.discount_percent>0 %}<div class="badge discount">{{ prod.discount_percent }}% OFF</div>{% endif %}
                  {% if prod.is_new %}<div class="badge new">NEW</div>{% endif %}
                  {% if prod.is_trending %}<div class="badge trending">TRENDING</div>{% endif %}
                </div>
              </div>
              <div class="title">{{ prod.title }}</div>
              <div class="bio">{{ prod.bio[:100] }}{% if prod.bio|length>100 %}...{% endif %}</div>
              {% if cat!='Creators' %}
                <div class="price">${{ '%.2f' % prod.price }}</div>
                <a class="purchase"
                   href="https://t.me/SikeNezReborn?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title|urlencode }}">
                  Purchase
                </a>
              {% else %}
                <a class="purchase" href="{{ prod.contact_link }}">Contact</a>
              {% endif %}
            </div>
          {% endfor %}
        </div>
      {% else %}
        <div class="no-products">
          {% if cat=='Creators' %}No creator yet.{% else %}No products available yet.{% endif %}
        </div>
      {% endif %}
    </div>
  {% endfor %}

  {% for cat in categories %}
    {% for prod in grouped.get(cat, []) %}
      <div id="modal-{{ prod.id }}" class="modal">
        <div class="modal-content">
          <span class="close" onclick="closeModal('{{ prod.id }}')">×</span>
          <h2>{{ prod.title }}</h2>
          <div class="image-container">
            <img src="{{ prod.image_path }}"
                 style="{% if cat=='Creators' %}border-radius:50%;max-width:200px;height:200px;display:block;margin:0 auto;{% endif %}width:100%;">
            <div class="badges">
              {% if prod.discount_percent>0 %}<div class="badge discount">{{ prod.discount_percent }}% OFF</div>{% endif %}
              {% if prod.is_new %}<div class="badge new">NEW</div>{% endif %}
              {% if prod.is_trending %}<div class="badge trending">TRENDING</div>{% endif %}
            </div>
          </div>
          <div class="modal-body">
            <p>{{ prod.bio }}</p>
          </div>
          <div class="modal-footer">
            {% if cat!='Creators' %}
              <div class="price">${{ '%.2f' % prod.price }}</div>
              <a class="purchase"
                 href="https://t.me/SikeNezReborn?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title|urlencode }}">
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
      if (e.target.classList.contains('modal')) e.target.style.display = 'none';
    };

    function createSparkle() {
      const tube = document.querySelector('.tube-light');
      if (!tube) return;
      const r = tube.getBoundingClientRect();
      const s = document.createElement('div');
      s.classList.add('sparkle');
      s.style.left = (r.left + Math.random()*r.width) + 'px';
      s.style.top  = (r.top  + Math.random()*r.height) + 'px';
      document.body.appendChild(s);
      setTimeout(() => s.remove(), 3000);
    }
    setInterval(createSparkle, 200);
  </script>
</body>
</html>
'''
