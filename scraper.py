# -*- coding: utf-8 -*-
from google_play_scraper import search, app
import pandas as pd
import time
import random
import os
import re
import requests

print("🚀 Запуск СУПЕР-АВТОНОМНОГО парсера (RU/BY/KZ, 2026 год, Ротация ключевых слов)...")

# 🌍 1. Страны - Россия, Беларусь, Казахстан
COUNTRIES = ["ru", "by", "kz"]

# 🛑 2. Черный список жанров
BLACKLIST = ["slots"]
FILENAME = "Leads.xlsx"

# 🧠 3. ГИГАНТСКИЙ БАНК КЛЮЧЕВЫХ СЛОВ (из всех блоков, что мы обсуждали)
KEYWORD_POOL = [
    # Автомобильные / Физика
    "шашки по городу", "оперская езда", "суета на дорогах", "краш тест", 
    "разрушение машин", "парковка", "автошкола", "дальнобойщики", 
    "внедорожники", "уличные гонки", "drag racing", "car crash", "дрифт", 
    "jdm", "тюнинг", "физика", "автосимулятор", "реалистичная игра",
    # Мидкор / Сленг / Механики
    "рогалик", "выживач", "квест", "хоррор", "лутер", "гача", 
    "защита башни", "ферма", "визуальная новелла", "метроидвания", 
    "соулслайк", "тактика", "roguelike", "tower defense", "open world", 
    "crafting", "pve", "tactical", "puzzle game", "story driven", "base building",
    # Визуал / Стиль
    "лоу поли", "low poly", "ragdoll", "мультяшная графика", "вид сверху", 
    "изометрия", "атмосферная", "открытый мир", "текстовая", "свобода действий",
    "пиксельная", "инди игра", "сюжетная", "песочница", "sandbox", "premium", "rpg",
    # Классические широкие жанры
    "симулятор", "стратегия", "ролевая игра", "экшен", "выживание", 
    "головоломка", "гонки", "шутер", "платформер", "настольная игра",
    # Сеттинги
    "киберпанк", "зомби апокалипсис", "космос", "постапокалипсис", 
    "фэнтези", "магия", "средневековье", "детектив"
]

# 🎰 МАГИЯ РОТАЦИИ: Каждый день скрипт выбирает 10 СЛУЧАЙНЫХ слов из банка выше
base_queries = random.sample(KEYWORD_POOL, 10)

print(f"🎲 Сегодня кубик Рубика выбрал следующие 10 базовых слов для поиска:")
for word in base_queries:
    print(f"  • {word}")

# ASO-мультипликатор для глубокого поиска (из 10 слов делает 70 запросов)
modifiers = ["", " 2026", " 3d", " a", " b", " simulator", " pro"]
deep_queries = []
for q in base_queries:
    for mod in modifiers:
        deep_queries.append(q + mod)

print(f"\n📁 С учетом ASO-мультипликатора создано: {len(deep_queries)} глубоких запросов.")

scraped_data = []
added_games = set()

def parse_installs(installs_str):
    try:
        clean_str = re.sub(r'\D', '', str(installs_str))
        return int(clean_str) if clean_str else 0
    except Exception:
        return 0

def save_to_excel():
    if scraped_data:
        df = pd.DataFrame(scraped_data)
    else:
        df = pd.DataFrame(columns=["Title", "Developer", "Email", "Website", "Installs", "Price", "Genre", "Rating", "Reviews", "Released", "Region", "URL"])
    df.to_excel(FILENAME, index=False, engine='openpyxl')

# Главный цикл парсинга
for country in COUNTRIES:
    print(f"\n🌍 === Регион: {country.upper()} ===")
    
    for query in deep_queries:
        print(f"\n📡 Запрос: '{query}' ...")

        try:
            results = search(query, lang="ru", country=country, n_hits=30)
            time.sleep(random.uniform(2.5, 4.0)) 
        except Exception as e:
            print(f"❌ Ошибка соединения (пауза 15 сек): {e}")
            time.sleep(15)
            continue

        if not results:
            continue

        for index, r in enumerate(results):
            title_for_log = r.get('title', 'Unknown')[:20] + "..."
            print(f"   ⏳ [{index+1}/{len(results)}] {title_for_log.ljust(23)} ->", end=" ")

            try:
                details = app(r["appId"], lang="ru", country=country)
                title = details.get("title", "")

                if title in added_games:
                    print("Уже в базе ❌")
                    continue

                released = details.get("released", "")
                if not released or "2026" not in str(released):
                    print(f"Не 2026 год ❌")
                    continue

                installs = details.get("installs", "0")
                installs_num = parse_installs(installs)
                if installs_num > 50000:
                    print(f"Крупная ({installs}) ❌")
                    continue

                rating = details.get("score", 0) or 0
                reviews = details.get("ratings", 0) or 0
                if rating < 4.0 or reviews < 500:
                    print(f"Не прошла по качеству ({round(rating, 1)}⭐, {reviews} отз.) ❌")
                    continue

                title_lower = title.lower()
                summary_lower = details.get("summary", "").lower()
                if any(word in title_lower or word in summary_lower for word in BLACKLIST):
                    print("В черном списке ❌")
                    continue

                price_val = details.get("price", 0)
                price_str = "Free" if price_val == 0 else f"${price_val}"

                game_info = {
                    "Title": title,
                    "Developer": details.get("developer", ""),
                    "Email": details.get("developerEmail", ""),
                    "Website": details.get("developerWebsite", ""),
                    "Installs": installs,
                    "Price": price_str,
                    "Genre": details.get("genre", "Unknown"),
                    "Rating": round(rating, 2),
                    "Reviews": reviews,
                    "Released": released,
                    "Region": country.upper(),
                    "URL": details.get("url", "")
                }

                scraped_data.append(game_info)
                added_games.add(title)
                
                save_to_excel()
                print("✅ ДОБАВЛЕНО И СОХРАНЕНО!")

                time.sleep(random.uniform(1.0, 2.0))

            except Exception:
                print("Ошибка страницы ❌")
                pass 

save_to_excel()
print(f"\n✅ Готово! Найдено крутых проектов: {len(scraped_data)}. Файл: {FILENAME}")

# === ОТПРАВКА В TELEGRAM ===
print("\n📤 Отправка файла в Telegram...")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        with open(FILENAME, 'rb') as f:
            files = {'document': f}
            data = {
                'chat_id': TELEGRAM_CHAT_ID, 
                'caption': f'🤖 Ежедневный отчет сформирован!\n🎲 Использованы новые случайные ключевые слова.\n✅ Найдено проектов: {len(scraped_data)}'
            }
            response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("✅ Файл успешно отправлен в Telegram!")
        else:
            print(f"❌ Ошибка отправки в Telegram. Код: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при отправке файла: {e}")
else:
    print("⚠️ Токен бота или Chat ID не найдены в GitHub Secrets.")
