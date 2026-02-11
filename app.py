import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="🔮 Arbitrage Monitor", layout="wide")
st.title("🔮 Prediction Markets — Полные данные для арбитража")

os.environ["OPINION_API_KEY"] = st.secrets.get("OPINION_API_KEY", "")
os.environ["PREDICT_API_KEY"] = st.secrets.get("PREDICT_API_KEY", "")

if st.button("🚀 ЗАПУСТИТЬ ПОЛНУЮ ЗАГРУЗКУ (45–75 сек)", type="primary", use_container_width=True):
    st.session_state.loading = True
    st.cache_data.clear()

if st.session_state.get("loading"):
    with st.spinner("⏳ Загрузка Opinion.Trade... (45–75 сек)"):
        try:
            from opinion_monitor import run as run_opinion
            st.session_state.opinion_data = run_opinion()
        except Exception as e:
            st.session_state.opinion_data = {"error": str(e)}
    
    with st.spinner("⏳ Загрузка Predict.Fun... (45–75 сек)"):
        try:
            from predict_monitor import run as run_predict
            st.session_state.predict_data = run_predict()
        except Exception as e:
            st.session_state.predict_data = {"error": str(e)}
    
    st.session_state.loading = False
    st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Opinion.Trade")
    if "opinion_data" in st.session_state:
        data = st.session_state.opinion_data
        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.success(f"✅ {data.get('markets_count', 0)} рынков | {data.get('tokens_count', 0)} токенов")
            st.json(data)
    else:
        st.info("Нажмите кнопку выше для загрузки")

with col2:
    st.subheader("📊 Predict.Fun")
    if "predict_data" in st.session_state:
        data = st.session_state.predict_data
        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.success(f"✅ {data.get('total_markets', 0)} рынков")
            st.json(data)
    else:
        st.info("Нажмите кнопку выше для загрузки")

st.sidebar.subheader("🎯 Как искать вилки")
st.sidebar.markdown("""
1. Нажми **«ЗАПУСТИТЬ ПОЛНУЮ ЗАГРУЗКУ»**
2. Подожди 45–75 сек (полная загрузка всех токенов)
3. Нажми `Ctrl+F` в браузере:
   - Ищи события по `title` или `symbol`
   - Сравни `bestAsk` / `bestBid` между платформами
4. Разница > 2–3% = арбитраж 🚀
""")
