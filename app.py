import streamlit as st
import os

st.title("🔍 Диагностика секретов")

st.write("OPINION_API_KEY:", "*" * len(os.getenv("OPINION_API_KEY", "")) if os.getenv("OPINION_API_KEY") else "❌ НЕТ")
st.write("PREDICT_API_KEY:", "*" * len(os.getenv("PREDICT_API_KEY", "")) if os.getenv("PREDICT_API_KEY") else "❌ НЕТ")

if not os.getenv("OPINION_API_KEY") or not os.getenv("PREDICT_API_KEY"):
    st.error("⚠️ Секреты не загружены! Настрой их в Streamlit Cloud → Manage app → Settings → Secrets")
else:
    st.success("✅ Секреты загружены")
