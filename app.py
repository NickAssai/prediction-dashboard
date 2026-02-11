import streamlit as st
import pandas as pd
import time
from datetime import datetime
from api_client import fetch_opinion_markets, fetch_predict_markets, compute_complement

st.set_page_config(
    page_title="📊 Prediction Markets Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🔮 Prediction Markets Monitor")
with col2:
    last_update = st.empty()

OPINION_KEY = st.secrets.get("OPINION_API_KEY", "")
PREDICT_KEY = st.secrets.get("PREDICT_API_KEY", "")

@st.cache_data(ttl=30)
def load_data():
    start = time.time()
    
    with st.spinner("📡 Загружаем данные с бирж..."):
        opinion = fetch_opinion_markets(OPINION_KEY) if OPINION_KEY else []
        predict = fetch_predict_markets(PREDICT_KEY) if PREDICT_KEY else []
    
    elapsed = time.time() - start
    return opinion, predict, elapsed

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 30:
    st.cache_data.clear()
    st.session_state.last_refresh = time.time()
    st.rerun()

opinion_data, predict_data, load_time = load_data()
last_update.caption(f"⏱️ Обновлено: {datetime.now().strftime('%H:%M:%S')} (загрузка: {load_time:.1f} сек)")

tab1, tab2 = st.tabs(["Opinion.Trade", "Predict.Fun"])

with tab1:
    if opinion_data:
        df = pd.DataFrame(opinion_data)
        if not df.empty and "title" in df.columns:
            cols_to_show = [c for c in ["title", "symbol", "volume24h", "price"] if c in df.columns]
            df = df[cols_to_show].copy()
            df.columns = ["Рынок", "Символ", "Объём 24ч", "Цена"]
            df["Объём 24ч"] = pd.to_numeric(df["Объём 24ч"], errors="coerce").round(2)
            df = df.sort_values("Объём 24ч", ascending=False).reset_index(drop=True)
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("Данные получены, но нет колонок для отображения")
    else:
        st.warning("Нет данных Opinion.Trade — проверь API ключ в Secrets")

with tab2:
    if predict_data:
        processed = []
        for m in predict_data[:50]:
            dp = m.get("decimalPrecision", 2)
            yes_bid = m.get("bestBid", None)
            yes_ask = m.get("bestAsk", None)
            
            processed.append({
                "Рынок": m.get("title", "")[:40],
                "Символ": m.get("symbol", ""),
                "Объём 24ч": round(m.get("volume24h", 0), 2),
                "Yes Buy": yes_ask,
                "Yes Sell": yes_bid,
                "No Buy": compute_complement(yes_bid, dp) if yes_bid else None,
                "No Sell": compute_complement(yes_ask, dp) if yes_ask else None,
            })
        
        df = pd.DataFrame(processed)
        st.dataframe(df, use_container_width=True, height=500)
    else:
        st.warning("Нет данных Predict.Fun — проверь API ключ в Secrets")

with st.sidebar:
    st.subheader("📈 Статистика")
    st.metric("Opinion.Trade рынков", len(opinion_data))
    st.metric("Predict.Fun рынков", len(predict_data))
    st.metric("Загрузка данных", f"{load_time:.1f} сек")
    
    st.divider()
    st.subheader("⚙️ Управление")
    if st.button("🔄 Обновить сейчас"):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("Автообновление: каждые 30 сек")
    st.caption("Автообновление: каждые 30 сек")
