import streamlit as st
from datetime import datetime
import os

# Установка переменных окружения из secrets
os.environ["OPINION_API_KEY"] = st.secrets.get("OPINION_API_KEY", "")
os.environ["PREDICT_API_KEY"] = st.secrets.get("PREDICT_API_KEY", "")

st.set_page_config(
    page_title="🔮 Prediction Markets Monitor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Автообновление каждые 10 секунд
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10000, key="data_refresh")

st.title("🔮 Prediction Markets Monitor")
st.caption(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")

# Импорт и запуск скриптов
try:
    from opinion_monitor import run as run_opinion
    opinion_data = run_opinion()
except Exception as e:
    opinion_data = {"error": str(e)}

try:
    from predict_monitor import run as run_predict
    predict_data = run_predict()
except Exception as e:
    predict_data = {"error": str(e)}

# Две независимые вкладки
tab1, tab2 = st.tabs([
    f"Opinion.Trade ({opinion_data.get('markets_count', 0)} рынков)",
    f"Predict.Fun ({predict_data.get('total_markets', 0)} рынков)"
])

with tab1:
    st.subheader("Opinion.Trade — сырые данные")
    st.json(opinion_data)

with tab2:
    st.subheader("Predict.Fun — сырые данные")
    st.json(predict_data)

# Статистика в сайдбаре
with st.sidebar:
    st.subheader("📊 Статистика")
    st.metric("Opinion.Trade", f"{opinion_data.get('markets_count', 0)} рынков")
    st.metric("Predict.Fun", f"{predict_data.get('total_markets', 0)} рынков")
    st.metric("Обновление", "Каждые 10 сек")
    
    st.divider()
    st.markdown("### Как искать вилки")
    st.markdown("""
    1. Открой обе вкладки
    2. Нажми `Ctrl+F` в браузере
    3. Ищи одинаковые события по `title` или `symbol`
    4. Сравни цены:
       - `bestAsk` / `bestBid`
       - `price`
    5. Разница > 2-3% = вилка 🎯
    """)
