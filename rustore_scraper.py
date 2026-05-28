# -*- coding: utf-8 -*-
import requests
import pandas as pd
import time
import random
import os
import re
import datetime # 
print("🚀 Запуск СУПЕР-АВТОНОМНОГО парсера RuStore (2026 год, <50k установок, Ротация слов)...")

BLACKLIST = ["slots"]
FILENAME = "RuStore_Leads.xlsx"

# 🧠 ГИГАНТСКИЙ БАНК КЛЮЧЕВЫХ СЛОВ (Топ-130+ популярных запросов СНГ)
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
    "рпг", "rpg", "ролевая", "магия", "драконы", "подземелья", "аниме","майн" , "майнкрафт" , "обби" , "обби паркур" , "обби лава " , "роблокс" , 
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
# Добавляем ASO-модификаторы
modifiers = ["", " 2026", " 3d", " a", " b", " simulator", " pro" , " online" , " free" , " онлайн" , " симулятор" , " бесплатно"]
deep_queries = [q + mod for q in base_queries for mod in modifiers]

print(f"\n📁 Создано {len(deep_queries)} глубоких запросов для RuStore API.")

scraped_data = []
added_games = set()

# Заголовки, чтобы RuStore не блокировал запросы (притворяемся обычным браузером)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
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
    
    # 1. Запрашиваем список игр по ключевому слову
    search_url = f"https://backapi.rustore.ru/applicationData/search?query={query}&limit=20&offset=0"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        search_data = response.json()
        apps = search_data.get('body', {}).get('applications', [])
        time.sleep(random.uniform(1.0, 2.0)) # Пауза анти-бана
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        continue

    if not apps:
        continue

    for index, app_item in enumerate(apps):
        package_name = app_item.get('packageName')
        if not package_name:
            continue

        # 2. Получаем детальную информацию о каждой игре по ее package_name
        details_url = f"https://backapi.rustore.ru/applicationData/overallInfo/{package_name}"
        try:
            res_details = requests.get(details_url, headers=HEADERS, timeout=10)
            details = res_details.json().get('body', {})
            
            title = details.get('appName', 'Unknown')
            title_for_log = title[:20] + "..."
            print(f"   ⏳ [{index+1}/{len(apps)}] {title_for_log.ljust(23)} ->", end=" ")

            if title in added_games:
                print("Уже в базе ❌")
                continue

            # Фильтр: Количество скачиваний (RuStore отдает точное число)
            installs = details.get('downloads', 0)
            if installs > 50000:
                print(f"Крупная ({installs}) ❌")
                continue

            # Фильтр: Рейтинг и Отзывы
            rating = details.get('rating', 0) or 0
            reviews = details.get('reviewCount', 0) or 0
            if rating < 4.0 or reviews < 100: # Для RuStore планку отзывов лучше снизить до 100
                print(f"Слабая ({round(rating, 1)}⭐, {reviews} отз.) ❌")
                continue

            # Фильтр: Год релиза или последнего обновления
            # RuStore часто отдает firstPublishDate или versionDate в формате "2026-05-12T10:00:00Z"
            release_date = details.get('firstPublishDate', '')
            if "2026" not in str(release_date):
                print(f"Не 2026 год ❌")
                continue

            # Фильтр: Черный список в названии и описании
            description = details.get('shortDescription', '').lower()
            if any(word in title.lower() or word in description for word in BLACKLIST):
                print("В черном списке ❌")
                continue

            # УСПЕХ! Собираем лид
            developer_name = details.get('companyName', '')
            email = details.get('ownerEmail', '')
            website = details.get('ownerSite', '')
            
            # Если разработчик не указал почту в спец. поле, часто она есть в описании
            if not email:
                emails_in_desc = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", description)
                if emails_in_desc:
                    email = emails_in_desc[0]

            game_info = {
                "Title": title,
                "Developer": developer_name,
                "Email": email,
                "Website": website,
                "Installs": installs,
                "Rating": round(rating, 2),
                "Reviews": reviews,
                "Released": str(release_date)[:10], # Оставляем только дату (YYYY-MM-DD)
                "URL": f"https://apps.rustore.ru/app/{package_name}"
            }

            scraped_data.append(game_info)
            added_games.add(title)
            
            save_to_excel()
            print("✅ ДОБАВЛЕНО И СОХРАНЕНО!")

            time.sleep(random.uniform(0.5, 1.5))

        except Exception:
            print("Ошибка страницы ❌")
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
                'caption': f'🟢 [RuStore] Парсинг завершен!\n🎲 Использованы новые случайные слова.\n✅ Найдено лидов: {len(scraped_data)}'
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
