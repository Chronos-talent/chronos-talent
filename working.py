import streamlit as st

st.set_page_config(page_title="Chronos Talent - Working", page_icon="✅")

st.title("✅ Chronos Talent - Working Version")
st.write("Testing database connection...")

try:
    # Try to import database
    from database import SessionLocal, Job
    st.success("✅ Database imported successfully!")
    
    # Try to connect
    db = SessionLocal()
    job_count = db.query(Job).count()
    st.success(f"✅ Connected to database! Found {job_count} jobs")
    
    # Show first job as sample
    if job_count > 0:
        first_job = db.query(Job).first()
        st.write("---")
        st.subheader("📌 Sample Job:")
        st.write(f"**Title:** {first_job.title}")
        st.write(f"**Company:** {first_job.company}")
        st.write(f"**Location:** {first_job.location}")
    
    db.close()
    
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
