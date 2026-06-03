import XLSX from 'xlsx';

const FETCH_USER_APPS_ENDPOINT = 'https://backapi.rustore.ru/applicationData/retrieveUserApps?pagination=false';

// 🔐 НАСТРОЙКИ (Вставь свой токен из браузера)
const AUTH_TOKEN = process.env.RUSTORE_TOKEN || 'ТВОЙ_RUSTORE_TOKEN_ИЗ_БРАУЗЕРА';

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 1️⃣ Получаем список твоих игр из консоли
const getMyApps = async () => {
    try {
        const response = await fetch(FETCH_USER_APPS_ENDPOINT, {
            headers: { 'Content-Type': 'application/json', 'Authorization': AUTH_TOKEN },
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.body.content || [];
    } catch (error) {
        console.error('❌ Ошибка получения списка игр:', error.message);
        return [];
    }
};

// 2️⃣ Вытаскиваем дату релиза/обновления из публичного API
const getAppReleaseDate = async (packageName) => {
    try {
        const url = `https://backapi.rustore.ru/applicationData/overallInfo/${packageName}`;
        const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }});
        
        if (!response.ok) return 'Нет данных';
        
        const data = await response.json();
        const body = data.body || {};

        // RuStore хранит даты в разных полях. Ищем самое старое (firstPublishDate) или текущее
        const rawDate = body.firstPublishDate || body.publishDate || body.updateDate;

        if (rawDate) {
            // Если сервер вернул дату в виде 13-значных миллисекунд
            if (typeof rawDate === 'number' || !isNaN(Number(rawDate))) {
                return new Date(Number(rawDate)).toLocaleDateString('ru-RU');
            }
            // Если дата пришла текстом
            return new Date(rawDate).toLocaleDateString('ru-RU');
        }

        // Бронебойный скан: ищем системный timestamp 
        const jsonStr = JSON.stringify(body);
        const match = jsonStr.match(/\b(1[67]\d{11})\b/);
        if (match) {
            return new Date(Number(match[1])).toLocaleDateString('ru-RU');
        }

        return 'Дата не найдена';
    } catch (e) {
        return 'Ошибка сервера';
    }
};

// 🚀 ГЛАВНЫЙ ЗАПУСК
const runDatesReport = async () => {
    console.log('🔄 Собираем список твоих игр...');
    const apps = await getMyApps();
    
    if (apps.length === 0) {
        console.log('❌ Игры не найдены. Проверь токен авторизации!');
        return;
    }

    console.log(`✅ Найдено игр: ${apps.length}. Начинаем сбор дат...`);

    // Шапка для Excel
    const worksheetData = [
        ['Название игры', 'Package Name', 'Статус', 'Дата публикации']
    ];

    for (const app of apps) {
        const safeAppName = app.appName.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const status = app.appStatus === 'PUBLISHED' ? 'Опубликовано' : app.appStatus;
        
        process.stdout.write(`⏳ Проверяем: ${safeAppName.substring(0, 20)}... `);
        
        // Получаем дату
        const releaseDate = await getAppReleaseDate(app.packageName);
        console.log(`[${releaseDate}]`);

        worksheetData.push([
            safeAppName, 
            app.packageName, 
            status, 
            releaseDate
        ]);
        
        // Пауза, чтобы сервер не выдал 429 ошибку
        await delay(1000); 
    }

    // 💾 Сохраняем в Excel ЛОКАЛЬНО
    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
    const workbook = XLSX.utils.book_new();
    
    // Настраиваем ширину колонок для красоты
    worksheet['!cols'] = [{ wch: 40 }, { wch: 30 }, { wch: 15 }, { wch: 20 }];
    
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Мои Игры');

    const fileName = 'My_Games_Release_Dates.xlsx';
    XLSX.writeFile(workbook, fileName);
    console.log(`\n✅ Готово! Файл '${fileName}' успешно сохранен в текущей папке.`);
};

runDatesReport();
