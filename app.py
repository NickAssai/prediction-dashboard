import streamlit as st
import pandas as pd
import json
from datetime import datetime
from api_client import fetch_opinion_markets, fetch_predict_markets, compute_complement

st.set_page_config(
    page_title="📊 Prediction Markets Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔮 Prediction Markets Monitor")
st.caption(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")

OPINION_KEY = st.secrets.get("OPINION_API_KEY", "")
PREDICT_KEY = st.secrets.get("PREDICT_API_KEY", "")

@st.cache_data(ttl=30)
def load_data():
    opinion = fetch_opinion_markets(OPINION_KEY) if OPINION_KEY else []
    predict = fetch_predict_markets(PREDICT_KEY) if PREDICT_KEY else []
    return opinion, predict

opinion_data, predict_data = load_data()

tab1, tab2, tab3 = st.tabs(["Opinion.Trade", "Predict.Fun", "Отладка (сырые данные)"])

# ============ Opinion.Trade ============
with tab1:
    if not opinion_
        st.warning("Нет данных от Opinion.Trade — проверь API ключ")
    else:
        st.metric("Рынков", len(opinion_data))
        
        # Извлекаем ключевые поля (адаптировано под реальную структуру)
        rows = []
        for m in opinion_data:
            rows.append({
                "Название": m.get("title", m.get("name", "—")),
                "Символ": m.get("symbol", "—"),
                "Объём 24ч": round(float(m.get("volume24h", 0)), 2),
                "Цена": round(float(m.get("price", m.get("currentPrice", 0))), 4),
                "Статус": m.get("status", "—"),
            })
        
        df = pd.DataFrame(rows)
        df = df.sort_values("Объём 24ч", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, height=500)

# ============ Predict.Fun ============
with tab2:
    if not predict_
        st.warning("Нет данных от Predict.Fun — проверь API ключ")
    else:
        st.metric("Рынков", len(predict_data))
        
        rows = []
        for m in predict_data:
            dp = m.get("decimalPrecision", 2)
            yes_bid = m.get("bestBid")
            yes_ask = m.get("bestAsk")
            
            rows.append({
                "Название": m.get("title", "—")[:50],
                "Символ": m.get("symbol", "—"),
                "Объём 24ч": round(float(m.get("volume24h", 0)), 2),
                "Yes Buy": round(yes_ask, dp) if yes_ask else None,
                "Yes Sell": round(yes_bid, dp) if yes_bid else None,
                "No Buy": round(compute_complement(yes_bid, dp), dp) if yes_bid else None,
                "No Sell": round(compute_complement(yes_ask, dp), dp) if yes_ask else None,
            })
        
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, height=500)

# ============ Отладка ============
with tab3:
    st.subheader("Opinion.Trade — первые 2 рынка (сырой JSON)")
    if opinion_
        st.json(opinion_data[:2])
    else:
        st.code(json.dumps({"error": "Нет данных"}, indent=2), language="json")
    
    st.divider()
    st.subheader("Predict.Fun — первый рынок (сырой JSON)")
    if predict_
        st.json(predict_data[0] if predict_data else {})
    else:
        st.code(json.dumps({"error": "Нет данных"}, indent=2), language="json")
    
    st.divider()
    st.caption("💡 Совет: посмотри структуру выше и скажи, какие поля важны — адаптирую таблицу под твои нужды")

# ============ Сайдбар ============
with st.sidebar:
    st.subheader("📈 Статистика")
    st.metric("Opinion.Trade", len(opinion_data))
    st.metric("Predict.Fun", len(predict_data))
    
    st.divider()
    if st.button("🔄 Обновить данные"):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("Автообновление: каждые 30 сек")
