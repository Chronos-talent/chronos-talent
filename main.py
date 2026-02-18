import streamlit as st
from database import SessionLocal, Job
import pandas as pd

st.set_page_config(page_title="Chronos Talent", page_icon="🤖", layout="wide")

st.title("🤖 Chronos Talent AI Job Platform")
st.markdown("---")

try:
    session = SessionLocal()
    jobs = session.query(Job).all()
    total_jobs = len(jobs)
    pending = session.query(Job).filter_by(is_applied=False).count()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", total_jobs)
    with col2:
        st.metric("Pending Applications", pending)
    with col3:
        st.metric("Applied", total_jobs - pending)
    
    st.markdown("---")
    st.subheader("📋 Available Jobs")
    
    if jobs:
        job_data = []
        for job in jobs:
            job_data.append({
                "Title": job.title,
                "Company": job.company,
                "Location": job.location,
                "Applied": "✅" if job.is_applied else "⏳"
            })
        df = pd.DataFrame(job_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No jobs found in database")
    
    session.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
