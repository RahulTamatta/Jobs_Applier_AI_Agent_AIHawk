import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.job import Job
from src.logging import logger
from config import JOB_MAX_APPLICATIONS, MINIMUM_WAIT_TIME_IN_SECONDS

# Function to search for jobs (dummy implementation for demonstration)
def search_jobs(criteria: dict) -> list[Job]:
    logger.info("Starting job search with criteria: %s", criteria)
    # Simulate job search (replace with real logic, e.g., scraping a job board)
    jobs = [
        Job(role="Software Engineer", company="TechCorp", link="http://example.com/job1", description="Requires Python"),
        Job(role="Data Analyst", company="DataInc", link="http://example.com/job2", description="Requires SQL")
    ]
    logger.info("Found %d jobs", len(jobs))
    return jobs

# Function to apply for jobs (dummy implementation for demonstration)
def apply_to_job(job: Job, driver, resume_facade):
    logger.info("Applying to job: %s at %s", job.role, job.company)
    try:
        driver.get(job.link)
        logger.debug("Navigated to job URL: %s", job.link)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.debug("Page loaded successfully")
        
        # Simulate form interaction (replace with real logic)
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "apply"))  # Adjust selector
        )
        apply_button.click()
        logger.debug("Clicked apply button")
        
        # Simulate human-like delay
        time.sleep(random.uniform(1, 3))
        logger.debug("Application submitted with human-like delay")
        
    except Exception as e:
        logger.error("Error applying to job %s: %s", job.role, str(e))
        raise

# Main bot logic
def job_application_bot(driver, resume_facade, config):
    applications_made = 0
    while applications_made < JOB_MAX_APPLICATIONS:
        logger.info("Starting job search cycle. Applications made: %d/%d", 
                   applications_made, JOB_MAX_APPLICATIONS)
        # Search for jobs
        jobs = search_jobs(config)
        if not jobs:
            logger.warning("No jobs found. Waiting %d seconds before retrying...", 
                          MINIMUM_WAIT_TIME_IN_SECONDS)
            time.sleep(MINIMUM_WAIT_TIME_IN_SECONDS)
            continue

        # Apply to each job
        for job in jobs:
            if applications_made >= JOB_MAX_APPLICATIONS:
                break
            try:
                resume_facade.link_to_job(job.link)
                apply_to_job(job, driver, resume_facade)
                applications_made += 1
                logger.info("Successfully applied to job %d: %s at %s", 
                           applications_made, job.role, job.company)
                
                # Random delay to mimic human behavior
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error("Failed to apply to job %s at %s: %s", 
                            job.role, job.company, str(e))
                continue

        # Wait before next search cycle
        if applications_made < JOB_MAX_APPLICATIONS:
            logger.info("Waiting %d seconds before next search cycle", 
                       MINIMUM_WAIT_TIME_IN_SECONDS)
            time.sleep(MINIMUM_WAIT_TIME_IN_SECONDS)

    logger.info("Completed job applications. Total: %d", applications_made)
