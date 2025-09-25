import streamlit as st
import csv
import os

# Импортируем функции для работы с Google Sheets
try:
    from google_sheets_config import load_catalog_from_sheets, save_catalog_to_sheets
    USE_GOOGLE_SHEETS = True
except ImportError:
    USE_GOOGLE_SHEETS = False

# Проверяем, работаем ли мы на Hugging Face Spaces
import os
IS_HUGGINGFACE_SPACE = os.getenv("SPACE_ID") is not None

CSV_FILE = "connectors.csv"

# ---------- Работа с данными ----------
def load_catalog():
    """Загружает каталог с приоритетом Google Sheets"""
    catalog = {}
    
    # Приоритет 1: Google Sheets (облако) - только если не на Hugging Face Spaces
    if USE_GOOGLE_SHEETS and not IS_HUGGINGFACE_SPACE:
        try:
            catalog = load_catalog_from_sheets()
            if catalog:  # Если получили данные из облака
                return catalog
        except:
            pass  # Если облако недоступно, переходим к локальному
    
    # Приоритет 2: CSV файл (локально)
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
    
    # Приоритет 3: Базовый набор (если ничего не загрузилось)
    if not catalog:
        catalog = {
            "SF9351-60004": 3.0,
            "16_MCX-50-2-104": 5.0,
            "16_SMA-50-2-103/111_NE": 3.0,
            "SMA-50-2-103": 2.5,
            "N-50-2-103": 4.0,
            "TNC-50-2-103": 3.5,
            "BNC-50-2-103": 2.8,
            "MCX-50-2-103": 3.2,
            "MMCX-50-2-103": 2.1,
            "U.FL-50-2-103": 1.8,
        }
    
    return catalog

def sync_catalogs():
    """Синхронизирует данные между Google Sheets и CSV"""
    if not USE_GOOGLE_SHEETS:
        return False
    
    try:
        # Загружаем данные из Google Sheets
        sheets_catalog = load_catalog_from_sheets()
        if not sheets_catalog:
            return False
        
        # Загружаем данные из CSV
        csv_catalog = {}
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        name, size = row
                        try:
                            csv_catalog[name] = float(size)
                        except ValueError:
                            continue
        
        # Объединяем: Google Sheets + уникальные из CSV
        merged_catalog = sheets_catalog.copy()
        for name, size in csv_catalog.items():
            if name not in merged_catalog:  # Добавляем только уникальные
                merged_catalog[name] = size
        
        # Сохраняем объединенный каталог в Google Sheets
        from google_sheets_config import save_catalog_to_sheets
        if save_catalog_to_sheets(merged_catalog):
            # Обновляем CSV файл
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for name, size in merged_catalog.items():
                    writer.writerow([name, size])
            return True
        
        return False
    except Exception as e:
        st.error(f"Ошибка синхронизации: {e}")
        return False

def update_catalog_files():
    """Обновляет файлы с актуальными данными каталога"""
    # Обновляем CSV файл
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for name, size in st.session_state.catalog.items():
                writer.writerow([name, size])
    except Exception as e:
        st.error(f"Ошибка обновления CSV: {e}")
    
    # Обновляем Google Sheets (если доступно)
    if USE_GOOGLE_SHEETS:
        try:
            from google_sheets_config import save_catalog_to_sheets
            save_catalog_to_sheets(st.session_state.catalog)
        except Exception as e:
            st.warning(f"Не удалось обновить Google Sheets: {e}")

# Функция сохранения больше не нужна - данные редактируются только в Google Sheets

# ---------- Интерфейс ----------
# Загружаем каталог только при первом запуске или принудительном обновлении
if "catalog" not in st.session_state or st.session_state.get("force_reload", False):
    st.session_state.catalog = load_catalog()
    st.session_state.force_reload = False

# Навигация по страницам
if "current_page" not in st.session_state:
    st.session_state.current_page = "Калькулятор"

