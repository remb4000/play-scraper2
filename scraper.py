# -*- coding: utf-8 -*-
from google_play_scraper import search, app
import pandas as pd
import time
import random
import os
import re

print("🚀 Запуск обновленного парсера (RU/BY, 2026 год, <50k установок, Рейтинг 4.0+)...")

# 🌍 1. Страны - Россия, Беларусь
COUNTRIES = ["ru", "by"]

# 🛑 2. Обновленный черный список
BLACKLIST = ["hypercasual", "slots", "clicker", "merge", "idle"]
FILENAME = "Leads.xlsx"

if not os.path.exists("keywords.txt"):
    print("❌ Создай файл 'keywords.txt' и добавь туда запросы.")
    exit()

with open("keywords.txt", "r", encoding="utf-8") as file:
    base_queries = [line.strip() for line in file if line.strip()]

if not base_queries:
    print("❌ Файл 'keywords.txt' пуст.")
    exit()

# ASO-мультипликатор для глубокого поиска
modifiers = ["", " 2026", " 3d", " a", " b", " simulator", " pro"]
deep_queries = []
for q in base_queries:
    for mod in modifiers:
        deep_queries.append(q + mod)

print(f"📁 Базовых запросов: {len(base_queries)}. С учетом ASO-мультипликатора: {len(deep_queries)}.")

scraped_data = []
added_games = set()

def parse_installs(installs_str):
    try:
        # Регулярное выражение \D удаляет ВСЕ символы, кроме цифр (пробелы, плюсы, буквы, запятые)
        clean_str = re.sub(r'\D', '', str(installs_str))
        return int(clean_str) if clean_str else 0
    except Exception:
        return 0

# 🔥 Исправленная функция сохранения
def save_to_excel():
    # Если данные есть - сохраняем их. Если нет - создаем пустую таблицу с заголовками.
    if scraped_data:
        df = pd.DataFrame(scraped_data)
    else:
        df = pd.DataFrame(columns=["Title", "Developer", "Email", "Website", "Installs", "Price", "Genre", "Rating", "Reviews", "Released", "Region", "URL"])
    
    df.to_excel(FILENAME, index=False, engine='openpyxl')

# Главный цикл
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

                # --- 1. Фильтр: 2026 год ---
                released = details.get("released", "")
                if not released or "2026" not in str(released):
                    print(f"Не 2026 год ❌")
                    continue

                # --- 2. Фильтр: ДО 50к установок ---
                installs = details.get("installs", "0")
                installs_num = parse_installs(installs)
                if installs_num > 50000:
                    print(f"Крупная ({installs}) ❌")
                    continue

                # --- 3. Фильтр: Качество (Рейтинг >= 4.0 и Отзывы >= 500) ---
                rating = details.get("score", 0) or 0
                reviews = details.get("ratings", 0) or 0
                if rating < 4.0 or reviews < 500:
                    print(f"Не прошла по качеству ({round(rating, 1)}⭐, {reviews} отз.) ❌")
                    continue

                # --- 4. Фильтр: Черный список ---
                title_lower = title.lower()
                summary_lower = details.get("summary", "").lower()
                if any(word in title_lower or word in summary_lower for word in BLACKLIST):
                    print("В черном списке ❌")
                    continue

                # --- 5. Сбор расширенных данных ---
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
                
                # 🔥 Вызываем сохранение после каждой добавленной игры
                save_to_excel()
                print("✅ ДОБАВЛЕНО И СОХРАНЕНО!")

                time.sleep(random.uniform(1.0, 2.0))

            except Exception:
                print("Ошибка страницы ❌")
                pass 

# 🔥 Финальное сохранение, чтобы файл сгенерировался даже если игр 0
save_to_excel()
print(f"\n✅ Готово! Найдено крутых проектов: {len(scraped_data)}. Файл: {FILENAME}")
