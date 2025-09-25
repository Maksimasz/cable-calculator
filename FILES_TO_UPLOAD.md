# 📁 Файлы для загрузки на Hugging Face Spaces

## ✅ Обязательные файлы:

### Основное приложение:
- `app.py` - главный файл Streamlit приложения
- `requirements.txt` - зависимости Python
- `README.md` - описание Space (с метаданными для HF)

### База данных:
- `connectors.csv` - каталог коннекторов

## 📱 PWA файлы (для мобильного приложения):

### Манифест и Service Worker:
- `manifest.json` - манифест PWA
- `sw.js` - service worker для офлайн работы
- `index.html` - HTML страница

### Иконки:
- `icon-192.png` - иконка 192x192 пикселей
- `icon-512.png` - иконка 512x512 пикселей

## ❌ НЕ загружайте:

- `google_sheets_config.py` - не нужен на HF Spaces
- `secrets.toml` - не нужен на HF Spaces
- `__pycache__/` - папка с кэшем Python
- `*.md` файлы кроме `README.md` - документация

## 📋 Итого для загрузки (9 файлов):
1. app.py
2. requirements.txt
3. README.md
4. connectors.csv
5. manifest.json
6. sw.js
7. index.html
8. icon-192.png
9. icon-512.png

---

**После загрузки этих файлов ваше приложение будет полностью функциональным! 🚀**
