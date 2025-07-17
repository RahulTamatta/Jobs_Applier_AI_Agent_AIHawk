#!/usr/bin/env python3
"""
LinkedIn Job Application Bot Runner

This script automates job searching and application on LinkedIn using the
existing project structure for resume generation and job application tracking.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import traceback

from src.linkedin_bot import LinkedInBot
import yaml
from src.logging import logger

def load_configuration() -> Dict[str, Any]:
    """Load configuration from YAML files"""
    try:
        # Load secrets (LinkedIn credentials)
        secrets_path = Path("data_folder/secrets.yaml")
        with open(secrets_path, 'r') as f:
            secrets = yaml.safe_load(f)
        
        # Load work preferences
        work_preferences_path = Path("data_folder/work_preferences.yaml")
        with open(work_preferences_path, 'r') as f:
            work_preferences = yaml.safe_load(f)
        
        # Validate required fields
        required_secrets = ["linkedin_email", "linkedin_password"]
        missing_secrets = [key for key in required_secrets if not secrets.get(key)]
        
        if missing_secrets:
            raise ValueError(f"Missing required secrets: {missing_secrets}")
        
        return {
            "email": secrets["linkedin_email"],
            "password": secrets["linkedin_password"],
            "work_preferences": work_preferences
        }
        
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise

def get_search_parameters() -> Dict[str, Any]:
    """Get job search parameters from user input or configuration"""
    # You can customize these parameters based on your needs
    search_params = {
        "keywords": "Software Engineer",
        "location": "Remote",
        "experience_level": "entry",  # internship, entry, associate, mid_senior_level, director, executive
        "job_type": "full_time"  # full_time, part_time, contract, temporary, internship, volunteer
    }
    
    # Interactive parameter selection (optional)
    print("\n=== LinkedIn Job Search Configuration ===")
    print("Current search parameters:")
    for key, value in search_params.items():
        print(f"  {key}: {value}")
    
    modify = input("\nWould you like to modify these parameters? (y/n): ").lower().strip()
    
    if modify == 'y':
        search_params["keywords"] = input("Enter job keywords (e.g., 'Software Engineer'): ").strip() or search_params["keywords"]
        search_params["location"] = input("Enter location (e.g., 'Remote', 'New York'): ").strip() or search_params["location"]
        
        print("\nExperience levels: internship, entry, associate, mid_senior_level, director, executive")
        experience = input("Enter experience level: ").strip()
        if experience:
            search_params["experience_level"] = experience
            
        print("\nJob types: full_time, part_time, contract, temporary, internship, volunteer")
        job_type = input("Enter job type: ").strip()
        if job_type:
            search_params["job_type"] = job_type
    
    return search_params

def run_linkedin_bot():
    """Main function to run the LinkedIn job application bot"""
    try:
        logger.info("Starting LinkedIn Job Application Bot")
        
        # Load configuration
        config = load_configuration()
        
        # Get search parameters
        search_params = get_search_parameters()
        
        # Initialize the bot
        bot = LinkedInBot(
            email=config["email"],
            password=config["password"],
            headless=False  # Set to True for headless mode
        )
        
        # Start the bot
        bot.start_driver()
        
        # Login to LinkedIn
        if not bot.login():
            logger.error("Failed to login to LinkedIn")
            return
        
        # Search for jobs
        jobs = bot.search_jobs(
            keywords=search_params["keywords"],
            location=search_params["location"],
            experience_level=search_params["experience_level"],
            job_type=search_params["job_type"]
        )
        
        if not jobs:
            logger.warning("No jobs found matching your criteria")
            return
        
        # Apply to jobs
        logger.info(f"Found {len(jobs)} jobs. Starting application process...")
        
        applied_count = 0
        failed_count = 0
        
        for i, job in enumerate(jobs):
            try:
                logger.info(f"Processing job {i+1}/{len(jobs)}: {job.get('title', 'Unknown')}")
                
                # Apply to job (this would use your existing resume generation logic)
                success = bot.apply_to_job(job)
                
                if success:
                    applied_count += 1
                    logger.info(f"Successfully applied to: {job.get('title', 'Unknown')}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to apply to: {job.get('title', 'Unknown')}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error applying to job {job.get('title', 'Unknown')}: {str(e)}")
                continue
        
        # Summary
        logger.info(f"\n=== Application Summary ===")
        logger.info(f"Total jobs found: {len(jobs)}")
        logger.info(f"Successfully applied: {applied_count}")
        logger.info(f"Failed applications: {failed_count}")
        logger.info(f"Success rate: {(applied_count/len(jobs)*100):.1f}%")
        
        return {
            "total_found": len(jobs),
            "applied": applied_count,
            "failed": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error running LinkedIn bot: {str(e)}")
        logger.debug(traceback.format_exc())
        return None
    
    finally:
        # Clean up
        if 'bot' in locals() and bot.driver:
            bot.driver.quit()
            logger.info("Browser closed")

def main():
    """Entry point for the script"""
    try:
        # Check if required files exist
        required_files = [
            "data_folder/secrets.yaml",
            "data_folder/work_preferences.yaml",
            "data_folder/plain_text_resume.yaml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            logger.error("Please ensure all configuration files are present before running the bot.")
            return
        
        # Run the bot
        results = run_linkedin_bot()
        
        if results:
            print(f"\n✅ Bot completed successfully!")
            print(f"Applied to {results['applied']} out of {results['total_found']} jobs")
        else:
            print("\n❌ Bot failed to complete")
            
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        print("\n⚠️  Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
