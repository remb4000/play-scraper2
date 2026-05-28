# -*- coding: utf-8 -*-
from google_play_scraper import search, app
import pandas as pd
import time
import random
import os
import re
import requests
import datetime # 

print("🚀 Запуск СУПЕР-АВТОНОМНОГО парсера (RU/BY/KZ, 2026 год, Ротация ключевых слов)...")

# 🌍 1. Страны - Россия, Беларусь, Казахстан
COUNTRIES = ["ru", "by", "kz"]

# 🛑 2. Черный список жанров
BLACKLIST = ["slots"]
FILENAME = "Leads.xlsx"

# 🧠 3. ГИГАНТСКИЙ БАНК КЛЮЧЕВЫХ СЛОВ (из всех блоков, что мы обсуждали)
KEYWORD_POOL = [
  # 🚗 Топ-запросы (Машины, симуляторы вождения, суета)
    "гонки", "шашки по городу", "оперская", "опер стайл", "суета", "русские тачки",
    "ваз", "лада", "нива", "уаз", "бпан", "краш тест", "разрушение", "дрифт",
    "дрифтинг", "jdm", "тюнинг", "парковка 3d", "симулятор вождения", "автошкола",
    "дальнобойщики", "камаз", "грузовики", "бездорожье", "4x4", "оффроуд", "автосимулятор",

    # 🔫 Экшен, Шутеры, Выживание (Очень высокий трафик)
    "стрелялки", "шутер", "снайпер", "спецназ", "война", "оружие", "танки",
    "битва", "онлайн шутер", "королевская битва", "выживание", "выживач", "зомби",
    "сталкер", "постапокалипсис", "чернобыль", "мафия", "бандиты", "гта", "fps",

    # 🧩 Казуальные, Головоломки, Аркады
    "головоломка", "три в ряд", "шарики", "кроссворд", "слова из слов",
    "найди отличия", "поиск предметов", "логика", "судоку", "раскраска",
    "антистресс", "поп ит", "прятки", "платформер", "аркада",

    # 🏰 РПГ, Стратегии, Мидкор
    "рпг", "rpg", "ролевая", "магия", "драконы", "подземелья", "аниме", "майн" , "майнкрафт" , "обби" , "обби паркур" , "обби лава " , "роблокс" , 
    "открытый мир", "стратегия", "защита башни", "tower defense", "ферма",
    "магнат", "бизнес", "тактика", "рогалик", "гача", "метроидвания",

    # 🏗️ Симуляторы жизни, профессий и песочницы
    "симулятор", "симулятор жизни", "симулятор бомжа", "строительство",
    "крафт", "крафтинг", "песочница", "sandbox", "кубики", "майн",
    "обби", "паркур", "поезда", "метро", "самолеты", "рыбалка", "охота",

    # 👻 Хорроры, Квесты и Сюжетные
    "хоррор", "страшилки", "квест", "побег", "побег из тюрьмы", "детектив",
    "сюжетная", "новелла", "визуальная новелла", "текстовый квест",

    # 🎲 Настольные, Карточные и Спорт
    "дурак", "покер", "шахматы", "нарды", "мафия игра", "монополия",
    "футбол", "бильярд", "бокс", "драки", "файтинг",

    # 🎨 Стилистика и Инди
    "инди игра", "лоу поли", "ragdoll", "мультяшная", "пиксельная",
    "киберпанк", "космос", "фэнтези", "средневековье"
]

# 📅 УМНАЯ ОЧЕРЕДЬ: Берем слова строго по порядку каждый день
WORDS_PER_DAY = 10
total_words = len(KEYWORD_POOL)

# Получаем уникальный непрерывный номер сегодняшнего дня
current_day = datetime.date.today().toordinal() 

# Вычисляем индекс, с которого стартуем сегодня
start_index = (current_day * WORDS_PER_DAY) % total_words

# Собираем слова, плавно переходя в начало списка, если дошли до конца
base_queries = [KEYWORD_POOL[(start_index + i) % total_words] for i in range(WORDS_PER_DAY)]

print(f"📅 Алгоритм очереди: сегодня берем слова с {start_index + 1} по {(start_index + WORDS_PER_DAY)} из {total_words}:")
for word in base_queries:
    print(f"  • {word}")

# ASO-мультипликатор для глубокого поиска (из 10 слов делает 70 запросов)
modifiers = ["", " 2026", " 3d", " a", " b", " simulator", " pro" , " online" , " free" , " онлайн" , " симулятор" , " бесплатно" ]
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
