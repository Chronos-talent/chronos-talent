import os
import pandas as pd
from datetime import datetime
import sqlite3

class ResumeTailor:
    def __init__(self):
        self.db_path = 'chronos.db'
        self.upload_folder = 'uploads'
        self.tailored_folder = 'tailored_resumes'
        
        # Create folders if they don't exist
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.tailored_folder, exist_ok=True)
    
    def save_uploaded_cv(self, uploaded_file, user_name):
        """Save uploaded CV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{user_name}_{timestamp}_{uploaded_file.name}"
        filepath = os.path.join(self.upload_folder, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                original_filename TEXT,
                stored_filename TEXT,
                upload_date TEXT,
                skills TEXT,
                experience TEXT,
                education TEXT,
                target_role TEXT
            )
        ''')
        
        cursor.execute('''
            INSERT INTO resumes (user_name, original_filename, stored_filename, upload_date)
            VALUES (?, ?, ?, ?)
        ''', (user_name, uploaded_file.name, filename, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return filename
    
    def tailor_resume(self, resume_id, job_id):
        """Tailor resume for specific job"""
        # Get resume and job details
        conn = sqlite3.connect(self.db_path)
        
        # Get resume
        resume = pd.read_sql("SELECT * FROM resumes WHERE id = ?", conn, params=(resume_id,))
        
        # Get job
        job = pd.read_sql("SELECT * FROM jobs WHERE id = ?", conn, params=(job_id,))
        
        conn.close()
        
        if resume.empty or job.empty:
            return None
        
        job = job.iloc[0]
        
        # Create tailored resume content
        tailored_content = f"""
==========================================
TAILORED RESUME
==========================================
Target Position: {job['title']}
Company: {job['company']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

==========================================
JOB DESCRIPTION
==========================================
{job['description']}

==========================================
TAILORED RESUME CONTENT
==========================================

[Your optimized resume based on the job requirements above]

Key skills highlighted for this role:
• Sales experience
• Tech industry knowledge
• Client relationship management

"""
        
        # Save tailored resume
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = job['title'].replace(' ', '_').replace('/', '_')
        safe_company = job['company'].replace(' ', '_').replace('/', '_')
        output_filename = f"tailored_{safe_company}_{safe_title}_{timestamp}.txt"
        output_path = os.path.join(self.tailored_folder, output_filename)
        
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(tailored_content)
        
        return output_path
    
    def get_user_resumes(self, user_name=None):
        """Get all resumes or filter by user"""
        conn = sqlite3.connect(self.db_path)
        if user_name:
            query = "SELECT * FROM resumes WHERE user_name = ? ORDER BY upload_date DESC"
            df = pd.read_sql(query, conn, params=(user_name,))
        else:
            df = pd.read_sql("SELECT * FROM resumes ORDER BY upload_date DESC", conn)
        conn.close()
        return df