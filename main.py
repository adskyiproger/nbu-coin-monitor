#!/usr/bin/env python3

import json
import os
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


CATALOG_URL = "https://coins.bank.gov.ua/catalog.html"
STATE_FILE = os.environ.get("STATE_FILE", "data/seen_products.json")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_IDS = [
    chat_id.strip()
    for chat_id in os.environ.get("TELEGRAM_CHAT_IDS", "").split(",")
    if chat_id.strip()
]

if not CHAT_IDS:
    raise RuntimeError("TELEGRAM_CHAT_IDS is not set")


def send_telegram_product(product, chat_id):
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    data = {
        "chat_id": chat_id,
        "photo": product["image"],
        "caption": f"{product['title']}\n{product['url']}",
    }

    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()
    

def load_seen_products():
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen_products(products):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def fetch_catalog():
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; coins-monitor/1.0)"
    }

    response = requests.get(CATALOG_URL, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")

    products = {}

    # шукаємо тільки блоки з картинками товарів
    for link in soup.find_all("a", class_="p_img_href"):
        href = link.get("href")
        img = link.find("img")
        
        if not href or not img:
            continue

        image = img.get("data-hover") or img.get("data-src") or img.get("src")
        title = img.get("alt", "").strip()
        
        if not image:
            continue

        url = urljoin(CATALOG_URL, href)

        products[url] = {
            "title": title,
            "url": url,
            "image": image,
        }

    return products


def main():
    seen_products = load_seen_products()

    html = fetch_catalog()
    current_products = parse_products(html)

    new_products = {
        url: product
        for url, product in current_products.items()
        if url not in seen_products
    }

    if not new_products:
        print("Нових товарів немає.")
    else:
        print(f"Знайдено нових товарів: {len(new_products)}\n")

        for product in new_products.values():
            # print(f"- {product['title']}")
            # print(f"  {product['url']}")
            # print(f"  {product['image']}")
            for chat_id in CHAT_IDS:
                send_telegram_product(product=product, chat_id=chat_id)
                time.sleep(10)
    # Оновлюємо локальну базу після перевірки
    save_seen_products(current_products)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Помилка: {e}", file=sys.stderr)
        sys.exit(1)