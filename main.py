import streamlit as st
from database import SessionLocal, Job
import pandas as pd

st.set_page_config(page_title="Chronos Talent", page_icon="🤖", layout="wide")

st.title("🤖 Chronos Talent AI Job Platform")
st.markdown("---")

# Database connection
@st.cache_resource
def get_db():
    try:
        return SessionLocal()
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

db = get_db()

if db:
    try:
        # Get all jobs
        jobs = db.query(Job).all()
        total_jobs = len(jobs)
        
        # Calculate applied/pending
        applied_jobs = sum(1 for j in jobs if j.is_applied)
        pending_jobs = total_jobs - applied_jobs
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Jobs", total_jobs)
        with col2:
            st.metric("Pending Applications", pending_jobs)
        with col3:
            st.metric("Applied", applied_jobs)
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filter Jobs")
        col1, col2 = st.columns(2)
        
        with col1:
            # Get unique categories
            categories = ["All"] + list(set([j.category for j in jobs if j.category]))
            selected_category = st.selectbox("Category", categories)
        
        with col2:
            status_filter = st.selectbox("Status", ["All", "Applied", "Pending"])
        
        # Apply filters
        filtered_jobs = jobs
        if selected_category != "All":
            filtered_jobs = [j for j in filtered_jobs if j.category == selected_category]
        
        if status_filter == "Applied":
            filtered_jobs = [j for j in filtered_jobs if j.is_applied]
        elif status_filter == "Pending":
            filtered_jobs = [j for j in filtered_jobs if not j.is_applied]
        
        # Display jobs
        st.subheader(f"📋 Available Jobs ({len(filtered_jobs)})")
        
        if filtered_jobs:
            # Create dataframe for display
            job_data = []
            for job in filtered_jobs:
                job_data.append({
                    "Title": job.title,
                    "Company": job.company,
                    "Location": job.location,
                    "Category": job.category or "General",
                    "Status": "✅ Applied" if job.is_applied else "⏳ Pending"
                })
            
            df = pd.DataFrame(job_data)
            st.dataframe(df, use_container_width=True)
            
            # Show job details in expanders
            st.subheader("📌 Job Details")
            for job in filtered_jobs[:5]:  # Show first 5 jobs in detail
                with st.expander(f"{job.title} @ {job.company}"):
                    st.write(f"**Location:** {job.location}")
                    st.write(f"**Category:** {job.category or 'General'}")
                    st.write(f"**Description:** {job.description}")
                    st.write(f"**Status:** {'✅ Applied' if job.is_applied else '⏳ Pending'}")
        else:
            st.info("No jobs match your filters")
        
        db.close()
        
    except Exception as e:
        st.error(f"Error loading jobs: {str(e)}")
else:
    st.error("Could not connect to database")
