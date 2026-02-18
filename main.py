#!/usr/bin/env python3
"""
Chronos Talent - Main Program
"""

import streamlit as st
from database import SessionLocal, Job
import pandas as pd

# Page config
st.set_page_config(
    page_title="Chronos Talent",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 Chronos Talent AI Job Platform")
st.markdown("---")

def main():
    try:
        # Connect to database
        session = SessionLocal()
        jobs = session.query(Job).all()
        total_jobs = len(jobs)
        pending = session.query(Job).filter_by(is_applied=False).count()
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Jobs", total_jobs)
        with col2:
            st.metric("Pending Applications", pending)
        with col3:
            st.metric("Applied", total_jobs - pending)
        
        st.markdown("---")
        
        # Show jobs table
        st.subheader("📋 Available Jobs")
        
        if jobs:
            # Convert to DataFrame for display
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

if __name__ == "__main__":
    main()
