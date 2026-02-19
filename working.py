import streamlit as st
from database import SessionLocal, Job
import pandas as pd

st.set_page_config(page_title="Chronos Talent", page_icon="🤖", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .category-filter {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .job-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Chronos Talent - Global AI Job Platform")
st.markdown("### Skills Over Degrees · Remote First · AI-Focused")

try:
    # Connect to database
    db = SessionLocal()
    jobs = db.query(Job).all()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Jobs")
    
    # Category filter
    categories = ["All", "AI Automation", "Prompt Engineering", "No-Code AI", 
                  "Chatbot Development", "AI Consultant", "Tech Sales", 
                  "Solutions Engineer", "AI Integration"]
    
    selected_category = st.sidebar.selectbox("Job Category", categories)
    
    # Job type filter
    job_types = ["All", "Remote", "Hybrid", "On-site", "Freelance/Contract"]
    selected_type = st.sidebar.selectbox("Job Type", job_types)
    
    # Skill filter (multi-select)
    skills = ["Python", "JavaScript", "Zapier", "Rasa", "OpenAI API", 
              "Voiceflow", "Make/Integromat", "No-Code", "ChatGPT API", 
              "Botpress", "Twilio", "Workflow Automation"]
    selected_skills = st.sidebar.multiselect("Skills/Tools", skills)
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Skills Over Degrees**\n\nWe focus on what you can build, not just your degree. Showcase your projects!")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(jobs))
    with col2:
        applied = sum(1 for j in jobs if j.is_applied)
        st.metric("Applied", applied)
    with col3:
        st.metric("Pending", len(jobs) - applied)
    with col4:
        st.metric("AI Roles", "Coming Soon! 🚀")
    
    # Expanded job categories with more AI-focused roles
    st.markdown("---")
    st.subheader("🎯 Featured AI Categories")
    
    cat_col1, cat_col2, cat_col3, cat_col4 = st.columns(4)
    
    with cat_col1:
        st.markdown("**🤖 AI Automation**")
        st.caption("Build workflows, integrate AI tools")
        
    with cat_col2:
        st.markdown("**⚡ Prompt Engineering**")
        st.caption("LLM specialists, ChatGPT experts")
        
    with cat_col3:
        st.markdown("**🔧 No-Code AI**")
        st.caption("Build AI apps without code")
        
    with cat_col4:
        st.markdown("**💬 Chatbot Dev**")
        st.caption("Rasa, Botpress, Voiceflow")
    
    st.markdown("---")
    st.subheader("📋 Available Jobs")
    
    # Create dataframe with enhanced categories
    job_data = []
    for job in jobs:
        # Safely get category
        try:
            category = job.category
        except AttributeError:
            # Assign smarter categories based on job title
            title_lower = job.title.lower()
            if "sales" in title_lower or "sdr" in title_lower:
                category = "Tech Sales"
            elif "engineer" in title_lower and "solution" in title_lower:
                category = "Solutions Engineer"
            elif "ai" in title_lower or "machine learning" in title_lower:
                category = "AI/ML"
            elif "automation" in title_lower:
                category = "AI Automation"
            elif "prompt" in title_lower:
                category = "Prompt Engineering"
            else:
                category = "General"
        
        # Determine if remote
        location = job.location
        is_remote = "remote" in location.lower() if location else False
        
        job_data.append({
            "Title": job.title,
            "Company": job.company,
            "Location": location,
            "Category": category,
            "Remote": "✅" if is_remote else "❌",
            "Skills": "Python, OpenAI API" if "AI" in category else "Communication, Sales",
            "Status": "✅ Applied" if job.is_applied else "⏳ Pending"
        })
    
    df = pd.DataFrame(job_data)
    
    # Apply filters
    if selected_category != "All":
        df = df[df["Category"] == selected_category]
    
    st.dataframe(df, use_container_width=True)
    
    # Show job cards for better visualization
    st.markdown("---")
    st.subheader("📌 Quick Apply Jobs")
    
    # Display as cards in columns
    cols = st.columns(3)
    for idx, job in enumerate(df.head(6).iterrows()):
        job_data = job[1]
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="padding: 1rem; border: 1px solid #ddd; border-radius: 5px; margin: 0.5rem 0;">
                <h4>{job_data['Title']}</h4>
                <p><b>{job_data['Company']}</b> · {job_data['Location']}</p>
                <p>🏷️ {job_data['Category']} · 🌍 Remote: {job_data['Remote']}</p>
                <p>🛠️ {job_data['Skills']}</p>
                <p>{job_data['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    db.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("💡 Our AI is learning! Check back soon for more features.")
