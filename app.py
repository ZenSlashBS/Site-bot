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
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Aarav's Marketplace</title>
  <link rel="icon" href="https://iili.io/FkCxdk7.jpg">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
  <style>
    /* — Body & background unchanged — */
    body {
      background-color:#0f0f0f; color:#fff; font-family:'Roboto',sans-serif;
      margin:0; padding:0;
      background-attachment:fixed; background-size:cover;
      background-image:
        radial-gradient(circle at top left, rgba(0,255,0,0.3),transparent 50%),
        radial-gradient(circle at bottom right, rgba(0,255,0,0.3),transparent 50%),
        linear-gradient(to right,#0f0f0f,#001a00);
      background-blend-mode:screen;
      animation:gradient-shift 10s ease infinite;
    }
    @keyframes gradient-shift {0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

    /* — Tube light & sparkles unchanged — */
    .tube-light { /* … */ }
    @keyframes blink-error { /* … */ }
    .sparkle { /* … */ }
    @keyframes sparkle-fall { /* … */ }

    /* — Header & hero unchanged — */
    header { /* … */ }
    .logo-container { /* … */ }
    .logo-img { /* … */ }
    .logo-text { /* … */ }
    @keyframes glow { /* … */ }
    .hero { /* … */ }

    /* — Category header styling — */
    .category-name {
      font-size:20px; color:#f5f5f5;
      background:rgba(255,255,255,0.05);
      padding:8px 16px; border-radius:12px;
      display:inline-block; margin-bottom:15px;
    }

    /* — Carousel & cards unchanged — */
    .category {margin-bottom:40px;padding:20px;}
    .carousel {display:flex;overflow-x:auto;scrollbar-width:none;}
    .carousel::-webkit-scrollbar{display:none;}
    .card { /* … */ }
    .card:hover { /* … */ }
    .card img { /* … */ }
    .creators .card img { /* … */ }
    .title, .bio, .price, .badges, .badge, .purchase { /* … */ }

    /* — Modal overlay at 40% black — */
    .modal {
      display:none; position:fixed; z-index:1;
      inset:0;
      background:rgba(0,0,0,0.4);
      backdrop-filter:blur(5px);
    }
    .modal-content {
      position:relative;
      background:rgba(31,31,31,0.8);
      backdrop-filter:blur(10px);
      width:90%; max-width:600px;
      margin:10% auto;
      border-radius:20px;
      padding:0;
      display:flex; flex-direction:column;
      max-height:80vh;
      overflow:hidden;
    }
    /* — Image container with badges overlay — */
    .modal-image {
      position:relative;
      width:100%;
      flex-shrink:0;
    }
    .modal-image img {
      display:block;
      width:100%;
      {% raw %}{% if cat=='Creators' %}border-radius:50%;max-width:200px;height:200px;margin:20px auto 0;{% else %}border-top-left-radius:20px;border-top-right-radius:20px;{% endif %}{% endraw %}
    }
    .modal-image .badges {
      position:absolute;
      top:10px; left:10px;
      display:flex; flex-wrap:wrap; gap:6px;
    }
    .modal-image .badge {
      font-size:12px; padding:5px 8px;
      border-radius:5px; color:#fff;
    }
    /* — Title just under image — */
    .modal-content h2 {
      margin:10px 16px 4px;
      font-size:22px;
    }
    /* — Body text tight under title — */
    .modal-body {
      padding:0 16px;
      margin-bottom:8px;
      overflow-y:auto;
      flex:1 1 auto;
    }
    /* — Footer (price+btn) snug at bottom — */
    .modal-footer {
      padding:0 16px 16px;
      display:flex; flex-direction:column; gap:8px;
    }
    .modal-footer .price {margin:0;}
    .modal-footer .purchase {margin:0;}
    .close {
      position:absolute; top:12px; right:16px;
      font-size:24px; color:#aaa; cursor:pointer;
    }
    .close:hover {color:#fff;}

    .no-products {text-align:center;color:#aaa;padding:40px 0;}
  </style>
</head>
<body>
  <div class="tube-light"></div>
  <header>…</header>
  <section class="hero">…</section>

  {% for cat in categories %}
    {% set prods = grouped.get(cat, []) %}
    <div class="category{% if cat=='Creators' %} creators{% endif %}">
      <div class="category-name">{{ cat }}</div>
      {% if prods %}
        <div class="carousel">
          {% for prod in prods %}
            <div class="card" onclick="…openModal('{{ prod.id }}')">
              <!-- card markup unchanged -->
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
          <div class="modal-image">
            <img src="{{ prod.image_path }}" alt="{{ prod.title }}">
            <div class="badges">
              {% if prod.discount_percent>0 %}<div class="badge discount">{{ prod.discount_percent }}% OFF</div>{% endif %}
              {% if prod.is_new %}<div class="badge new">NEW</div>{% endif %}
              {% if prod.is_trending %}<div class="badge trending">TRENDING</div>{% endif %}
            </div>
            <span class="close" onclick="closeModal('{{ prod.id }}')">×</span>
          </div>
          <h2>{{ prod.title }}</h2>
          <div class="modal-body">
            <p>{{ prod.bio }}</p>
          </div>
          <div class="modal-footer">
            {% if cat!='Creators' %}
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
      document.getElementById('modal-'+id).style.display='block';
    }
    function closeModal(id) {
      document.getElementById('modal-'+id).style.display='none';
    }
    window.onclick = e => {
      if (e.target.classList.contains('modal')) e.target.style.display='none';
    };
    function createSparkle(){
      const tube = document.querySelector('.tube-light');
      if(!tube) return;
      const r = tube.getBoundingClientRect();
      const s = document.createElement('div');
      s.className='sparkle';
      s.style.left=(r.left+Math.random()*r.width)+'px';
      s.style.top =(r.top +Math.random()*r.height)+'px';
      document.body.appendChild(s);
      setTimeout(()=>s.remove(),3000);
    }
    setInterval(createSparkle,200);
  </script>
</body>
</html>
'''
