# -*- coding: utf-8 -*-
import requests
import pandas as pd
import time
import random
import os
import re
import datetime
import json  # 🔥 Новая библиотека для глубокого сканирования

print("🚀 Запуск СУПЕР-АВТОНОМНОГО парсера RuStore (2026 год, Умный сканер дат, <100k установок)...")

BLACKLIST = ["slots"]
FILENAME = "RuStore_Leads.xlsx"

# 🧠 ГИГАНТСКИЙ БАНК КЛЮЧЕВЫХ СЛОВ (Топ-130+ популярных запросов СНГ)
KEYWORD_POOL = [
    # 🚗 Топ-запросы
    "гонки", "шашки по городу", "оперская", "опер стайл", "суета", "русские тачки",
    "ваз", "лада", "нива", "уаз", "бпан", "краш тест", "разрушение", "дрифт",
    "дрифтинг", "jdm", "тюнинг", "парковка 3d", "симулятор вождения", "автошкола",
    "дальнобойщики", "камаз", "грузовики", "бездорожье", "4x4", "оффроуд", "автосимулятор",

    # 🔫 Экшен, Шутеры, Выживание
    "стрелялки", "шутер", "снайпер", "спецназ", "война", "оружие", "танки",
    "битва", "онлайн шутер", "королевская битва", "выживание", "выживач", "зомби",
    "сталкер", "постапокалипсис", "чернобыль", "мафия", "бандиты", "гта", "fps",

    # 🧩 Казуальные, Головоломки, Аркады
    "головоломка", "три в ряд", "шарики", "кроссворд", "слова из слов",
    "найди отличия", "поиск предметов", "логика", "судоку", "раскраска",
    "антистресс", "поп ит", "прятки", "платформер", "аркада",

    # 🏰 РПГ, Стратегии, Мидкор
    "рпг", "rpg", "ролевая", "магия", "драконы", "подземелья", "аниме", "майн", "майнкрафт", "обби", "обби паркур", "обби лава", "роблокс", 
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

current_day = datetime.date.today().toordinal() 
start_index = (current_day * WORDS_PER_DAY) % total_words
base_queries = [KEYWORD_POOL[(start_index + i) % total_words] for i in range(WORDS_PER_DAY)]

print(f"📅 Алгоритм очереди: сегодня берем слова с {start_index + 1} по {(start_index + WORDS_PER_DAY)} из {total_words}:")
for word in base_queries:
    print(f"  • {word}")
    
modifiers = ["", " 2026", " 3d", " a", " b", " simulator", " pro", " online", " free", " онлайн", " симулятор", " бесплатно"]
deep_queries = [q + mod for q in base_queries for mod in modifiers]

print(f"\n📁 Создано {len(deep_queries)} глубоких запросов для RuStore API.")

scraped_data = []
added_games = set()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://apps.rustore.ru",
    "Referer": "https://apps.rustore.ru/",
    "Connection": "keep-alive"
}

def save_to_excel():
    if scraped_data:
        df = pd.DataFrame(scraped_data)
    else:
        df = pd.DataFrame(columns=["Title", "Developer", "Email", "Website", "Installs", "Rating", "Reviews", "Released", "URL"])
    df.to_excel(FILENAME, index=False, engine='openpyxl')

