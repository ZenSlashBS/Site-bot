# app.py
from flask import Flask, render_template_string, request, Response
from db import get_products, init_db
from datetime import datetime, timedelta
from bot import bot, TOKEN
import telebot  # Added this import to fix the NameError
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
    init_db()  # Ensure DB exists
    products = get_products()
    # Group by category
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
    return render_template_string(HTML_TEMPLATE, grouped=grouped)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aarav's Marketplace</title>
    <link rel="icon" href="https://iili.io/FkCxdk7.jpg" type="image/jpg">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
    <style>
        body { 
            background-color: #0f0f0f; 
            color: #fff; 
            font-family: 'Roboto', sans-serif; 
            margin: 0; 
            padding: 0; 
            background-image: radial-gradient(circle at top left, rgba(0,255,0,0.3), transparent 50%), 
                              radial-gradient(circle at bottom right, rgba(0,255,0,0.3), transparent 50%), 
                              linear-gradient(to right, #0f0f0f, #001a00); 
            background-blend-mode: screen;
            animation: gradient-shift 10s ease infinite;
        }
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .tube-light {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(45deg);
            width: 300px;
            height: 10px;
            background: #00ff00;
            box-shadow: 0 0 20px #00ff00, 0 0 40px #00ff00;
            opacity: 0.8;
            animation: blink-error 2s infinite alternate;
            z-index: -1;
        }
        @keyframes blink-error {
            0% { opacity: 0.8; box-shadow: 0 0 20px #00ff00; }
            20% { opacity: 0.4; box-shadow: 0 0 10px #00ff00; }
            40% { opacity: 0.8; }
            60% { opacity: 0.2; box-shadow: 0 0 5px #00ff00; }
            80% { opacity: 0.6; }
            100% { opacity: 0.8; box-shadow: 0 0 20px #00ff00; }
        }
        .sparkle {
            position: fixed;
            width: 5px;
            height: 5px;
            background: #00ff00;
            border-radius: 50%;
            box-shadow: 0 0 10px #00ff00;
            animation: sparkle-fall 3s linear infinite;
            z-index: -1;
        }
        @keyframes sparkle-fall {
            0% { transform: translate(0, 0) scale(1); opacity: 1; }
            100% { transform: translate(0, 100vh) scale(0.5); opacity: 0; }
        }
        header {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            padding: 20px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
        }
        .logo-container {
            display: flex;
            align-items: center;
        }
        .logo-img {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .logo-text {
            font-size: 24px;
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            animation: glow 2s ease infinite;
        }
        @keyframes glow {
            0% { text-shadow: 0 0 5px #00ff00; }
            50% { text-shadow: 0 0 15px #00ff00; }
            100% { text-shadow: 0 0 5px #00ff00; }
        }
        .hero {
            text-align: center;
            padding: 50px;
            background: rgba(15,15,15,0.7);
            backdrop-filter: blur(10px);
            margin: 20px;
            border-radius: 20px;
        }
        .category { margin-bottom: 40px; display: block; padding: 20px; }
        .category-name { font-size: 24px; color: #00ffff; padding: 10px 0; width: auto; }
        .carousel { display: flex; overflow-x: auto; scrollbar-width: none; width: 100%; }
        .carousel::-webkit-scrollbar { display: none; }
        .card { 
            min-width: 250px; 
            margin: 10px; 
            background: rgba(31,31,31,0.7); 
            backdrop-filter: blur(10px); 
            border-radius: 10px; 
            padding: 10px; 
            text-align: center; 
            position: relative; 
            transition: transform 0.3s; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            border: 1px solid rgba(0,255,0,0.2);
        }
        .card:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(0,255,0,0.5); }
        .card img { width: 100%; height: 200px; object-fit: cover; border-radius: 10px; }
        .creators .card img { border-radius: 50%; width: 200px; height: 200px; margin: 0 auto; }
        .title { font-size: 18px; font-weight: bold; }
        .bio { font-size: 14px; white-space: pre-wrap; overflow: hidden; text-overflow: ellipsis; max-height: 60px; }
        .price { font-size: 16px; color: #00ff00; }
        .badges { position: absolute; top: 10px; left: 10px; display: flex; flex-direction: column; gap: 5px; }
        .badge { padding: 5px 10px; border-radius: 5px; font-size: 12px; width: fit-content; }
        .discount { background: red; }
        .new { background: green; }
        .trending { background: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet); background-size: 400% 400%; animation: rainbow 5s ease infinite; color: #fff; }
        @keyframes rainbow { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
        .purchase { background: linear-gradient(to right, #00ff00, #00cc00); color: #000; padding: 10px; border-radius: 5px; text-decoration: none; display: block; margin-top: auto; transition: box-shadow 0.3s; }
        .purchase:hover { box-shadow: 0 0 10px #00ff00; }
        .modal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.8); backdrop-filter: blur(5px); }
        .modal-content { background: rgba(31,31,31,0.8); backdrop-filter: blur(10px); margin: 15% auto; padding: 20px; border: 1px solid rgba(0,255,0,0.2); width: 80%; max-width: 600px; border-radius: 20px; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; }
        .close:hover { color: #fff; cursor: pointer; }
        .no-products { text-align: center; color: #aaa; flex: 1; }
        .modal-content .badges { position: relative; display: flex; flex-direction: row; flex-wrap: wrap; gap: 5px; justify-content: center; margin-bottom: 10px; }
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
        <h1>Marketplace For The Pro Crackers</h1>
        <p>Discover And Get The Tool U Need For The Ultimate Hacking Experience.</p>
    </section>
    {% if grouped %}
    {% for cat, prods in grouped.items() %}
    <div class="category{% if cat == 'Creators' %} creators{% endif %}">
        <div class="category-name">{{ cat }}</div>
        {% if prods %}
        <div class="carousel">
            {% for prod in prods %}
            <div class="card" onclick="event.target.closest('.card').querySelector('.purchase') !== event.target && openModal('{{ prod.id }}')">
                <img src="{{ prod.image_path }}" alt="{{ prod.title }}">
                <div class="badges">
                    {% if prod.discount_percent > 0 %}
                    <div class="badge discount">{{ prod.discount_percent }}% OFF</div>
                    {% endif %}
                    {% if prod.is_new %}
                    <div class="badge new">NEW</div>
                    {% endif %}
                    {% if prod.is_trending %}
                    <div class="badge trending">TRENDING</div>
                    {% endif %}
                </div>
                <div class="title">{{ prod.title }}</div>
                <div class="bio">{{ prod.bio[:100] }}{% if prod.bio|length > 100 %}...{% endif %}</div>
                {% if cat != 'Creators' %}
                <div class="price">${{ "%.2f" % prod.price }}</div>
                <a class="purchase" href="https://t.me/philoxnex?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title | urlencode }}">Purchase</a>
                {% else %}
                <a class="purchase" href="{{ prod.contact_link }}">Contact</a>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-products">No products available yet.</div>
        {% endif %}
    </div>
    {% endfor %}
    {% else %}
    <div class="no-products">No products available yet.</div>
    {% endif %}
    <!-- Modals -->
    {% for cat, prods in grouped.items() %}
    {% for prod in prods %}
    <div id="modal-{{ prod.id }}" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('{{ prod.id }}')">×</span>
            <h2>{{ prod.title }}</h2>
            <div class="badges">
                {% if prod.discount_percent > 0 %}
                <div class="badge discount">{{ prod.discount_percent }}% OFF</div>
                {% endif %}
                {% if prod.is_new %}
                <div class="badge new">NEW</div>
                {% endif %}
                {% if prod.is_trending %}
                <div class="badge trending">TRENDING</div>
                {% endif %}
            </div>
            <img src="{{ prod.image_path }}" style="width:100%;{% if cat == 'Creators' %} border-radius:50%; max-width:200px; height:200px; display:block; margin:0 auto;{% endif %}">
            <p>{{ prod.bio }}</p>
            {% if cat != 'Creators' %}
            <div class="price">${{ "%.2f" % prod.price }}</div>
            <a class="purchase" href="https://t.me/philoxnex?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title | urlencode }}">Purchase</a>
            {% else %}
            <a class="purchase" href="{{ prod.contact_link }}">Contact</a>
            {% endif %}
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
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }
        // Add sparkles
        function createSparkle() {
            const sparkle = document.createElement('div');
            sparkle.classList.add('sparkle');
            sparkle.style.left = (50 + (Math.random() - 0.5) * 100) + '%';
            sparkle.style.top = (50 + (Math.random() - 0.5) * 100) + '%';
            sparkle.style.animationDelay = Math.random() * 2 + 's';
            document.body.appendChild(sparkle);
            setTimeout(() => sparkle.remove(), 3000);
        }
        setInterval(createSparkle, 200);
    </script>
</body>
</html>
'''
