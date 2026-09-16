#!/usr/bin/env python3

import json
import os
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


CATALOG_URL = "https://coins.bank.gov.ua/catalog.html"
STATE_FILE = os.environ.get("STATE_FILE", "data/seen_products.json")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))

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
    os.makedirs(os.path.dirname(STATE_FILE) or ".", exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def fetch_catalog():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux armv7l) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            ),
            locale="uk-UA",
        )

        page = context.new_page()

        try:
            print(f"Відкриваю {CATALOG_URL}...")

            response = page.goto(
                CATALOG_URL,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            if response is None:
                raise RuntimeError("No response received from catalog")

            print(f"HTTP status: {response.status}")

            if response.status >= 400:
                raise RuntimeError(
                    f"Catalog returned HTTP {response.status}"
                )

            # Give BunnyCDN/browser challenge time to complete.
            page.wait_for_timeout(5_000)

            # Wait until product blocks appear.
            page.wait_for_selector(
                "a.p_img_href",
                timeout=30_000,
            )

            return page.content()

        finally:
            browser.close()


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")

    products = {}

    # шукаємо тільки блоки з картинками товарів
    for link in soup.find_all("a", class_="p_img_href"):
        href = link.get("href")
        img = link.find("img")

        if not href or not img:
            continue

        image = (
            img.get("data-hover")
            or img.get("data-src")
            or img.get("src")
        )

        title = img.get("alt", "").strip()

        if not image:
            continue

        url = urljoin(CATALOG_URL, href)
        image = urljoin(CATALOG_URL, image)

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

    print(f"Знайдено товарів у каталозі: {len(current_products)}")

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
            print(f"- {product['title']}")
            print(f"  {product['url']}")
            print(f"  {product['image']}")

            for chat_id in CHAT_IDS:
                send_telegram_product(
                    product=product,
                    chat_id=chat_id,
                )
                time.sleep(10)

    # Оновлюємо локальну базу після перевірки
    save_seen_products(current_products)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Помилка: {e}", file=sys.stderr)

        print(f"Наступна перевірка через {CHECK_INTERVAL} сек.")
        time.sleep(CHECK_INTERVAL)