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

# UNIVERSAL SKILL DATABASE - Works for ANY career
def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    skill_categories = {}
    
    # Comprehensive skill keywords for ALL professions
    skill_keywords = {
        # TECH SKILLS
        "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy"],
        "JavaScript": ["javascript", "js", "node.js", "react", "vue", "angular", "typescript"],
        "Java": ["java", "spring", "maven", "gradle"],
        "C++": ["c++", "cpp", "c plus plus"],
        "C#": ["c#", "c sharp", ".net", "dotnet"],
        "Ruby": ["ruby", "rails", "ruby on rails"],
        "PHP": ["php", "laravel", "wordpress"],
        "SQL": ["sql", "mysql", "postgresql", "database", "query"],
        "HTML/CSS": ["html", "css", "scss", "sass", "bootstrap", "tailwind"],
        "Cloud": ["aws", "azure", "gcp", "cloud", "lambda", "ec2", "s3"],
        "DevOps": ["docker", "kubernetes", "jenkins", "ci/cd", "github actions"],
        "Mobile Dev": ["android", "ios", "swift", "kotlin", "flutter", "react native"],
        
        # AI & DATA SKILLS
        "Machine Learning": ["machine learning", "ml", "tensorflow", "pytorch", "keras", "ai"],
        "Data Science": ["data science", "data analysis", "analytics", "statistics", "visualization"],
        "OpenAI API": ["openai", "gpt", "chatgpt", "llm", "claude", "anthropic", "langchain"],
        "Data Visualization": ["tableau", "power bi", "looker", "grafana"],
        "Big Data": ["hadoop", "spark", "kafka", "data pipeline"],
        
        # AI TOOLS & AUTOMATION
        "Automation": ["automation", "zapier", "make", "integromat", "n8n", "workflow"],
        "No-Code": ["no-code", "low-code", "bubble", "adalo", "flutterflow", "retool"],
        "Chatbot": ["chatbot", "rasa", "botpress", "voiceflow", "dialogflow", "twilio"],
        "AI Tools": ["langchain", "hugging face", "transformers", "llama", "embedding"],
        
        # BUSINESS & SALES SKILLS
        "Sales": ["sales", "b2b", "business development", "client acquisition", "revenue", "quota"],
        "Account Management": ["account management", "client relations", "customer success", "key accounts"],
        "CRM": ["crm", "salesforce", "hubspot", "zoho", "pipedrive"],
        "Negotiation": ["negotiation", "closing", "deal", "contract"],
        "Lead Generation": ["lead generation", "prospecting", "cold calling", "outreach"],
        "Sales Strategy": ["sales strategy", "go-to-market", "gtm", "territory management"],
        
        # MARKETING SKILLS
        "Digital Marketing": ["digital marketing", "online marketing", "growth marketing"],
        "Content Creation": ["content", "writing", "blog", "copywriting", "editorial"],
        "SEO": ["seo", "search engine optimization", "keyword research"],
        "Social Media": ["social media", "instagram", "linkedin", "tiktok", "twitter"],
        "Email Marketing": ["email marketing", "mailchimp", "campaign", "newsletter"],
        "Marketing Analytics": ["marketing analytics", "google analytics", "data studio"],
        
        # COMMUNICATION & SOFT SKILLS
        "Communication": ["communication", "verbal", "written", "presentation", "public speaking"],
        "Leadership": ["leadership", "team lead", "management", "mentoring", "supervising"],
        "Project Management": ["project management", "agile", "scrum", "jira", "confluence", "trello"],
        "Problem Solving": ["problem solving", "critical thinking", "analytical", "troubleshooting"],
        "Teamwork": ["teamwork", "collaboration", "cross-functional", "interpersonal"],
        "Time Management": ["time management", "organization", "multitasking", "deadline"],
        
        # CREATIVE SKILLS
        "Graphic Design": ["graphic design", "photoshop", "illustrator", "figma", "canva"],
        "UI/UX Design": ["ui", "ux", "user interface", "user experience", "wireframe", "prototype"],
        "Video Editing": ["video editing", "premiere", "final cut", "davinci resolve"],
        "Photography": ["photography", "photo editing", "lightroom"],
        "Writing": ["writing", "creative writing", "technical writing", "editing"],
        
        # HR & RECRUITING
        "Recruiting": ["recruiting", "talent acquisition", "sourcing", "headhunting"],
        "HR": ["hr", "human resources", "employee relations", "onboarding", "benefits"],
        "Training": ["training", "learning & development", "l&d", "coaching"],
        
        # FINANCE & ADMIN
        "Accounting": ["accounting", "bookkeeping", "quickbooks", "xero", "audit"],
        "Finance": ["finance", "financial analysis", "budgeting", "forecasting"],
        "Excel": ["excel", "spreadsheet", "vba", "pivot tables"],
        "Administrative": ["administration", "office management", "executive assistant", "scheduling"],
        
        # CUSTOMER SERVICE
        "Customer Service": ["customer service", "customer support", "help desk", "client service"],
        "Technical Support": ["technical support", "it support", "helpdesk", "troubleshooting"],
        
        # HEALTHCARE
        "Healthcare": ["healthcare", "medical", "clinical", "patient care", "nursing"],
        "Medical Coding": ["medical coding", "cpt", "icd-10", "billing"],
        
        # EDUCATION
        "Teaching": ["teaching", "education", "instruction", "curriculum", "lesson planning"],
        "ESL": ["esl", "english as second language", "tefl", "tesol"],
        
        # LEGAL
        "Legal": ["legal", "law", "attorney", "lawyer", "paralegal", "contract law"],
        "Compliance": ["compliance", "regulatory", "policy", "risk management"],
        
        # ENGLISH/ARTS (for your CV!)
        "English": ["english", "literature", "creative writing", "grammar", "editing"],
        "Teaching English": ["teaching english", "esl instructor", "language teacher"],
        "Editing": ["editing", "proofreading", "copy editing", "manuscript"],
        "Research": ["research", "academic research", "qualitative research", "literature review"],
        "Liberal Arts": ["liberal arts", "humanities", "arts", "philosophy", "history"],
    }
    
    # Also look for job titles/roles
    role_keywords = {
        "Sales": ["sales representative", "account executive", "sdr", "bdr", "sales manager"],
        "Marketing": ["marketing manager", "marketing specialist", "growth hacker"],
        "Engineering": ["software engineer", "developer", "programmer", "tech lead"],
        "Data": ["data scientist", "data analyst", "data engineer"],
        "Product": ["product manager", "product owner", "product specialist"],
        "Design": ["designer", "ui designer", "ux designer", "graphic designer"],
        "HR": ["hr manager", "recruiter", "talent acquisition"],
        "Customer Support": ["customer support", "customer service", "support specialist"],
        "Teacher": ["teacher", "instructor", "professor", "educator", "lecturer"],
        "Writer": ["writer", "content writer", "copywriter", "editor"],
        "Administrative": ["administrative assistant", "executive assistant", "office manager"],
    }
    
    # Check for skills
    for category, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_skills.append(category)
                skill_categories[category] = skill_categories.get(category, 0) + 1
                break
    
    # Check for roles
    for category, keywords in role_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                role_skill = f"{category} Role"
                if role_skill not in found_skills:
                    found_skills.append(role_skill)
                break
    
    # If no skills found, try to extract based on common sections
    if len(found_skills) < 3:
        # Look for education section
        if "bachelor" in text_lower or "master" in text_lower or "phd" in text_lower or "degree" in text_lower:
            found_skills.append("Higher Education")
        
        # Look for work experience
        if "year" in text_lower or "experience" in text_lower or "worked" in text_lower:
            found_skills.append("Professional Experience")
        
        # Look for languages
        if "english" in text_lower or "french" in text_lower or "spanish" in text_lower:
            found_skills.append("Languages")
    
    return list(set(found_skills)), skill_categories

