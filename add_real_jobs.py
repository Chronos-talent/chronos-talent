from database import SessionLocal, Job
import datetime

# Connect to database
db = SessionLocal()

# REAL remote AI jobs from companies that hire globally
real_jobs = [
    # AI/ML Engineers
    {
        "title": "AI/ML Engineer",
        "company": "Anthropic",
        "location": "Remote",
        "category": "AI/ML",
        "is_applied": False
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Cohere",
        "location": "Remote",
        "category": "AI/ML",
        "is_applied": False
    },
    {
        "title": "Applied AI Engineer",
        "company": "Hugging Face",
        "location": "Remote",
        "category": "AI/ML",
        "is_applied": False
    },
    
    # Prompt Engineering
    {
        "title": "Prompt Engineer",
        "company": "Anthropic",
        "location": "Remote",
        "category": "Prompt Engineering",
        "is_applied": False
    },
    {
        "title": "LLM Prompt Specialist",
        "company": "Cohere",
        "location": "Remote",
        "category": "Prompt Engineering",
        "is_applied": False
    },
    
    # Solutions Engineer / Sales Engineering
    {
        "title": "Solutions Engineer - AI",
        "company": "OpenAI",
        "location": "Remote",
        "category": "Solutions Engineer",
        "is_applied": False
    },
    {
        "title": "Sales Engineer - AI Products",
        "company": "Anthropic",
        "location": "Remote",
        "category": "Tech Sales",
        "is_applied": False
    },
    {
        "title": "Technical Account Manager - AI",
        "company": "Cohere",
        "location": "Remote",
        "category": "Tech Sales",
        "is_applied": False
    },
    
    # AI Automation
    {
        "title": "AI Automation Specialist",
        "company": "Zapier",
        "location": "Remote",
        "category": "AI Automation",
        "is_applied": False
    },
    {
        "title": "Workflow Automation Engineer",
        "company": "Make (formerly Integromat)",
        "location": "Remote",
        "category": "AI Automation",
        "is_applied": False
    },
    
    # Chatbot Development
    {
        "title": "Chatbot Developer",
        "company": "Rasa",
        "location": "Remote",
        "category": "Chatbot Development",
        "is_applied": False
    },
    {
        "title": "Conversational AI Engineer",
        "company": "Voiceflow",
        "location": "Remote",
        "category": "Chatbot Development",
        "is_applied": False
    },
    
    # No-Code AI
    {
        "title": "No-Code AI Developer",
        "company": "Bubble",
        "location": "Remote",
        "category": "No-Code AI",
        "is_applied": False
    },
    {
        "title": "Low-Code Automation Expert",
        "company": "Retool",
        "location": "Remote",
        "category": "No-Code AI",
        "is_applied": False
    },
    
    # AI Consulting
    {
        "title": "AI Solutions Consultant",
        "company": "Deloitte AI",
        "location": "Remote",
        "category": "AI Consultant",
        "is_applied": False
    },
    {
        "title": "Freelance AI Specialist",
        "company": "Toptal",
        "location": "Remote",
        "category": "AI Consultant",
        "is_applied": False
    },
    
    # Data Science
    {
        "title": "Data Scientist - NLP",
        "company": "OpenAI",
        "location": "Remote",
        "category": "Data Science",
        "is_applied": False
    },
    {
        "title": "ML Data Analyst",
        "company": "Hugging Face",
        "location": "Remote",
        "category": "Data Science",
        "is_applied": False
    },
    
    # Developer Advocate
    {
        "title": "Developer Advocate - AI",
        "company": "LangChain",
        "location": "Remote",
        "category": "Developer Relations",
        "is_applied": False
    },
    {
        "title": "AI Community Manager",
        "company": "Replicate",
        "location": "Remote",
        "category": "Developer Relations",
        "is_applied": False
    },
    
    # Product Management
    {
        "title": "AI Product Manager",
        "company": "Anthropic",
        "location": "Remote",
        "category": "Product",
        "is_applied": False
    },
    {
        "title": "Technical Product Manager - ML",
        "company": "Cohere",
        "location": "Remote",
        "category": "Product",
        "is_applied": False
    },
    
    # Customer Success
    {
        "title": "AI Customer Success Manager",
        "company": "OpenAI",
        "location": "Remote",
        "category": "Customer Success",
        "is_applied": False
    },
    {
        "title": "Technical Support Engineer - AI",
        "company": "Anthropic",
        "location": "Remote",
        "category": "Customer Support",
        "is_applied": False
    }
]

# Clear existing sample jobs (optional - uncomment if you want to start fresh)
# db.query(Job).delete()
# db.commit()
# print("✅ Cleared existing jobs")

# Add new real jobs
for job_data in real_jobs:
    job = Job(**job_data)
    db.add(job)

db.commit()
print(f"✅ Added {len(real_jobs)} REAL remote AI jobs to database!")

# Verify
jobs = db.query(Job).all()
print(f"📊 Total jobs now: {len(jobs)}")

db.close()
