# Конфигурация для Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# Настройки Google Sheets
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ID вашей Google Sheets таблицы (извлеките из URL)
import streamlit as st

# Получаем ID из секретов Streamlit Cloud или используем по умолчанию
try:
    SPREADSHEET_ID = st.secrets["GOOGLE_SHEETS_ID"]
except:
    SPREADSHEET_ID = "10SrcUM8AAehI0rIV_c0szFW-9TWhbvb5iO0GecaahmY"  # Fallback ID

WORKSHEET_NAME = "Каталог"  # Название листа

def get_google_sheets_client():
    """Получение клиента Google Sheets"""
    try:
        # Создаем учетные данные из JSON файла
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", SCOPE
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        return None

def get_public_sheets_client():
    """Получение клиента для публичных таблиц"""
    try:
        # Для публичных таблиц используем gspread без авторизации
        import gspread
        return gspread
    except Exception as e:
        st.error(f"Ошибка подключения к публичной таблице: {e}")
        return None

def load_catalog_from_sheets():
    """Загрузка каталога из Google Sheets"""
    try:
        # Используем публичный доступ через URL
        import requests
        import csv
        from io import StringIO
        
        # URL для экспорта Google Sheets в CSV (публичный доступ)
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
        
        # Отладочная информация
        st.write(f"🔍 Пытаемся загрузить: {csv_url}")
        
        # Загружаем данные с заголовками
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(csv_url, headers=headers)
        response.raise_for_status()
        
        # Парсим CSV
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        # Отладочная информация
        rows = list(reader)
        st.write(f"📊 Загружено строк: {len(rows)}")
        if rows:
            st.write(f"📋 Колонки: {list(rows[0].keys())}")
            st.write(f"📋 Первая строка: {rows[0]}")
        
        catalog = {}
        for row in rows:
            # Проверяем разные возможные названия колонок
            name_key = None
            size_key = None
            
            for key in row.keys():
                if 'коннектор' in key.lower() or 'connector' in key.lower():
                    name_key = key
                if 'размер' in key.lower() or 'size' in key.lower() or 'мм' in key.lower():
                    size_key = key
            
            if name_key and size_key and row[name_key] and row[size_key]:
                try:
                    catalog[row[name_key]] = float(row[size_key])
                except ValueError:
                    continue
        
        st.write(f"✅ Успешно загружено коннекторов: {len(catalog)}")
        return catalog
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        st.write(f"🔍 Детали ошибки: {type(e).__name__}")
        return {}

def save_catalog_to_sheets(catalog):
    """Сохранение каталога в Google Sheets"""
    client = get_google_sheets_client()
    if not client:
        return False
    
    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        # Очищаем лист
        worksheet.clear()
        
        # Добавляем заголовки
        worksheet.append_row(['Вид коннектора', 'Размер (мм)'])
        
        # Добавляем данные
        for name, size in catalog.items():
            worksheet.append_row([name, size])
        
        return True
    except Exception as e:
        st.error(f"Ошибка сохранения данных: {e}")
        return False
