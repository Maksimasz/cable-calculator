import streamlit as st
import csv
import os

# Импортируем функции для работы с Google Sheets
try:
    from google_sheets_config import load_catalog_from_sheets, save_catalog_to_sheets
    USE_GOOGLE_SHEETS = True
except ImportError:
    USE_GOOGLE_SHEETS = False

CSV_FILE = "connectors.csv"

# ---------- Работа с данными ----------
def load_catalog():
    catalog = {}
    
    # Сначала пробуем Google Sheets
    if USE_GOOGLE_SHEETS:
        try:
            catalog = load_catalog_from_sheets()
            if catalog:  # Если получили данные из Google Sheets
                return catalog
        except:
            pass  # Если ошибка, продолжаем к fallback
    
    # Fallback к CSV файлу
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    name, size = row
                    try:
                        catalog[name] = float(size)
                    except ValueError:
                        continue
    else:
        # Если нет CSV файла, используем базовый набор
        catalog = {
            "SF9351-60004": 3.0,
            "16_MCX-50-2-104": 5.0,
            "16_SMA-50-2-103/111_NE": 3.0,
        }
    return catalog

# Функция сохранения больше не нужна - данные редактируются только в Google Sheets

# ---------- Интерфейс ----------
# Всегда загружаем каталог заново для актуальных данных
st.session_state.catalog = load_catalog()

# CSS стили для улучшения внешнего вида выпадающих списков
st.markdown("""
<style>
/* Стили для выпадающих списков */
.stSelectbox > div > div {
    background-color: #262730 !important;
}

/* Цвет текста в выпадающем списке (опции) */
.stSelectbox > div > div > div > div {
    color: #90EE90 !important; /* светло-зеленый */
}

/* Цвет текста выбранного элемента остается обычным */
.stSelectbox > div > div > div > div[data-baseweb="select"] {
    color: #fafafa !important; /* обычный белый */
}

/* Улучшение контрастности для мобильных */
@media (max-width: 768px) {
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        border: 1px solid #444 !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #90EE90 !important;
        font-weight: 500 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Индикатор подключения и заголовок
if USE_GOOGLE_SHEETS:
    # Проверяем, действительно ли подключение работает
    try:
        test_catalog = load_catalog_from_sheets()
        if test_catalog:
            st.title("✅ Калькулятор длины кабеля")
            st.caption(f"📊 В базе данных: {len(test_catalog)} коннекторов")
        else:
            st.title("❌ Калькулятор длины кабеля")
            st.caption("📊 База данных недоступна - пустой каталог")
            st.error("Каталог пустой или не загружается")
    except Exception as e:
        st.title("❌ Калькулятор длины кабеля")
        st.caption("📊 База данных недоступна")
        st.error(f"Ошибка подключения: {str(e)}")
        # Показываем детали ошибки для отладки
        st.write("🔍 Детали ошибки:", str(e))
else:
    st.title("❌ Калькулятор длины кабеля")
    st.caption(f"📊 В локальной базе: {len(st.session_state.catalog)} коннекторов")
    st.warning("Google Sheets модуль не найден")

st.divider()

# Основной калькулятор
conn1 = st.selectbox("1 Коннектор", list(st.session_state.catalog.keys()), key="conn1")
conn2 = st.selectbox("2 Коннектор", list(st.session_state.catalog.keys()), key="conn2")
cable_len = st.number_input("Длина кабеля (мм)", min_value=0.0, step=1.0)

# Переключатель типа толеранса
tol_type = st.radio("Тип толеранса", ["мм", "%"], horizontal=True, key="tol_type")

# Поле ввода толеранса в зависимости от выбранного типа
if tol_type == "мм":
    tol_value = st.number_input("Толеранц (мм)", value=0.0, step=0.1, key="tol_mm")
    tol_mm = tol_value
else:
    tol_percent = st.number_input("Толеранц (%)", value=0.0, step=0.1, key="tol_percent")
    # Конвертируем % в мм (от длины кабеля)
    tol_mm = (tol_percent / 100) * cable_len

size1 = st.session_state.catalog[conn1]
size2 = st.session_state.catalog[conn2]
final_len = cable_len - (size1 + size2) + tol_mm

st.write("Размер коннектора 1:", size1, "мм")
st.write("Размер коннектора 2:", size2, "мм")

# Показываем текущий толеранс
if tol_type == "мм":
    st.write("Толеранс:", tol_mm, "мм")
else:
    st.write("Толеранс:", tol_percent, "% (", f"{tol_mm:.2f}", "мм)")

st.subheader(f"Окончательная длина кабеля: {final_len:.2f} мм")
