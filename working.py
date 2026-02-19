import streamlit as st
from database import SessionLocal, Job
import pandas as pd
import PyPDF2
import docx2txt
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import io

st.set_page_config(page_title="Chronos Talent", page_icon="🤖", layout="wide")

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

# Function to extract skills from text
def extract_skills(text):
    # Common AI/tech skills to look for
    skill_keywords = {
        "Python": ["python", "django", "flask"],
        "JavaScript": ["javascript", "js", "node.js", "react", "vue"],
        "OpenAI API": ["openai", "gpt", "chatgpt", "llm"],
        "Machine Learning": ["machine learning", "ml", "tensorflow", "pytorch", "scikit-learn"],
        "Data Science": ["data science", "pandas", "numpy", "jupyter"],
        "AI Tools": ["langchain", "hugging face", "transformers", "llama"],
        "Automation": ["automation", "zapier", "make", "integromat", "n8n"],
        "No-Code": ["no-code", "low-code", "bubble", "adalo", "flutterflow"],
        "Chatbot": ["chatbot", "rasa", "botpress", "voiceflow", "dialogflow"],
        "Cloud": ["aws", "azure", "gcp", "cloud"],
        "Database": ["sql", "postgresql", "mongodb", "redis"],
        "DevOps": ["docker", "kubernetes", "ci/cd", "jenkins"],
        "API": ["api", "rest", "graphql", "fastapi"],
        "Communication": ["communication", "presentation", "leadership", "teamwork"],
        "Sales": ["sales", "b2b", "client", "negotiation", "account management"]
    }
    
    text_lower = text.lower()
    found_skills = []
    skill_categories = {}
    
    for category, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_skills.append(category)
                skill_categories[category] = skill_categories.get(category, 0) + 1
                break
    
    return list(set(found_skills)), skill_categories

# Function to calculate match score
def calculate_match_score(cv_skills, job_skills):
    if not cv_skills or not job_skills:
        return 0
    
    cv_set = set(cv_skills)
    job_set = set(job_skills)
    
    if not job_set:
        return 0
    
    matches = cv_set.intersection(job_set)
    match_percentage = (len(matches) / len(job_set)) * 100
    return round(match_percentage, 1)

