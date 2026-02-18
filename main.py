import streamlit as st

st.set_page_config(page_title="Chronos Talent", page_icon="🤖")

st.title("🤖 Chronos Talent")
st.write("If you see this, Streamlit is working!")

try:
    from database import SessionLocal, Job
    st.success("✅ Database imports working!")
except Exception as e:
    st.error(f"❌ Import error: {str(e)}")
