# 🪙 NBU Coins Monitor

Скрипт для відстеження нових товарів на сайті https://coins.bank.gov.ua/
👉 [https://coins.bank.gov.ua/](https://coins.bank.gov.ua/)

При появі нових позицій — надсилає повідомлення в Telegram з:

* 📸 картинкою
* 📝 назвою
* 🔗 посиланням

---

## 🚀 Можливості

* Відстеження нових товарів
* Збереження стану (щоб не дублювати повідомлення)
* Підтримка кількох Telegram чатів
* Простий запуск через cron

---

## 📦 Встановлення

```bash
pip install requests beautifulsoup4
```

---

## ⚙️ Налаштування

### 1. Створити Telegram бота

Через Telegram:

* знайти `@BotFather`
* створити бота
* отримати `BOT_TOKEN`

---

### 2. Дізнатись chat_id

Можна через:

```
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

---

### 3. Задати змінні середовища

```bash
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_IDS="123456789,987654321"
```

---

# ▶️ Запуск локально

```bash
python3 coins_monitor.py
```

---

## 🔁 Автоматичний запуск (cron)

Перевірка кожні 5 хвилин:

```bash
*/5 * * * * /usr/bin/python3 /path/to/coins_monitor.py >> /path/to/log.log 2>&1
```
---

## 🐳 Запуск через Docker Compose

### 1. Клонуй репозиторій на сервер

```bash
git clone git@github.com:adskyiproger/nbu-coin-monitor.git
```

---

### 2. Створити `.env`

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=123456789,987654321
CHECK_INTERVAL=300
```

---

### 3. Запуск

```bash
docker compose up -d --build
```

---

### 4. Перевірка логів

```bash
docker compose logs -f
```

---

### 5. Зупинка

```bash
docker compose down
```

---

## ⚙️ Як це працює

* Контейнер запускає скрипт у циклі
* Інтервал задається через `CHECK_INTERVAL` (в секундах)
* Дані про вже оброблені товари зберігаються в `./data`
* При перезапуску контейнера стан не втрачається

---

## 🔧 Корисні команди

### Перезапуск

```bash
docker compose restart
```

### Перебілд після змін

```bash
docker compose up -d --build
```

### Видалити все (включаючи дані ⚠️)

```bash
docker compose down -v
```

---

## ⚠️ Важливо

* Переконайся, що бот у Telegram має доступ до чату
* Якщо не приходять повідомлення — перевір `.env`
* Не став дуже малий `CHECK_INTERVAL` (рекомендовано ≥ 60 сек)

---

## 📁 Як це працює

Скрипт:

1. Завантажує HTML каталогу
2. Парсить товари (назва, посилання, картинка)
3. Порівнює з попереднім станом (`seen_products.json`)
4. Відправляє нові товари в Telegram
5. Оновлює локальний файл стану

---

## 🧾 Формат даних

```json
{
  "https://coins.bank.gov.ua/...": {
    "title": "Назва товару",
    "url": "https://...",
    "image": "https://..."
  }
}
```

---

## ⚠️ Обмеження

* Скрипт використовує HTML парсинг (немає офіційного API)
* Зміна структури сайту може зламати парсер
* Telegram має rate limits (затримка між повідомленнями)

---

## 💡 Ідеї для покращення

* 📦 Batch відправка (альбоми)
* 🔔 Фільтрація по ключових словах
* 🧠 Визначення змін статусу товару
* 🐳 Docker контейнер
* ☁️ Деплой як сервіс

---

## 🛠️ Troubleshooting

### Немає повідомлень

* перевірити `TELEGRAM_BOT_TOKEN`
* перевірити `CHAT_ID`
* чи писали боту хоча б 1 раз

### Помилка Telegram API

* перевірити доступність картинки
* перевірити правильність URL

---
