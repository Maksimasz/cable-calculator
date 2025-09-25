# Упрощенная конфигурация для Google Sheets (только чтение публичных таблиц)
import streamlit as st
import requests
import csv
from io import StringIO

# ID вашей Google Sheets таблицы
SPREADSHEET_ID = "10SrcUM8AAehI0rIV_c0szFW-9TWhbvb5iO0GecaahmY"

def load_catalog_from_sheets():
    """Загрузка каталога из публичной Google Sheets таблицы"""
    try:
        # URL для экспорта Google Sheets в CSV (публичный доступ)
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
        
        # Загружаем данные с заголовками
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(csv_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Исправляем кодировку
        response.encoding = 'utf-8'
        
        # Парсим CSV
        csv_data = StringIO(response.text)
        reader = csv.DictReader(csv_data)
        
        rows = list(reader)
        catalog = {}
        for row in rows:
            # Проверяем разные возможные названия колонок
            name_key = None
            size_key = None
            
            for key in row.keys():
                # Ищем колонку с названием коннектора (более гибкий поиск)
                if any(word in key.lower() for word in ['коннектор', 'connector', 'вид', 'type']):
                    name_key = key
                # Ищем колонку с размером (более гибкий поиск)
                if any(word in key.lower() for word in ['размер', 'size', 'мм', 'mm']):
                    size_key = key
            
            if name_key and size_key and row[name_key] and row[size_key]:
                try:
                    catalog[row[name_key]] = float(row[size_key])
                except ValueError:
                    continue
        return catalog
    except Exception as e:
        # Более детальная информация об ошибке
        error_msg = f"Ошибка загрузки данных: {e}"
        if "403" in str(e):
            error_msg += " (Таблица не публичная или доступ запрещен)"
        elif "404" in str(e):
            error_msg += " (Таблица не найдена)"
        elif "timeout" in str(e).lower():
            error_msg += " (Таймаут подключения)"
        st.error(error_msg)
        return {}

def save_catalog_to_sheets(catalog):
    """Сохранение каталога в Google Sheets (только для локального использования)"""
    st.info("Сохранение в Google Sheets доступно только при локальном запуске с авторизацией")
    return False
