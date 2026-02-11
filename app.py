import streamlit as st
import os
from datetime import datetime

st.set_page_config(
    page_title="🔮 Prediction Markets Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔮 Prediction Markets Monitor")
st.caption("Полные данные для арбитража | Обновление по кнопке")

# Загрузка ключей из секретов
os.environ["OPINION_API_KEY"] = st.secrets.get("OPINION_API_KEY", "")
os.environ["PREDICT_API_KEY"] = st.secrets.get("PREDICT_API_KEY", "")

# Кнопка обновления
if st.button("🔄 ЗАПУСТИТЬ ПОЛНУЮ ЗАГРУЗКУ ДАННЫХ", type="primary", use_container_width=True):
    st.session_state.loading = True
    st.cache_data.clear()

# Если нажата кнопка — запускаем загрузку
if st.session_state.get("loading"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Opinion.Trade")
        progress_opinion = st.empty()
        status_opinion = st.empty()
        
        try:
            progress_opinion.progress(0)
            status_opinion.info("Запуск скрипта...")
            
            from opinion_monitor import run as run_opinion
            
            def callback_opinion(msg):
                progress_opinion.progress(50)  # Просто индикатор что работает
                status_opinion.info(f"Opinion.Trade: {msg}")
            
            with st.spinner("Загрузка данных Opinion.Trade (45–75 сек)..."):
                opinion_data = run_opinion(callback_opinion)
            
            progress_opinion.progress(100)
            status_opinion.success(f"✅ Загружено: {opinion_data.get('markets_count', 0)} рынков, {opinion_data.get('tokens_count', 0)} токенов")
            st.session_state.opinion_data = opinion_data
            
        except Exception as e:
            status_opinion.error(f"❌ Ошибка: {str(e)}")
            st.session_state.opinion_data = {"error": str(e)}
    
    with col2:
        st.subheader("📊 Predict.Fun")
        progress_predict = st.empty()
        status_predict = st.empty()
        
        try:
            progress_predict.progress(0)
            status_predict.info("Запуск скрипта...")
            
            from predict_monitor import run as run_predict
            
            def callback_predict(msg):
                progress_predict.progress(50)  # Просто индикатор что работает
                status_predict.info(f"Predict.Fun: {msg}")
            
            with st.spinner("Загрузка данных Predict.Fun (45–75 сек)..."):
                predict_data = run_predict(callback_predict)
            
            progress_predict.progress(100)
            status_predict.success(f"✅ Загружено: {predict_data.get('total_markets', 0)} рынков")
            st.session_state.predict_data = predict_data
            
        except Exception as e:
            status_predict.error(f"❌ Ошибка: {str(e)}")
            st.session_state.predict_data = {"error": str(e)}
    
    st.session_state.loading = False
    st.rerun()

# Отображение результатов (если уже загружены)
if "opinion_data" in st.session_state or "predict_data" in st.session_state:
    tab1, tab2 = st.tabs([
        f"Opinion.Trade ({st.session_state.get('opinion_data', {}).get('markets_count', 0)} рынков)",
        f"Predict.Fun ({st.session_state.get('predict_data', {}).get('total_markets', 0)} рынков)"
    ])
    
    with tab1:
        if "opinion_data" in st.session_state:
            st.subheader("Opinion.Trade — полные данные")
            st.json(st.session_state.opinion_data)
        else:
            st.info("Нажмите кнопку выше для загрузки данных")
    
    with tab2:
        if "predict_data" in st.session_state:
            st.subheader("Predict.Fun — полные данные")
            st.json(st.session_state.predict_data)
        else:
            st.info("Нажмите кнопку выше для загрузки данных")

# Статистика в сайдбаре
with st.sidebar:
    st.subheader("📊 Статус")
    
    if st.session_state.get("loading"):
        st.warning("⏳ Идёт загрузка данных...")
    elif "opinion_data" in st.session_state and "predict_data" in st.session_state:
        st.success("✅ Данные загружены")
        st.metric("Opinion.Trade", f"{st.session_state.opinion_data.get('markets_count', 0)} рынков")
        st.metric("Predict.Fun", f"{st.session_state.predict_data.get('total_markets', 0)} рынков")
        st.metric("Время", datetime.now().strftime("%H:%M:%S"))
    else:
        st.info("⏳ Ожидание загрузки")
    
    st.divider()
    st.markdown("### Как искать вилки")
    st.markdown("""
    1. Нажми **«ЗАПУСТИТЬ ПОЛНУЮ ЗАГРУЗКУ»**
    2. Подожди 45–75 сек (идёт загрузка всех токенов)
    3. Открой обе вкладки
    4. Нажми `Ctrl+F` → ищи события по `title` или `symbol`
    5. Сравни цены:
       - `bestAsk` / `bestBid`
       - `price`
    6. Разница > 2–3% = вилка 🎯
    """)
