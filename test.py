import streamlit as st
import sys
import os

st.set_page_config(page_title="Chronos Talent Test", page_icon="🤖")

st.title("✅ CHRONOS TALENT - TEST PAGE")
st.write("If you see this, Streamlit is working!")

st.subheader("System Information:")
st.write(f"Python version: {sys.version}")
st.write(f"Current directory: {os.getcwd()}")
st.write(f"Files in directory: {os.listdir('.')}")

try:
    st.write("---")
    st.write("Testing database import...")
    from database import SessionLocal, Job
    st.success("✅ Database imported successfully!")
except Exception as e:
    st.error(f"Import error: {str(e)}")
