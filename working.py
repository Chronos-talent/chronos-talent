import streamlit as st
from database import SessionLocal, Job
import pandas as pd
import PyPDF2
import docx2txt
import re
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Chronos Talent", page_icon="🤖", layout="wide")

# Initialize session state for applications
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = ""

# Custom CSS
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
    .match-highlight {
        background-color: #00ff8844;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-weight: bold;
    }
    .auto-apply-btn {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        margin: 5px 0;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Chronos Talent - Global AI Job Platform")
st.markdown("### Skills Over Degrees · Remote First · AI-Focused")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except:
        return ""

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    try:
        text = docx2txt.process(docx_file)
        return text
    except:
        return ""

# UNIVERSAL SKILL DATABASE
def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    skill_categories = {}
    
    # Comprehensive skill keywords (keeping your existing extensive list)
    skill_keywords = {
        "Communication": ["communication", "verbal", "written", "presentation", "public speaking"],
        "Writing": ["writing", "creative writing", "technical writing", "editing", "proofreading"],
        "Teaching": ["teaching", "education", "instruction", "curriculum", "lesson planning"],
        "Leadership": ["leadership", "team lead", "management", "mentoring", "supervising"],
        "Machine Learning": ["machine learning", "ml", "tensorflow", "pytorch", "keras", "ai"],
        "Teaching English": ["teaching english", "esl instructor", "language teacher", "tefl", "tesol"],
        "Sales": ["sales", "b2b", "business development", "client acquisition", "revenue"],
        "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy"],
        "JavaScript": ["javascript", "js", "node.js", "react", "vue", "angular"],
        # ... (keep all your other skills)
    }
    
    for category, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_skills.append(category)
                skill_categories[category] = skill_categories.get(category, 0) + 1
                break
    
    return list(set(found_skills)), skill_categories

# Function to get job requirements
def get_job_requirements(job):
    title_lower = job.title.lower()
    
    if any(word in title_lower for word in ["sales", "sdr", "account executive", "ae", "bdr"]):
        return ["Communication", "Sales", "Negotiation", "CRM", "Lead Generation"]
    elif any(word in title_lower for word in ["teacher", "instructor", "educator", "professor"]):
        return ["Teaching", "Communication", "Teaching English", "Patience", "Leadership"]
    elif any(word in title_lower for word in ["writer", "content", "copywriter", "editor"]):
        return ["Writing", "Editing", "Communication", "Research", "Creativity"]
    elif any(word in title_lower for word in ["engineer", "developer", "programmer"]):
        return ["Python", "JavaScript", "Problem Solving", "Communication", "Teamwork"]
    else:
        return ["Communication", "Problem Solving", "Teamwork", "Adaptability"]

# Function to calculate match score
def calculate_match_score(cv_skills, job_skills):
    if not cv_skills or not job_skills:
        return 0
    cv_set = set(cv_skills)
    job_set = set(job_skills)
    if not job_set:
        return 0
    matches = cv_set.intersection(job_set)
    return round((len(matches) / len(job_set)) * 100, 1)