# ==========================================
# ГЛАВНЫЙ ЦИКЛ ПАРСИНГА ЧЕРЕЗ API RUSTORE
# ==========================================
for query in deep_queries:
    print(f"\n📡 Ищем: '{query}' ...")
    
    search_url = "https://backapi.rustore.ru/applicationData/apps"
    search_params = {
        "query": query,
        "pageSize": 50,  # Оставляем глубину 50 для максимального охвата
        "pageNumber": 0
    }
    
    try:
        response = requests.get(search_url, params=search_params, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Сервер RuStore заблокировал запрос (Код {response.status_code}). Ждем 5 сек...")
            time.sleep(5)
            continue
            
        search_data = response.json()
        apps = search_data.get('body', {}).get('content', [])
        time.sleep(random.uniform(1.0, 2.0)) 
    except Exception as e:
        print(f"❌ Ошибка соединения при поиске: {e}")
        continue

    if not apps:
        continue

    for index, app_item in enumerate(apps):
        package_name = app_item.get('packageName')
        if not package_name:
            continue

        details_url = f"https://backapi.rustore.ru/applicationData/overallInfo/{package_name}"
        try:
            res_details = requests.get(details_url, headers=HEADERS, timeout=10)
            
            if res_details.status_code != 200:
                continue
                
            details = res_details.json().get('body', {})
            
            title = details.get('appName', 'Unknown')
            title_for_log = title[:20] + "..."
            print(f"   ⏳ [{index+1}/{len(apps)}] {title_for_log.ljust(23)} ->", end=" ")

            if title in added_games:
                print("Уже в базе ❌")
                continue

            installs = details.get('downloads', 0)
            if installs > 100000:
                print(f"Крупная ({installs}) ❌")
                continue

            # Парсинг рейтинга
            try:
                raw_rating = details.get('rating', 0)
                rating = float(raw_rating) if not isinstance(raw_rating, dict) else float(raw_rating.get('rating', raw_rating.get('average', 0)))
            except Exception:
                rating = 0.0

            try:
                raw_reviews = details.get('reviewCount', 0)
                reviews = int(raw_reviews) if not isinstance(raw_reviews, dict) else int(raw_reviews.get('count', 0))
            except Exception:
                reviews = 0

            # 🔥 БРОНЕБОЙНЫЙ ПОИСК ДАТЫ (Ищет везде, на любой глубине JSON)
            details_str = json.dumps(details)
            game_year = "Unknown"
            release_date_for_excel = "2026"
            
            # 1. Сначала ищем дату в явном текстовом виде ("YYYY-MM-DD")
            full_string_dates = re.findall(r'"((202\d)-\d{2}-\d{2})', details_str)
            if full_string_dates:
                years_found = [match[1] for match in full_string_dates]
                if "2026" in years_found:
                    game_year = "2026"
                    # Вытаскиваем точную дату для отчета
                    for match in full_string_dates:
                        if match[1] == "2026":
                            release_date_for_excel = match[0]
                            break
                else:
                    game_year = years_found[0]
            
            # 2. Если текста нет, ищем системное время RuStore (13-значные миллисекунды)
            if game_year == "Unknown":
                timestamps = re.findall(r'\b(1[67]\d{11})\b', details_str)
                for ts in timestamps:
                    try:
                        date_obj = datetime.datetime.fromtimestamp(int(ts) / 1000)
                        year = date_obj.year
                        if year == 2026:
                            game_year = "2026"
                            release_date_for_excel = date_obj.strftime('%Y-%m-%d')
                            break
                        elif 2020 <= year <= 2030:
                            game_year = str(year)
                    except:
                        pass

            # Финальная блокировка
            if game_year != "2026":
                print(f"Не 2026 год ({game_year}) ❌")
                continue

          # Проверка черного списка
            description = details.get('shortDescription', '').lower()
            if any(word in title.lower() or word in description for word in BLACKLIST):
                print("В черном списке ❌")
                continue

            developer_name = details.get('companyName', '')
            website = details.get('ownerSite', '')
            
            # 1. Пробуем стандартные ключи API
            email = details.get('ownerEmail', '') or details.get('supportEmail', '')
            
            # 2. Если поля пустые, сканируем ВЕСЬ ответ сервера (включая полное описание)
            if not email:
                all_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", details_str)
                # Фильтруем случайные совпадения (например, файлы картинок)
                valid_emails = [e for e in all_emails if not e.endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                
                if valid_emails:
                    email = valid_emails[0] # Берем первую найденную настоящую почту

            game_info = {
                "Title": title,
                "Developer": developer_name,
                "Email": email,
                "Website": website,
                "Installs": installs,
                "Rating": round(rating, 2),
                "Reviews": reviews,
                "Released": release_date_for_excel,
                "URL": f"https://apps.rustore.ru/app/{package_name}"
            }

            scraped_data.append(game_info)
            added_games.add(title)
            
            save_to_excel()
            print("✅ ДОБАВЛЕНО И СОХРАНЕНО!")

            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f"Ошибка страницы ❌ (Причина: {e})")
            pass

save_to_excel()
print(f"\n✅ Готово! Найдено крутых проектов в RuStore: {len(scraped_data)}. Файл: {FILENAME}")

# ==========================================
# ОТПРАВКА В TELEGRAM
# ==========================================
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
                'caption': f'🟢 [RuStore] Парсинг завершен!\n📅 Год: 2026 (Глубокий сканер).\n✅ Найдено лидов: {len(scraped_data)}'
            }
            response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("✅ Файл успешно отправлен в Telegram!")
        else:
            print(f"❌ Ошибка отправки. Код: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
else:
    print("⚠️ Токен бота или Chat ID не найдены.")
