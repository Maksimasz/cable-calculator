# 🤗 Развертывание на Hugging Face Spaces

## Преимущества:
- ✅ **Полностью бесплатно**
- ✅ **Автоматическое обновление** из GitHub
- ✅ **Быстрое развертывание** (2-3 минуты)
- ✅ **Поддержка PWA**
- ✅ **SSL сертификат** включен

## Шаги развертывания:

### 1. Создайте аккаунт на Hugging Face
- Перейдите на https://huggingface.co/
- Зарегистрируйтесь или войдите

### 2. Создайте Space
- Нажмите "Create new Space"
- Выберите **Streamlit** SDK
- Название: `cable-calculator` (или любое другое)
- Видимость: **Public** (для бесплатного хостинга)

### 3. Загрузите файлы
Скопируйте эти файлы в ваш Space:
- `app.py`
- `requirements.txt`
- `manifest.json`
- `sw.js`
- `icon-192.png`
- `icon-512.png`
- `index.html`

### 4. Структура файлов в Space:
```
cable-calculator/
├── app.py
├── requirements.txt
├── README.md
├── manifest.json
├── sw.js
├── icon-192.png
├── icon-512.png
└── index.html
```

### 5. README.md для Space:
```markdown
---
title: Калькулятор длины кабеля
emoji: 🔌
colorFrom: red
colorTo: yellow
sdk: streamlit
sdk_version: 1.49.1
app_file: app.py
pinned: false
license: mit
---

# 🔌 Калькулятор длины кабеля

PWA приложение для расчета длины кабеля с учетом размеров коннекторов.
```

## Результат:
После развертывания ваше приложение будет доступно по адресу:
`https://huggingface.co/spaces/YOUR_USERNAME/cable-calculator`
