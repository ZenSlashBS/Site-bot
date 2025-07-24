# app.py
from flask import Flask, render_template_string
from db import get_products, init_db
from datetime import datetime, timedelta
import os

app = Flask(__name__)

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
        grouped[p[9]].append({
            'id': p[0],
            'title': p[1],
            'bio': p[2],
            'price': p[3],
            'image_url': p[4],
            'discount_percent': p[7],
            'is_trending': p[8],
            'is_new': is_new
        })
    return render_template_string(HTML_TEMPLATE, grouped=grouped)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketplace</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #0f0f0f; color: #fff; font-family: 'Roboto', sans-serif; margin: 0; padding: 20px; }
        h1 { text-align: center; color: #00ff00; }
        .category { margin-bottom: 40px; }
        .category-name { font-size: 24px; color: #00ffff; position: sticky; left: 0; background: #0f0f0f; padding: 10px; width: 200px; display: inline-block; vertical-align: top; }
        .carousel { display: flex; overflow-x: auto; scrollbar-width: none; }
        .carousel::-webkit-scrollbar { display: none; }
        .card { min-width: 250px; margin: 10px; background: #1f1f1f; border-radius: 10px; padding: 10px; text-align: center; position: relative; transition: transform 0.3s; }
        .card:hover { transform: scale(1.05); }
        .card img { width: 100%; height: 200px; object-fit: cover; border-radius: 10px; }
        .title { font-size: 18px; font-weight: bold; }
        .bio { font-size: 14px; white-space: pre-wrap; overflow: hidden; text-overflow: ellipsis; max-height: 60px; }
        .price { font-size: 16px; color: #00ff00; }
        .badge { position: absolute; top: 10px; left: 10px; padding: 5px; border-radius: 5px; font-size: 12px; }
        .discount { background: red; }
        .new { background: green; }
        .trending { background: linear-gradient(45deg, red, orange, yellow, green, blue, indigo, violet); background-size: 400% 400%; animation: rainbow 5s ease infinite; color: #fff; }
        @keyframes rainbow { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
        .purchase { background: #00ff00; color: #000; padding: 10px; border-radius: 5px; text-decoration: none; display: block; margin-top: 10px; }
        .modal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.8); }
        .modal-content { background-color: #1f1f1f; margin: 15% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 600px; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; }
        .close:hover { color: #fff; cursor: pointer; }
        .no-products { text-align: center; color: #aaa; }
    </style>
</head>
<body>
    <h1>Marketplace</h1>
    {% for cat, prods in grouped.items() %}
    <div class="category">
        <div class="category-name">{{ cat }}</div>
        <div class="carousel">
            {% for prod in prods %}
            <div class="card" onclick="openModal('{{ prod.id }}')">
                <img src="{{ prod.image_url }}" alt="{{ prod.title }}">
                <div class="title">{{ prod.title }}</div>
                <div class="bio">{{ prod.bio[:100] }}{% if prod.bio|length > 100 %}...{% endif %}</div>
                <div class="price">${{ "%.2f" % prod.price }}</div>
                {% if prod.discount_percent > 0 %}
                <div class="badge discount">{{ prod.discount_percent }}% OFF</div>
                {% endif %}
                {% if prod.is_new %}
                <div class="badge new">NEW</div>
                {% endif %}
                {% if prod.is_trending %}
                <div class="badge trending">TRENDING</div>
                {% endif %}
                <a class="purchase" href="https://t.me/philoxnex?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title | urlencode }}">Purchase</a>
            </div>
            {% endfor %}
        </div>
        {% if not prods %}
        <div class="no-products">No products available yet.</div>
        {% endif %}
    </div>
    {% endfor %}
    <!-- Modals -->
    {% for prod in grouped.values() | flatten %}
    <div id="modal-{{ prod.id }}" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('{{ prod.id }}')">&times;</span>
            <h2>{{ prod.title }}</h2>
            <img src="{{ prod.image_url }}" style="width:100%;">
            <p>{{ prod.bio }}</p>
            <div class="price">${{ "%.2f" % prod.price }}</div>
            <a class="purchase" href="https://t.me/philoxnex?text=Hi%20Im%20interested%20to%20buy%20{{ prod.title | urlencode }}">Purchase</a>
        </div>
    </div>
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
    </script>
</body>
</html>
'''
