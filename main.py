import streamlit as st
import sys

st.set_page_config(page_title="Chronos Talent Test", page_icon="🤖")

st.title("🤖 Chronos Talent - Test Page")
st.write("If you can see this, Streamlit is working!")

st.subheader("System Info:")
st.write(f"Python version: {sys.version}")

try:
    st.write("Attempting to import database...")
    from database import SessionLocal, Job
    st.success("✅ Database imported successfully!")
    
    st.write("Attempting to connect to database...")
    session = SessionLocal()
    st.success("✅ Database connected!")
    
    st.write("Counting jobs...")
    total_jobs = session.query(Job).count()
    st.success(f"✅ Found {total_jobs} jobs!")
    
    session.close()
    
except Exception as e:
    st.error(f"❌ ERROR: {str(e)}")
    st.write("Error type:", type(e).__name__)
    import traceback
    st.code(traceback.format_exc())