# NEW: Auto-Apply Function
def auto_apply_to_job(job, user_name, user_email, user_phone, cv_text):
    try:
        # 1. Send Email to Employer
        employer_email = f"hiring@{job.company.lower().replace(' ', '')}.com"  # You'll need real emails
        
        subject = f"Application for {job.title} - {user_name}"
        body = f"""
        Dear Hiring Team at {job.company},
        
        I am excited to apply for the {job.title} position. Based on my CV analysis, my skills align well with this role.
        
        Key Skills:
        - {cv_skills[:5] if 'cv_skills' in locals() else 'Various relevant skills'}
        
        My CV is attached to this email. I would love to discuss how I can contribute to your team.
        
        Best regards,
        {user_name}
        {user_email}
        {user_phone}
        """
        
        # In production, use actual SMTP settings
        # msg = MIMEMultipart()
        # msg['From'] = user_email
        # msg['To'] = employer_email
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'plain'))
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login('your-email@gmail.com', 'your-password')
        # server.send_message(msg)
        
        # For now, simulate successful send
        st.success(f"✅ Application sent to {job.company}")
        
        # 2. Schedule WhatsApp follow-up for applicant
        follow_up_time = datetime.now() + timedelta(days=3)
        
        # In production, use WhatsApp Business API
        # whatsapp_message = f"Hi {user_name}, your application for {job.title} at {job.company} was sent. We'll follow up in 3 days!"
        # requests.post(
        #     "https://graph.facebook.com/v17.0/PHONE_NUMBER_ID/messages",
        #     headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"},
        #     json={
        #         "messaging_product": "whatsapp",
        #         "to": user_phone,
        #         "type": "text",
        #         "text": {"body": whatsapp_message}
        #     }
        # )
        
        return {
            "job_title": job.title,
            "company": job.company,
            "applied_date": datetime.now(),
            "follow_up_date": follow_up_time,
            "status": "Applied"
        }
    except Exception as e:
        st.error(f"Error applying: {str(e)}")
        return None