try:
    # Connect to database
    db = SessionLocal()
    jobs = db.query(Job).all()
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Filter Jobs")
        
        # CV Upload Section
        st.markdown("---")
        st.subheader("📤 Upload Your CV")
        st.caption("Let AI match you with the perfect job!")
        
        uploaded_file = st.file_uploader(
            "Upload resume (PDF or DOCX)", 
            type=['pdf', 'docx'],
            help="Upload your CV and we'll automatically find matching jobs based on your skills!"
        )
        
        cv_skills = []
        match_scores = {}
        
        if uploaded_file is not None:
            with st.spinner("🔍 AI is analyzing your CV..."):
                # Extract text based on file type
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)
                
                # Extract skills
                cv_skills, skill_categories = extract_skills(text)
                
                # Display found skills
                if cv_skills:
                    st.success(f"✅ Found {len(cv_skills)} skills!")
                    
                    # Show skills in columns
                    col1, col2 = st.columns(2)
                    for i, skill in enumerate(cv_skills[:6]):
                        if i < 3:
                            col1.info(f"📌 {skill}")
                        else:
                            col2.info(f"📌 {skill}")
                    
                    if len(cv_skills) > 6:
                        st.caption(f"... and {len(cv_skills)-6} more skills")
                    
                    # Calculate match scores for all jobs
                    for job in jobs:
                        # Define job skills based on category and title
                        job_skills = []
                        try:
                            category = job.category
                        except:
                            category = "General"
                        
                        # Map job categories to required skills
                        if "AI" in str(category) or "Machine Learning" in str(job.title):
                            job_skills = ["Python", "Machine Learning", "OpenAI API", "Data Science"]
                        elif "Chatbot" in str(category) or "Bot" in str(job.title):
                            job_skills = ["Python", "Chatbot", "API", "JavaScript"]
                        elif "Automation" in str(category) or "Automation" in str(job.title):
                            job_skills = ["Automation", "Python", "API", "No-Code"]
                        elif "Prompt" in str(category) or "LLM" in str(job.title):
                            job_skills = ["OpenAI API", "Machine Learning", "Python", "Communication"]
                        elif "No-Code" in str(category):
                            job_skills = ["No-Code", "Automation", "API", "JavaScript"]
                        elif "Sales" in str(category) or "SDR" in str(job.title):
                            job_skills = ["Communication", "Sales", "API", "CRM"]
                        else:
                            job_skills = ["Communication", "Problem Solving", "Teamwork"]
                        
                        # Calculate match score
                        match_scores[job.id] = calculate_match_score(cv_skills, job_skills)
        
        st.markdown("---")
        
        # Category filter
        categories = ["All", "AI Automation", "Prompt Engineering", "No-Code AI", 
                      "Chatbot Development", "AI Consultant", "Tech Sales", 
                      "Solutions Engineer", "AI Integration"]
        selected_category = st.selectbox("Job Category", categories)
        
        # Job type filter
        job_types = ["All", "Remote", "Hybrid", "On-site", "Freelance/Contract"]
        selected_type = st.selectbox("Job Type", job_types)
        
        # Skill filter
        all_skills = ["Python", "JavaScript", "OpenAI API", "Machine Learning", 
                     "Automation", "No-Code", "Chatbot", "Cloud", "API", 
                     "Communication", "Sales", "Data Science"]
        selected_skills = st.multiselect("Skills/Tools", all_skills)
        
        st.info("💡 **Skills Over Degrees**\n\nWe match you based on what you can build, not your degree!")
    
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
    
    # Show match summary if CV uploaded
    if cv_skills and match_scores:
        st.markdown("---")
        st.subheader("🎯 Your Job Matches")
        
        # Get top 3 matches
        top_matches = sorted(match_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        cols = st.columns(3)
        for idx, (job_id, score) in enumerate(top_matches):
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                with cols[idx]:
                    if score >= 70:
                        st.success(f"🔥 {score}% Match")
                    elif score >= 50:
                        st.info(f"📊 {score}% Match")
                    else:
                        st.warning(f"📌 {score}% Match")
                    
                    st.markdown(f"""
                    **{job.title}**  
                    {job.company} · {job.location}  
                    🏷️ {getattr(job, 'category', 'General')}
                    
                    *Skills you have: {min(3, len(cv_skills))} matching skills*
                    """)
    
    # Featured Categories
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
    
    # Jobs Table
    st.markdown("---")
    st.subheader("📋 Available Jobs")
    
    # Create dataframe
    job_data = []
    for job in jobs:
        try:
            category = job.category
        except:
            # Smart category assignment
            title_lower = job.title.lower()
            if "sales" in title_lower or "sdr" in title_lower:
                category = "Tech Sales"
            elif "engineer" in title_lower:
                category = "Solutions Engineer"
            elif "ai" in title_lower or "machine learning" in title_lower:
                category = "AI/ML"
            else:
                category = "General"
        
        location = job.location or "Remote"
        is_remote = "remote" in location.lower()
        
        # Add match score if CV uploaded
        match_display = ""
        if match_scores and job.id in match_scores:
            score = match_scores[job.id]
            if score >= 70:
                match_display = f"🔥 {score}% Match"
            elif score >= 50:
                match_display = f"📊 {score}% Match"
            else:
                match_display = f"📌 {score}% Match"
        
        job_data.append({
            "Title": job.title,
            "Company": job.company,
            "Location": location,
            "Category": category,
            "Match": match_display,
            "Remote": "✅" if is_remote else "❌",
            "Status": "✅ Applied" if job.is_applied else "⏳ Pending"
        })
    
    df = pd.DataFrame(job_data)
    
    # Apply filters
    if selected_category != "All":
        df = df[df["Category"] == selected_category]
    
    st.dataframe(df, use_container_width=True)
    
    # Job Cards
    st.markdown("---")
    st.subheader("📌 Quick Apply Jobs")
    
    cols = st.columns(3)
    for idx, job in enumerate(df.head(6).iterrows()):
        job_data = job[1]
        with cols[idx % 3]:
            match_badge = ""
            if job_data['Match']:
                match_badge = f"<p><span class='match-highlight'>{job_data['Match']}</span></p>"
            
            st.markdown(f"""
            <div style="padding: 1rem; border: 1px solid #ddd; border-radius: 5px; margin: 0.5rem 0;">
                <h4>{job_data['Title']}</h4>
                <p><b>{job_data['Company']}</b> · {job_data['Location']}</p>
                <p>🏷️ {job_data['Category']} · 🌍 Remote: {job_data['Remote']}</p>
                {match_badge}
                <p>{job_data['Status']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    db.close()
    
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("💡 Our AI is learning! Check back soon for more features.")