# Function to match job requirements based on category
def get_job_requirements(job):
    try:
        category = job.category
    except:
        category = "General"
    
    title_lower = job.title.lower()
    
    # Sales & Business Development jobs
    if any(word in title_lower for word in ["sales", "sdr", "account executive", "ae", "business development"]):
        return ["Communication", "Sales", "Negotiation", "CRM", "Lead Generation", "Account Management"]
    
    # Marketing jobs
    elif any(word in title_lower for word in ["marketing", "growth", "seo", "content"]):
        return ["Digital Marketing", "Content Creation", "SEO", "Social Media", "Marketing Analytics", "Communication"]
    
    # Engineering jobs
    elif any(word in title_lower for word in ["engineer", "developer", "programmer", "software", "backend", "frontend"]):
        return ["Python", "JavaScript", "Java", "SQL", "Cloud", "Problem Solving"]
    
    # AI/ML jobs
    elif any(word in title_lower for word in ["ai", "machine learning", "data scientist", "llm"]):
        return ["Python", "Machine Learning", "OpenAI API", "Data Science", "SQL", "Problem Solving"]
    
    # Design jobs
    elif any(word in title_lower for word in ["designer", "ui", "ux", "graphic"]):
        return ["UI/UX Design", "Graphic Design", "Figma", "Creative", "Communication"]
    
    # Writing/Content jobs
    elif any(word in title_lower for word in ["writer", "content", "copywriter", "editor"]):
        return ["Writing", "Editing", "Content Creation", "Communication", "Research"]
    
    # Teaching/Education jobs
    elif any(word in title_lower for word in ["teacher", "instructor", "educator", "professor"]):
        return ["Teaching", "Communication", "Curriculum Development", "Patience", "Leadership"]
    
    # Customer Service jobs
    elif any(word in title_lower for word in ["customer service", "support", "help desk"]):
        return ["Customer Service", "Communication", "Problem Solving", "Patience", "CRM"]
    
    # HR/Recruiting jobs
    elif any(word in title_lower for word in ["hr", "recruiter", "talent", "human resources"]):
        return ["Recruiting", "HR", "Communication", "Interviewing", "Sourcing"]
    
    # Administrative jobs
    elif any(word in title_lower for word in ["administrative", "executive assistant", "office manager"]):
        return ["Administrative", "Organization", "Time Management", "Excel", "Communication"]
    
    # Default for other roles
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
                    
                    # Show skills in a nice format
                    st.markdown("**Your Skills:**")
                    
                    # Group skills by category for better display
                    for i, skill in enumerate(cv_skills[:8]):
                        st.info(f"📌 {skill}")
                    
                    if len(cv_skills) > 8:
                        st.caption(f"... and {len(cv_skills)-8} more skills")
                    
                    # Calculate match scores for all jobs
                    for job in jobs:
                        job_skills = get_job_requirements(job)
                        match_scores[job.id] = calculate_match_score(cv_skills, job_skills)
        
        st.markdown("---")
        
        # Category filter
        categories = ["All", "AI Automation", "Prompt Engineering", "No-Code AI", 
                      "Chatbot Development", "AI Consultant", "Tech Sales", 
                      "Solutions Engineer", "AI Integration", "Marketing", 
                      "Design", "Writing", "Customer Service", "Administrative"]
        selected_category = st.selectbox("Job Category", categories)
        
        # Job type filter
        job_types = ["All", "Remote", "Hybrid", "On-site", "Freelance/Contract"]
        selected_type = st.selectbox("Job Type", job_types)
        
        st.info("💡 **Skills Over Degrees**\n\nWe match you based on what you can do, not your degree!")
    
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
                    elif score >= 30:
                        st.info(f"📌 {score}% Match")
                    else:
                        st.warning(f"🔍 {score}% Match")
                    
                    job_skills = get_job_requirements(job)
                    matching_skills = set(cv_skills).intersection(set(job_skills))
                    
                    st.markdown(f"""
                    **{job.title}**  
                    {job.company} · {job.location}  
                    
                    **Matching skills:** {', '.join(list(matching_skills)[:3]) if matching_skills else 'None'}
                    
                    *{len(matching_skills)} of {len(job_skills)} skills match*
                    """)
    
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
            if any(word in title_lower for word in ["sales", "sdr", "account executive"]):
                category = "Sales"
            elif any(word in title_lower for word in ["engineer", "developer"]):
                category = "Engineering"
            elif any(word in title_lower for word in ["ai", "machine learning"]):
                category = "AI/ML"
            elif any(word in title_lower for word in ["marketing", "growth"]):
                category = "Marketing"
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
            elif score >= 30:
                match_display = f"📌 {score}% Match"
            else:
                match_display = f"🔍 {score}% Match"
        
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
