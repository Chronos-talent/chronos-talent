import streamlit as st
from database import SessionLocal, Job
import pandas as pd

st.set_page_config(page_title="Chronos Talent", page_icon="🤖", layout="wide")

st.title("🤖 Chronos Talent - AI Job Platform")
st.markdown("---")

try:
    # Connect to database
    db = SessionLocal()
    jobs = db.query(Job).all()
    
    # Show metrics
    st.subheader("📊 Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", len(jobs))
    with col2:
        applied = sum(1 for j in jobs if j.is_applied)
        st.metric("Applied", applied)
    with col3:
        st.metric("Pending", len(jobs) - applied)
    
    # Show jobs table
    st.markdown("---")
    st.subheader("📋 Available Jobs")
    
    # Create dataframe
    job_data = []
    for job in jobs:
        job_data.append({
            "Title": job.title,
            "Company": job.company,
            "Location": job.location,
            "Category": job.category or "General",
            "Status": "✅ Applied" if job.is_applied else "⏳ Pending"
        })
    
    df = pd.DataFrame(job_data)
    st.dataframe(df, use_container_width=True)
    
    db.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
