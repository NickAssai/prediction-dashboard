import streamlit as st
import os
from datetime import datetime

# Custom CSS — Apple-style minimalism
st.markdown("""
<style>
    /* Основной фон */
    .stApp {
        background-color: #f5f5f7;
    }
    
    /* Заголовок */
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        font-size: 28px;
        letter-spacing: -0.01em;
        color: #1d1d1f;
        margin-bottom: 24px;
    }
    
    /* Подзаголовки колонок */
    .stColumn h3 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        font-size: 16px;
        letter-spacing: -0.005em;
        color: #86868b;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    /* Кнопка */
    .stButton button {
        background-color: #000000;
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 14px 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        font-size: 15px;
        letter-spacing: -0.005em;
        width: 100%;
        height: auto;
        box-shadow: none;
        transition: all 0.15s ease;
    }
    
    .stButton button:hover {
        background-color: #2c2c2e;
        transform: scale(1.01);
    }
    
    .stButton button:active {
        background-color: #000000;
        transform: scale(0.99);
    }
    
    /* Спиннер и статусы */
    .stSpinner {
        color: #000000;
    }
    
    .stSuccess {
        background-color: #f0fff4;
        color: #2e7d32;
        border: none;
        padding: 12px 16px;
        border-radius: 8px;
    }
    
    .stError {
        background-color: #fff0f0;
        color: #c62828;
        border: none;
        padding: 12px 16px;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: #e8f4fd;
        color: #1565c0;
        border: none;
        padding: 12px 16px;
        border-radius: 8px;
    }
    
    /* JSON viewer */
    .stJson {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e5e5e7;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e5e7;
    }
    
    [data-testid="stSidebar"] h3 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: -0.005em;
        color: #1d1d1f;
        margin-bottom: 16px;
    }
    
    [data-testid="stSidebar"] p {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        color: #86868b;
        line-height: 1.6;
    }
    
    [data-testid="stSidebar"] ul {
        padding-left: 20px;
        margin: 12px 0;
    }
    
    [data-testid="stSidebar"] li {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        color: #1d1d1f;
        margin: 6px 0;
        line-height: 1.5;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 24px;
        font-weight: 600;
        color: #1d1d1f;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 13px;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="Prediction Markets Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("Prediction Markets Monitor")

# Set API keys from secrets
os.environ["OPINION_API_KEY"] = st.secrets.get("OPINION_API_KEY", "")
os.environ["PREDICT_API_KEY"] = st.secrets.get("PREDICT_API_KEY", "")

# Load button
if st.button("Load Full Market Data", type="primary", use_container_width=True):
    st.session_state.loading = True
    st.cache_data.clear()

# Loading state
if st.session_state.get("loading"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opinion.Trade")
        with st.spinner("Loading data..."):
            try:
                from opinion_monitor import run as run_opinion
                st.session_state.opinion_data = run_opinion()
            except Exception as e:
                st.session_state.opinion_data = {"error": str(e)}
    
    with col2:
        st.subheader("Predict.Fun")
        with st.spinner("Loading data..."):
            try:
                from predict_monitor import run as run_predict
                st.session_state.predict_data = run_predict()
            except Exception as e:
                st.session_state.predict_data = {"error": str(e)}
    
    st.session_state.loading = False
    st.rerun()

# Display results
col1, col2 = st.columns(2)

with col1:
    st.subheader("Opinion.Trade")
    if "opinion_data" in st.session_state:
        data = st.session_state.opinion_data
        if "error" in 
            st.error(f"Error: {data['error']}")
        else:
            markets = data.get('markets_count', 0)
            tokens = data.get('tokens_count', 0)
            st.metric(label="Markets", value=f"{markets}")
            st.metric(label="Tokens", value=f"{tokens}")
            st.json(data)
    else:
        st.info("Press 'Load Full Market Data' to begin")

with col2:
    st.subheader("Predict.Fun")
    if "predict_data" in st.session_state:
        data = st.session_state.predict_data
        if "error" in 
            st.error(f"Error: {data['error']}")
        else:
            markets = data.get('total_markets', 0)
            st.metric(label="Markets", value=f"{markets}")
            st.json(data)
    else:
        st.info("Press 'Load Full Market Data' to begin")

# Sidebar
with st.sidebar:
    st.subheader("Market Data")
    
    if st.session_state.get("loading"):
        st.info("Loading...")
    elif "opinion_data" in st.session_state and "predict_data" in st.session_state:
        st.success("Data loaded")
        st.metric(label="Opinion.Trade", value=f"{st.session_state.opinion_data.get('markets_count', 0)} markets")
        st.metric(label="Predict.Fun", value=f"{st.session_state.predict_data.get('total_markets', 0)} markets")
        st.metric(label="Updated", value=datetime.now().strftime("%H:%M:%S"))
    else:
        st.caption("No data loaded")
    
    st.divider()
    
    st.subheader("How to Find Arbitrage")
    st.markdown("""
    1. Press **Load Full Market Data**
    2. Wait 45–75 seconds for complete scan
    3. Use browser **Ctrl+F** to search:
       - Event names in `title` or `symbol`
       - Compare `bestAsk` / `bestBid` prices
    4. Price difference > 2–3% = arbitrage opportunity
    """)
""")
