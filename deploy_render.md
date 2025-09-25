# 🎨 Развертывание на Render

## Преимущества:
- ✅ **Бесплатный тариф** с ограничениями
- ✅ **Автоматическое развертывание**
- ✅ **Поддержка Docker**
- ✅ **SSL и CDN включены**

## Шаги:

### 1. Создайте аккаунт
- https://render.com/
- Войдите через GitHub

### 2. Создайте Web Service
- "New" → "Web Service"
- Подключите GitHub репозиторий

### 3. Настройки:
```yaml
Name: cable-calculator
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### 4. Переменные окружения:
```bash
PORT=8501
```

## Результат:
`https://cable-calculator.onrender.com`
