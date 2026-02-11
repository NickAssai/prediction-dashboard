import streamlit as st
from api_client import fetch_opinion_raw, fetch_predict_raw
from datetime import datetime

st.set_page_config(page_title="🔍 Raw API Data", layout="wide")
st.title("🔮 Сырые данные с бирж (без обработки)")

OPINION_KEY = st.secrets.get("OPINION_API_KEY", "")
PREDICT_KEY = st.secrets.get("PREDICT_API_KEY", "")

if st.button("🔄 Обновить данные"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=300)
def get_raw_data():
    opinion = fetch_opinion_raw(OPINION_KEY) if OPINION_KEY else {"error": "No OPINION_API_KEY"}
    predict = fetch_predict_raw(PREDICT_KEY) if PREDICT_KEY else {"error": "No PREDICT_API_KEY"}
    return opinion, predict

opinion_raw, predict_raw = get_raw_data()

st.caption(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Opinion.Trade (сырой ответ)")
    st.json(opinion_raw)

with col2:
    st.subheader("Predict.Fun (сырой ответ)")
    st.json(predict_raw)

st.sidebar.markdown("### Как использовать")
st.sidebar.markdown("""
1. Нажми **«Обновить данные»**
2. В колонках — полные JSON ответы от API
3. Ищи поля:
   - `price`, `bestBid`, `bestAsk` — цены
   - `symbol`, `title` — идентификаторы событий
4. Сравнивай цены на одинаковые события между платформами
""")
