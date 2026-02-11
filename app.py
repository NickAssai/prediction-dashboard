import streamlit as st
import os
from datetime import datetime

st.set_page_config(page_title="Prediction Markets", layout="wide")

st.title("Prediction Markets Monitor")

os.environ["OPINION_API_KEY"] = st.secrets.get("OPINION_API_KEY", "")
os.environ["PREDICT_API_KEY"] = st.secrets.get("PREDICT_API_KEY", "")

if st.button("Load Full Market Data", type="primary", use_container_width=True):
    st.session_state.loading = True
    st.cache_data.clear()

if st.session_state.get("loading"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opinion.Trade")
        with st.spinner("Loading..."):
            try:
                from opinion_monitor import run as run_opinion
                st.session_state.opinion_data = run_opinion()
            except Exception as e:
                st.session_state.opinion_data = {"error": str(e)}
    
    with col2:
        st.subheader("Predict.Fun")
        with st.spinner("Loading..."):
            try:
                from predict_monitor import run as run_predict
                st.session_state.predict_data = run_predict()
            except Exception as e:
                st.session_state.predict_data = {"error": str(e)}
    
    st.session_state.loading = False
    st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Opinion.Trade")
    if "opinion_data" in st.session_state:
        data = st.session_state.opinion_data
        if "error" in data:
            st.error(f"Error: {data['error']}")
        else:
            st.metric("Markets", data.get('markets_count', 0))
            st.metric("Tokens", data.get('tokens_count', 0))
            st.json(data)
    else:
        st.info("Press button above to load data")

with col2:
    st.subheader("Predict.Fun")
    if "predict_data" in st.session_state:
        data = st.session_state.predict_data
        if "error" in data:
            st.error(f"Error: {data['error']}")
        else:
            st.metric("Markets", data.get('total_markets', 0))
            st.json(data)
    else:
        st.info("Press button above to load data")

with st.sidebar:
    st.subheader("Status")
    if st.session_state.get("loading"):
        st.info("Loading...")
    elif "opinion_data" in st.session_state and "predict_data" in st.session_state:
        st.success("Loaded")
        st.metric("Opinion.Trade", f"{st.session_state.opinion_data.get('markets_count', 0)}")
        st.metric("Predict.Fun", f"{st.session_state.predict_data.get('total_markets', 0)}")
        st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.caption("No data")
    
    st.divider()
    st.subheader("Arbitrage Guide")
    st.markdown("""
    1. Press **Load Full Market Data**
    2. Wait 45–75 seconds
    3. Use **Ctrl+F** to find events:
       - Search `title` or `symbol`
       - Compare `bestAsk` / `bestBid`
    4. Difference > 2–3% = opportunity
    """)
