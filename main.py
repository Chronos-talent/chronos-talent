#!/usr/bin/env python3
"""
Chronos Talent - Main Program
"""

from scrapers.linkedin_scraper import LinkedInScraper
from database import SessionLocal, Job
import time

def mine_jobs():
    """Find new jobs"""
    print("\n" + "="*50)
    print("🤖 CHRONOS TALENT - JOB MINING")
    print("="*50)
    
    # Create scraper
    scraper = LinkedInScraper()
    
    try:
        # Search for jobs
        jobs_found = scraper.search_jobs()
        
        # Show summary
        session = SessionLocal()
        total_jobs = session.query(Job).count()
        pending = session.query(Job).filter_by(is_applied=False).count()
        session.close()
        
        print("\n" + "="*50)
        print("📊 SUMMARY")
        print("="*50)
        print(f"✅ New jobs found: {jobs_found}")
        print(f"📁 Total jobs in database: {total_jobs}")
        print(f"⏳ Pending applications: {pending}")
        print("="*50 + "\n")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    print("🚀 Starting Chronos Talent...")
    mine_jobs()