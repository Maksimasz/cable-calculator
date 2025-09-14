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
SPREADSHEET_ID = "10SrcUM8AAehI0rIV_c0szFW-9TWhbvb5iO0GecaahmY"  # Ваш ID
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
        
        # URL для экспорта Google Sheets в CSV
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
        
        # Загружаем данные
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Парсим CSV
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        catalog = {}
        for row in reader:
            if 'Вид коннектора' in row and 'Размер (мм)' in row:
                name = row['Вид коннектора']
                size = row['Размер (мм)']
                if name and size:
                    try:
                        catalog[name] = float(size)
                    except ValueError:
                        continue
        
        return catalog
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
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