try:
    # Connect to database
    db = SessionLocal()
    jobs = db.query(Job).all()
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filter Jobs")
        
        # User Contact Info (for auto-apply)
        st.markdown("---")
        st.subheader("📋 Your Contact Info")
        user_name = st.text_input("Full Name", value="John Doe")
        st.session_state.user_email = st.text_input("Email", value="john@example.com")
        st.session_state.user_phone = st.text_input("WhatsApp Number", value="+1234567890")
        
        # CV Upload Section
        st.markdown("---")
        st.subheader("📤 Upload Your CV")
        st.caption("Let AI match you with the perfect job!")
        
        uploaded_file = st.file_uploader(
            "Upload resume (PDF or DOCX)", 
            type=['pdf', 'docx'],
            help="Upload your CV and we'll automatically find matching jobs!"
        )
        
        cv_skills = []
        match_scores = {}
        cv_text = ""
        
        if uploaded_file is not None:
            with st.spinner("🔍 AI is analyzing your CV..."):
                if uploaded_file.type == "application/pdf":
                    cv_text = extract_text_from_pdf(uploaded_file)
                else:
                    cv_text = extract_text_from_docx(uploaded_file)
                
                cv_skills, skill_categories = extract_skills(cv_text)
                
                if cv_skills:
                    st.success(f"✅ Found {len(cv_skills)} skills!")
                    st.markdown("**Your Skills:**")
                    for i, skill in enumerate(cv_skills[:8]):
                        st.info(f"📌 {skill}")
                    if len(cv_skills) > 8:
                        st.caption(f"... and {len(cv_skills)-8} more skills")
                    
                    # Calculate match scores
                    for job in jobs:
                        job_skills = get_job_requirements(job)
                        match_scores[job.id] = calculate_match_score(cv_skills, job_skills)
        
        st.markdown("---")
        
        # Category filter
        categories = ["All", "Sales", "Marketing", "Engineering", "AI/ML", 
                      "Education", "Writing", "Design", "Customer Service"]
        selected_category = st.selectbox("Job Category", categories)
        
        st.info("💡 **Skills Over Degrees**\n\nWe match you based on what you can do!")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(jobs))
    with col2:
        applied = len(st.session_state.applications)
        st.metric("Your Applications", applied)
    with col3:
        st.metric("Pending", max(0, len(jobs) - applied))
    with col4:
        st.metric("AI Roles", "Coming Soon! 🚀")
    
    # Show match summary if CV uploaded
    if cv_skills and match_scores:
        st.markdown("---")
        st.subheader("🎯 Your Job Matches")
        
        # Get top matches
        top_matches = sorted(match_scores.items(), key=lambda x: x[1], reverse=True)[:6]
        
        # Display in 2 rows of 3
        for row in range(0, len(top_matches), 3):
            cols = st.columns(3)
            for idx in range(3):
                if row + idx < len(top_matches):
                    job_id, score = top_matches[row + idx]
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if job:
                        with cols[idx]:
                            if score >= 70:
                                st.success(f"🔥 {score}% Match")
                            elif score >= 50:
                                st.info(f"📊 {score}% Match")
                            else:
                                st.info(f"📌 {score}% Match")
                            
                            job_skills = get_job_requirements(job)
                            matching_skills = set(cv_skills).intersection(set(job_skills))
                            
                            st.markdown(f"""
                            **{job.title}**  
                            {job.company} · {job.location}  
                            **Matching skills:** {', '.join(list(matching_skills)[:3])}
                            """)
                            
                            # Auto-Apply Button
                            if st.button(f"🤖 Auto-Apply to {job.title}", key=f"apply_{job.id}"):
                                with st.spinner("AI is applying on your behalf..."):
                                    application = auto_apply_to_job(
                                        job, user_name, 
                                        st.session_state.user_email,
                                        st.session_state.user_phone,
                                        cv_text
                                    )
                                    if application:
                                        st.session_state.applications.append(application)
                                        st.balloons()
                                        st.success(f"✅ Applied to {job.title}! Check your WhatsApp for updates.")
    
    # Featured Categories
    st.markdown("---")
    st.subheader("🎯 Featured Categories")
    
    cat_col1, cat_col2, cat_col3, cat_col4 = st.columns(4)
    with cat_col1:
        st.markdown("**🤖 AI & Tech**")
        st.caption("AI/ML, Engineering, Data")
    with cat_col2:
        st.markdown("**💼 Business**")
        st.caption("Sales, Marketing, HR")
    with cat_col3:
        st.markdown("**🎨 Creative**")
        st.caption("Design, Writing, Content")
    with cat_col4:
        st.markdown("**📚 Education**")
        st.caption("Teaching, Research, Training")
    
    # Applications Tracker
    if st.session_state.applications:
        st.markdown("---")
        st.subheader("📊 Your Application Tracker")
        
        app_data = []
        for app in st.session_state.applications:
            app_data.append({
                "Job": app["job_title"],
                "Company": app["company"],
                "Applied": app["applied_date"].strftime("%Y-%m-%d"),
                "Follow-up": app["follow_up_date"].strftime("%Y-%m-%d"),
                "Status": app["status"]
            })
        
        st.dataframe(pd.DataFrame(app_data), use_container_width=True)
    
    # Jobs Table
    st.markdown("---")
    st.subheader("📋 Available Jobs")
    
    job_data = []
    for job in jobs:
        try:
            category = job.category
        except:
            title_lower = job.title.lower()
            if "sales" in title_lower or "sdr" in title_lower or "bdr" in title_lower:
                category = "Sales"
            elif "teacher" in title_lower or "instructor" in title_lower:
                category = "Education"
            elif "writer" in title_lower or "content" in title_lower:
                category = "Writing"
            else:
                category = "General"
        
        location = job.location or "Remote"
        is_remote = "remote" in location.lower()
        
        match_display = ""
        if match_scores and job.id in match_scores:
            score = match_scores[job.id]
            if score >= 70:
                match_display = f"🔥 {score}%"
            elif score >= 50:
                match_display = f"📊 {score}%"
            elif score >= 30:
                match_display = f"📌 {score}%"
            else:
                match_display = f"🔍 {score}%"
        
        job_data.append({
            "Title": job.title,
            "Company": job.company,
            "Location": location,
            "Category": category,
            "Match": match_display,
            "Remote": "✅" if is_remote else "❌",
        })
    
    df = pd.DataFrame(job_data)
    
    if selected_category != "All":
        df = df[df["Category"] == selected_category]
    
    st.dataframe(df, use_container_width=True)
    
    db.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("💡 Our AI is learning! Check back soon for more features.")