# Боковая панель для навигации
with st.sidebar:
    st.title("📋 Навигация")
    
    if st.button("🧮 Калькулятор", use_container_width=True):
        st.session_state.current_page = "Калькулятор"
        st.rerun()
    
    if st.button("⚙️ Управление коннекторами", use_container_width=True):
        st.session_state.current_page = "Управление"
        st.rerun()
    
    st.divider()
    
    # Синхронизация
    st.subheader("🔄 Синхронизация")
    if st.button("🔄 Синхронизировать данные", use_container_width=True, type="secondary"):
        if sync_catalogs():
            st.success("✅ Данные синхронизированы!")
        else:
            st.warning("⚠️ Синхронизация недоступна")
        st.session_state.force_reload = True
        st.rerun()
    
    st.divider()
    
    # Мини-конвертер
    st.subheader("📏 Конвертер единиц")
    
    # Выбор типа конвертации
    conv_type = st.selectbox(
        "Тип конвертации:",
        ["Метры → Миллиметры", "Метры → Сантиметры", "Сантиметры → Миллиметры"],
        key="converter_type"
    )
    
    # Поле ввода
    if conv_type == "Метры → Миллиметры":
        input_value = st.number_input("Метры:", min_value=0.0, step=0.001, format="%.3f", key="meters_to_mm_input")
        result = input_value * 1000
        st.write(f"**{result:.1f} мм**")
    elif conv_type == "Метры → Сантиметры":
        input_value = st.number_input("Метры:", min_value=0.0, step=0.001, format="%.3f", key="meters_to_cm_input")
        result = input_value * 100
        st.write(f"**{result:.1f} см**")
    else:  # Сантиметры → Миллиметры
        input_value = st.number_input("Сантиметры:", min_value=0.0, step=0.1, format="%.1f", key="cm_to_mm_input")
        result = input_value * 10
        st.write(f"**{result:.1f} мм**")
    
    st.divider()
    
    # Информация
    st.subheader("📊 Информация")
    st.caption(f"Коннекторов: {len(st.session_state.catalog)}")
    
    # Информация о подключении (кэшируем статус)
    if "connection_status" not in st.session_state:
        if IS_HUGGINGFACE_SPACE:
            st.session_state.connection_status = "huggingface"
        elif USE_GOOGLE_SHEETS:
            try:
                test_catalog = load_catalog_from_sheets()
                if test_catalog:
                    st.session_state.connection_status = "connected"
                else:
                    st.session_state.connection_status = "unavailable"
            except:
                st.session_state.connection_status = "unavailable"
        else:
            st.session_state.connection_status = "local_only"
    
    # Показываем кэшированный статус
    if st.session_state.connection_status == "connected":
        st.success("☁️ Google Sheets подключен")
    elif st.session_state.connection_status == "unavailable":
        st.warning("⚠️ Google Sheets недоступен")
    elif st.session_state.connection_status == "huggingface":
        st.info("🤗 Hugging Face Spaces")
    else:
        st.info("💾 Только локальные данные")

# CSS стили для улучшения внешнего вида и мобильной адаптации
st.markdown("""
<style>
/* Основные стили для мобильных устройств */
@media (max-width: 768px) {
    /* Увеличиваем размеры элементов для мобильных */
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        border: 2px solid #444 !important;
        min-height: 44px !important; /* Минимальная высота для удобного нажатия */
    }
    
    .stSelectbox > div > div > div > div {
        color: #90EE90 !important;
        font-weight: 500 !important;
        font-size: 16px !important; /* Предотвращает зум на iOS */
    }
    
    /* Увеличиваем размеры кнопок */
    .stButton > button {
        min-height: 44px !important;
        font-size: 16px !important;
    }
    
    /* Улучшаем поля ввода */
    .stNumberInput > div > div > input {
        min-height: 44px !important;
        font-size: 16px !important;
    }
    
    /* Адаптируем боковую панель */
    .css-1d391kg {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Скрываем заголовок на мобильных для экономии места */
    .main > div {
        padding-top: 1rem !important;
    }
}

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

/* PWA стили */
@media (display-mode: standalone) {
    /* Стили для установленного PWA */
    .main > div {
        padding-top: env(safe-area-inset-top, 1rem) !important;
        padding-bottom: env(safe-area-inset-bottom, 1rem) !important;
    }
}

/* Улучшения для планшетов */
@media (min-width: 769px) and (max-width: 1024px) {
    .stSelectbox > div > div {
        min-height: 40px !important;
    }
    
    .stButton > button {
        min-height: 40px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Основной контент в зависимости от выбранной страницы
if st.session_state.current_page == "Калькулятор":
    # Страница калькулятора
    st.title("🧮 Калькулятор длины кабеля")
    st.caption(f"📊 Коннекторов в базе: {len(st.session_state.catalog)}")
    
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

elif st.session_state.current_page == "Управление":
    # Страница управления коннекторами
    st.title("⚙️ Управление коннекторами")
    
    # Кнопки управления
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ Добавить коннектор", type="primary", use_container_width=True):
            st.session_state.show_add_connector = True
            st.rerun()
    
    with col2:
        if st.button("📊 Показать все", use_container_width=True):
            st.session_state.show_all_connectors = not st.session_state.get("show_all_connectors", False)
            st.rerun()
    
    st.divider()
    
    # Форма добавления коннектора
    if st.session_state.get("show_add_connector", False):
        st.subheader("📝 Добавить новый коннектор")
        
        with st.form("add_connector_form"):
            new_name = st.text_input("Название коннектора", placeholder="Например: SMA-50-2-103")
            new_size = st.number_input("Размер (мм)", min_value=0.0, step=0.1, format="%.1f")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Добавить", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Отмена", use_container_width=True)
            
            if submit and new_name and new_size > 0:
                # Преобразуем название в верхний регистр
                new_name_upper = new_name.upper().strip()
                
                # Проверяем дубликаты в Google Sheets и CSV
                duplicate_found = False
                
                # Проверяем в Google Sheets
                if USE_GOOGLE_SHEETS:
                    try:
                        from google_sheets_config import load_catalog_from_sheets
                        sheets_catalog = load_catalog_from_sheets()
                        if sheets_catalog and new_name_upper in sheets_catalog:
                            st.error(f"❌ Коннектор '{new_name_upper}' уже существует в Google Sheets!")
                            duplicate_found = True
                    except:
                        pass
                
                # Проверяем в CSV файле
                if not duplicate_found and os.path.exists(CSV_FILE):
                    with open(CSV_FILE, newline="", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if len(row) == 2 and row[0] == new_name_upper:
                                st.error(f"❌ Коннектор '{new_name_upper}' уже существует в CSV файле!")
                                duplicate_found = True
                                break
                
                if not duplicate_found:
                    # Приоритет 1: Добавляем в Google Sheets
                    sheets_saved = False
                    if USE_GOOGLE_SHEETS:
                        try:
                            from google_sheets_config import save_catalog_to_sheets
                            # Загружаем текущий каталог и добавляем новый коннектор
                            current_catalog = load_catalog()
                            current_catalog[new_name_upper] = new_size
                            sheets_saved = save_catalog_to_sheets(current_catalog)
                        except Exception as e:
                            st.warning(f"Не удалось сохранить в Google Sheets: {e}")
                    
                    # Приоритет 2: Добавляем в CSV файл
                    csv_saved = False
                    try:
                        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow([new_name_upper, new_size])
                        csv_saved = True
                    except Exception as e:
                        st.warning(f"Не удалось сохранить в CSV: {e}")
                    
                    # Обновляем локальный каталог
                    st.session_state.catalog[new_name_upper] = new_size
                    
                    # Показываем результат
                    if sheets_saved and csv_saved:
                        st.success(f"✅ Коннектор '{new_name_upper}' добавлен в Google Sheets и CSV!")
                    elif sheets_saved:
                        st.success(f"✅ Коннектор '{new_name_upper}' добавлен в Google Sheets!")
                    elif csv_saved:
                        st.success(f"✅ Коннектор '{new_name_upper}' добавлен в CSV файл!")
                    else:
                        st.error("❌ Не удалось сохранить коннектор!")
                    
                    st.session_state.show_add_connector = False
                    st.session_state.force_reload = True
                    st.rerun()
            elif submit:
                st.error("❌ Пожалуйста, заполните все поля!")
            
            if cancel:
                st.session_state.show_add_connector = False
                st.rerun()
    
    # Показ всех коннекторов с возможностью редактирования и удаления
    if st.session_state.get("show_all_connectors", False):
        st.subheader("📋 Все коннекторы в базе")
        
        # Создаем DataFrame для красивого отображения
        import pandas as pd
        connectors_data = []
        for name, size in st.session_state.catalog.items():
            connectors_data.append({"Коннектор": name, "Размер (мм)": size})
        
        if connectors_data:
            df = pd.DataFrame(connectors_data)
            df = df.sort_values("Коннектор")  # Сортируем по алфавиту
            
            st.dataframe(df, use_container_width=True)
            
            # Статистика
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего коннекторов", len(df))
            with col2:
                st.metric("Средний размер", f"{df['Размер (мм)'].mean():.1f} мм")
            with col3:
                st.metric("Максимальный размер", f"{df['Размер (мм)'].max():.1f} мм")
            
            st.divider()
            
            # Управление коннекторами
            st.subheader("🔧 Редактирование коннекторов")
            
            # Выбор коннектора для редактирования
            selected_connector = st.selectbox(
                "Выберите коннектор для редактирования:",
                [""] + list(st.session_state.catalog.keys()),
                key="edit_connector"
            )
            
            if selected_connector:
                current_size = st.session_state.catalog[selected_connector]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✏️ Редактировать")
                    with st.form("edit_connector_form"):
                        new_name = st.text_input("Новое название", value=selected_connector)
                        new_size = st.number_input("Новый размер (мм)", value=current_size, min_value=0.0, step=0.1, format="%.1f")
                        
                        if st.form_submit_button("💾 Сохранить изменения", type="primary"):
                            if new_name.upper().strip() != selected_connector:
                                # Изменяем название
                                new_name_upper = new_name.upper().strip()
                                if new_name_upper in st.session_state.catalog and new_name_upper != selected_connector:
                                    st.error(f"❌ Коннектор '{new_name_upper}' уже существует!")
                                else:
                                    # Удаляем старый и добавляем новый
                                    del st.session_state.catalog[selected_connector]
                                    st.session_state.catalog[new_name_upper] = new_size
                                    
                                    # Обновляем файлы
                                    update_catalog_files()
                                    st.success(f"✅ Коннектор переименован в '{new_name_upper}'!")
                                    st.session_state.force_reload = True
                                    st.rerun()
                            else:
                                # Изменяем только размер
                                st.session_state.catalog[selected_connector] = new_size
                                update_catalog_files()
                                st.success(f"✅ Размер коннектора '{selected_connector}' обновлен!")
                                st.session_state.force_reload = True
                                st.rerun()
                
                with col2:
                    st.subheader("🗑️ Удалить")
                    st.warning(f"Вы собираетесь удалить коннектор '{selected_connector}'")
                    
                    if st.button("🗑️ Удалить коннектор", type="secondary"):
                        if selected_connector in st.session_state.catalog:
                            del st.session_state.catalog[selected_connector]
                            update_catalog_files()
                            st.success(f"✅ Коннектор '{selected_connector}' удален!")
                            st.session_state.force_reload = True
                            st.rerun()
        else:
            st.info("Коннекторы не найдены")
