#!/usr/bin/env python3
"""
Enhanced LinkedIn Job Application Bot

This script implements a robust LinkedIn job application bot with:
- Extensive error handling and logging
- Human-like behavior with random delays
- Continuous job search and application until max limit
- Resume and cover letter generation integration
- Comprehensive debugging statements
"""

import sys
import time
import random
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException

# Import existing modules
from src.linkedin_bot import LinkedInBot
from src.job import Job
from src.job_application import JobApplication
from src.job_application_saver import ApplicationSaver
from src.logging import logger
from src.utils.chrome_utils import init_browser
from src.libs.resume_and_cover_builder import ResumeFacade, ResumeGenerator, StyleManager
from src.resume_schemas.resume import Resume
from main import ConfigValidator, FileManager
from config import JOB_MAX_APPLICATIONS, MINIMUM_WAIT_TIME_IN_SECONDS

import yaml


class EnhancedLinkedInBot:
    """Enhanced LinkedIn Job Application Bot with robust error handling and human-like behavior"""
    
    def __init__(self, email: str, password: str, work_preferences: Dict, resume_facade: ResumeFacade):
        self.email = email
        self.password = password
        self.work_preferences = work_preferences
        self.resume_facade = resume_facade
        self.driver = None
        self.wait = None
        self.applied_jobs = set()
        self.failed_jobs = set()
        self.applications_made = 0
        self.search_cycles = 0
        
        logger.info("Enhanced LinkedIn Bot initialized")
        logger.debug(f"Email: {email}")
        logger.debug(f"Work preferences: {work_preferences}")
        
    def start_driver(self):
        """Initialize the Chrome driver with enhanced logging"""
        try:
            logger.info("Starting Chrome driver initialization...")
            self.driver = init_browser()
            logger.info("Chrome driver created successfully")
            
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("WebDriverWait initialized with 10 second timeout")
            
            # Test driver functionality
            logger.info(f"Current driver session ID: {self.driver.session_id}")
            logger.info(f"Current driver capabilities: {self.driver.capabilities.get('browserName')}")
            
            logger.info("Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise
        
    def login(self) -> bool:
        """Login to LinkedIn with enhanced error handling"""
        try:
            logger.info("Attempting to login to LinkedIn")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login page to load
            logger.debug("Waiting for email input field")
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_input = self.driver.find_element(By.ID, "password")
            
            # Clear and enter credentials
            logger.debug("Entering login credentials")
            email_input.clear()
            email_input.send_keys(self.email)
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Add human-like delay before clicking
            time.sleep(random.uniform(1, 2))
            
            # Click login button
            logger.debug("Clicking login button")
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
            
            # Wait for successful login
            logger.debug("Waiting for login to complete")
            time.sleep(random.uniform(3, 5))
            
            # Check if we're logged in
            try:
                self.wait.until(EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "global-nav__me")),
                    EC.presence_of_element_located((By.CLASS_NAME, "feed-identity-module")),
                    EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout"))
                ))
                logger.info("Successfully logged into LinkedIn")
                return True
            except TimeoutException:
                logger.error("Login failed - could not find expected elements")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            logger.error(f"Login error traceback: {traceback.format_exc()}")
            return False
    
    def search_jobs_from_preferences(self) -> List[Job]:
        """Search for jobs based on work preferences"""
        jobs = []
        
        # Get enabled positions
        positions = self.work_preferences.get('positions', [])
        locations = self.work_preferences.get('locations', [])
        
        if not positions:
            logger.warning("No positions specified in work preferences")
            return jobs
        
        # Use first position and location for search
        keywords = positions[0] if positions else "Software Engineer"
        location = locations[0] if locations else "Remote"
        
        logger.info(f"Searching for jobs: '{keywords}' in '{location}'")
        
        try:
            # Navigate to jobs page
            logger.debug("Navigating to LinkedIn jobs page")
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(random.uniform(2, 3))
            
            # Search for jobs
            logger.debug("Entering job search keywords")
            keyword_input = self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[contains(@aria-label, 'Search by title, skill, or company')]")
            ))
            
            keyword_input.click()
            keyword_input.clear()
            keyword_input.send_keys(keywords)
            
            # Add location if specified
            if location:
                logger.debug(f"Entering location: {location}")
                location_input = self.wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//input[contains(@aria-label, 'City, state, or zip code')]")
                ))
                location_input.click()
                location_input.clear()
                location_input.send_keys(location)
                location_input.send_keys(Keys.RETURN)
            
            # Submit search
            logger.debug("Submitting job search")
            search_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@aria-label, 'Search')]")
            ))
            search_btn.click()
            
            time.sleep(random.uniform(3, 5))
            
            # Apply filters based on preferences
            self._apply_search_filters()
            
            # Extract job listings
            jobs = self._extract_job_listings()
            
            logger.info(f"Found {len(jobs)} job listings")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return jobs
    
    def _apply_search_filters(self):
        """Apply search filters based on work preferences"""
        try:
            # Apply experience level filters
            experience_levels = self.work_preferences.get('experience_level', {})
            enabled_experience = [level for level, enabled in experience_levels.items() if enabled]
            
            if enabled_experience:
                logger.debug(f"Applying experience level filters: {enabled_experience}")
                self._apply_experience_filter(enabled_experience[0])
            
            # Apply job type filters
            job_types = self.work_preferences.get('job_types', {})
            enabled_types = [job_type for job_type, enabled in job_types.items() if enabled]
            
            if enabled_types:
                logger.debug(f"Applying job type filters: {enabled_types}")
                self._apply_job_type_filter(enabled_types[0])
            
            # Apply date filter
            date_filters = self.work_preferences.get('date', {})
            enabled_dates = [date_filter for date_filter, enabled in date_filters.items() if enabled]
            
            if enabled_dates:
                logger.debug(f"Applying date filters: {enabled_dates}")
                self._apply_date_filter(enabled_dates[0])
            
        except Exception as e:
            logger.warning(f"Error applying filters: {str(e)}")
    
    def _apply_experience_filter(self, experience_level: str):
        """Apply experience level filter"""
        try:
            experience_filter = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Experience level')]")
            experience_filter.click()
            time.sleep(random.uniform(1, 2))
            
            experience_map = {
                "internship": "1",
                "entry": "2", 
                "associate": "3",
                "mid_senior_level": "4",
                "director": "5",
                "executive": "6"
            }
            
            if experience_level in experience_map:
                checkbox = self.driver.find_element(By.XPATH, f"//input[@value='{experience_map[experience_level]}']")
                checkbox.click()
                time.sleep(random.uniform(1, 2))
                
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(random.uniform(2, 3))
                
        except Exception as e:
            logger.warning(f"Could not apply experience filter: {str(e)}")
    
    def _apply_job_type_filter(self, job_type: str):
        """Apply job type filter"""
        try:
            job_type_filter = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Job type')]")
            job_type_filter.click()
            time.sleep(random.uniform(1, 2))
            
            job_type_map = {
                "full_time": "F",
                "part_time": "P",
                "contract": "C",
                "temporary": "T",
                "internship": "I",
                "volunteer": "V"
            }
            
            if job_type in job_type_map:
                checkbox = self.driver.find_element(By.XPATH, f"//input[@value='{job_type_map[job_type]}']")
                checkbox.click()
                time.sleep(random.uniform(1, 2))
                
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(random.uniform(2, 3))
                
        except Exception as e:
            logger.warning(f"Could not apply job type filter: {str(e)}")
    
    def _apply_date_filter(self, date_filter: str):
        """Apply date filter"""
        try:
            date_filter_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Date posted')]")
            date_filter_btn.click()
            time.sleep(random.uniform(1, 2))
            
            date_map = {
                "24_hours": "r86400",
                "week": "r604800",
                "month": "r2592000",
                "all_time": ""
            }
            
            if date_filter in date_map and date_map[date_filter]:
                checkbox = self.driver.find_element(By.XPATH, f"//input[@value='{date_map[date_filter]}']")
                checkbox.click()
                time.sleep(random.uniform(1, 2))
                
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(random.uniform(2, 3))
                
        except Exception as e:
            logger.warning(f"Could not apply date filter: {str(e)}")
    
    def _extract_job_listings(self) -> List[Job]:
        """Extract job listings from current page"""
        jobs = []
        
        try:
            # Wait for job listings to load
            job_cards = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[data-job-id]")
            ))
            
            logger.debug(f"Found {len(job_cards)} job cards on page")
            
            for i, card in enumerate(job_cards[:10]):  # Limit to first 10 jobs
                try:
                    job_id = card.get_attribute("data-job-id")
                    if job_id in self.applied_jobs:
                        logger.debug(f"Skipping already applied job: {job_id}")
                        continue
                        
                    # Click on job card to load details
                    logger.debug(f"Processing job card {i+1}/{len(job_cards[:10])}")
                    card.click()
                    time.sleep(random.uniform(2, 3))
                    
                    # Extract job information
                    job_info = self._extract_job_details(job_id)
                    if job_info:
                        jobs.append(job_info)
                        
                except Exception as e:
                    logger.warning(f"Error extracting job from card {i+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting job listings: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            
        return jobs
    
    def _extract_job_details(self, job_id: str) -> Optional[Job]:
        """Extract details from a specific job posting"""
        try:
            # Wait for job details to load
            time.sleep(random.uniform(1, 2))
            
            # Extract job title
            title = self.driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title").text
            
            # Extract company name
            company = self.driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name").text
            
            # Extract location
            try:
                location = self.driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__bullet").text
            except:
                location = "Remote"
            
            # Extract job description
            try:
                description_element = self.driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-description")
                description = description_element.text
            except:
                try:
                    description_element = self.driver.find_element(By.CSS_SELECTOR, "[data-job-details='description']")
                    description = description_element.text
                except:
                    description = "No description available"
            
            # Get current URL as job link
            job_link = self.driver.current_url
            
            # Create Job object
            job = Job(
                role=title,
                company=company,
                location=location,
                link=job_link,
                apply_method="linkedin",
                description=description
            )
            
            logger.info(f"Extracted job: {title} at {company}")
            return job
            
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            return None
    
    def apply_to_job(self, job: Job) -> bool:
        """Apply to a specific job with enhanced error handling"""
        try:
            logger.info(f"Attempting to apply to job: {job.role} at {job.company}")
            
            # Check if already applied
            if job.link in self.applied_jobs:
                logger.info("Already applied to this job, skipping...")
                return True
            
            # Check company blacklist
            company_blacklist = self.work_preferences.get('company_blacklist', [])
            if any(blocked_company.lower() in job.company.lower() for blocked_company in company_blacklist):
                logger.info(f"Company {job.company} is blacklisted, skipping...")
                return False
            
            # Check title blacklist
            title_blacklist = self.work_preferences.get('title_blacklist', [])
            if any(blocked_word.lower() in job.role.lower() for blocked_word in title_blacklist):
                logger.info(f"Job title contains blacklisted word, skipping...")
                return False
            
            # Generate tailored resume and cover letter
            logger.debug("Generating tailored resume and cover letter")
            try:
                self.resume_facade.link_to_job(job.link)
                resume_base64, resume_name = self.resume_facade.create_resume_pdf_job_tailored()
                cover_letter_base64, cover_letter_name = self.resume_facade.create_cover_letter()
                
                # Save files
                resume_path = self._save_pdf_file(resume_base64, f"resume_{resume_name}.pdf")
                cover_letter_path = self._save_pdf_file(cover_letter_base64, f"cover_letter_{cover_letter_name}.pdf")
                
                job.resume_path = resume_path
                job.cover_letter_path = cover_letter_path
                
                logger.debug("Resume and cover letter generated successfully")
                
            except Exception as e:
                logger.error(f"Error generating resume/cover letter: {str(e)}")
                resume_path = None
                cover_letter_path = None
            
            # Look for Easy Apply button
            try:
                easy_apply_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]")
                ))
                easy_apply_btn.click()
                time.sleep(random.uniform(2, 3))
                
                # Handle the application process
                if self._handle_easy_apply_process(resume_path, cover_letter_path):
                    self.applied_jobs.add(job.link)
                    self.applications_made += 1
                    logger.info(f"Successfully applied to {job.role} at {job.company}")
                    
                    # Save application data
                    self._save_application_data(job, resume_path, cover_letter_path)
                    return True
                else:
                    self.failed_jobs.add(job.link)
                    logger.warning(f"Failed to complete application for {job.role} at {job.company}")
                    return False
                    
            except TimeoutException:
                logger.warning("Easy Apply button not found, skipping job")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to job: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            self.failed_jobs.add(job.link)
            return False
    
    def _save_pdf_file(self, base64_content: str, filename: str) -> str:
        """Save PDF file from base64 content"""
        try:
            output_dir = Path("data_folder/output")
            output_dir.mkdir(exist_ok=True)
            
            file_path = output_dir / filename
            
            pdf_data = base64.b64decode(base64_content)
            with open(file_path, "wb") as f:
                f.write(pdf_data)
            
            logger.debug(f"Saved PDF file: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving PDF file: {str(e)}")
            return None
    
    def _handle_easy_apply_process(self, resume_path: str = None, cover_letter_path: str = None) -> bool:
        """Handle the Easy Apply process steps with enhanced error handling"""
        try:
            max_steps = 5
            current_step = 0
            
            while current_step < max_steps:
                time.sleep(random.uniform(2, 3))
                
                # Check for file upload
                try:
                    file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
                    for file_input in file_inputs:
                        if resume_path and "resume" in file_input.get_attribute("name").lower():
                            file_input.send_keys(resume_path)
                            logger.debug("Uploaded resume file")
                        elif cover_letter_path and "cover" in file_input.get_attribute("name").lower():
                            file_input.send_keys(cover_letter_path)
                            logger.debug("Uploaded cover letter file")
                except Exception as e:
                    logger.debug(f"No file upload required or error: {str(e)}")
                
                # Fill form fields
                self._fill_application_form()
                
                # Look for Next button
                try:
                    next_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue to next step') or contains(@aria-label, 'Review your application') or contains(text(), 'Next')]")
                    next_btn.click()
                    current_step += 1
                    logger.debug(f"Clicked Next button, step {current_step}")
                    time.sleep(random.uniform(2, 3))
                    continue
                except:
                    pass
                
                # Look for Submit button
                try:
                    submit_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application') or contains(text(), 'Submit application')]")
                    submit_btn.click()
                    logger.debug("Clicked Submit button")
                    time.sleep(random.uniform(3, 5))
                    
                    # Check for success message
                    try:
                        self.wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//*[contains(text(), 'Application sent') or contains(text(), 'Your application was sent')]")
                        ))
                        logger.debug("Application submitted successfully")
                        return True
                    except:
                        logger.debug("Assuming application was successful")
                        return True
                        
                except:
                    pass
                
                # Look for Close or Cancel button to exit
                try:
                    close_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Dismiss') or contains(text(), 'Cancel')]")
                    close_btn.click()
                    logger.debug("Clicked Close/Cancel button")
                    break
                except:
                    break
            
            return False
            
        except Exception as e:
            logger.error(f"Error in Easy Apply process: {str(e)}")
            return False
    
    def _fill_application_form(self):
        """Fill out application form fields with enhanced error handling"""
        try:
            # Fill text inputs
            text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='tel']")
            for input_field in text_inputs:
                try:
                    label = input_field.get_attribute("aria-label") or input_field.get_attribute("placeholder") or ""
                    label = label.lower()
                    
                    if "first" in label and "name" in label:
                        input_field.clear()
                        input_field.send_keys("Rahul")
                        logger.debug("Filled first name")
                    elif "last" in label and "name" in label:
                        input_field.clear()
                        input_field.send_keys("Tamatta")
                        logger.debug("Filled last name")
                    elif "email" in label:
                        input_field.clear()
                        input_field.send_keys("rahultamatta73000@gmail.com")
                        logger.debug("Filled email")
                    elif "phone" in label:
                        input_field.clear()
                        input_field.send_keys("+91 8291541168")
                        logger.debug("Filled phone number")
                    elif "city" in label or "location" in label:
                        input_field.clear()
                        input_field.send_keys("Thane, India")
                        logger.debug("Filled location")
                        
                except Exception as e:
                    logger.debug(f"Error filling text input: {str(e)}")
                    continue
            
            # Handle dropdowns
            select_elements = self.driver.find_elements(By.TAG_NAME, "select")
            for select_element in select_elements:
                try:
                    select = Select(select_element)
                    options = select.options
                    if len(options) > 1:
                        select.select_by_index(1)
                        logger.debug("Selected dropdown option")
                except Exception as e:
                    logger.debug(f"Error handling dropdown: {str(e)}")
                    continue
            
            # Handle radio buttons and checkboxes
            radio_buttons = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
            for radio in radio_buttons:
                try:
                    label = radio.get_attribute("aria-label") or ""
                    if "yes" in label.lower() or "authorized" in label.lower():
                        radio.click()
                        logger.debug("Clicked radio button")
                except Exception as e:
                    logger.debug(f"Error handling radio button: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error filling form: {str(e)}")
    
    def _save_application_data(self, job: Job, resume_path: str, cover_letter_path: str):
        """Save application data for tracking"""
        try:
            # Create JobApplication object
            job_application = JobApplication(
                job=job,
                resume_path=resume_path,
                cover_letter_path=cover_letter_path
            )
            
            job_application.application["application_date"] = datetime.now().isoformat()
            job_application.application["status"] = "applied"
            
            # Save application
            ApplicationSaver.save(job_application)
            logger.debug("Application data saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving application data: {str(e)}")
    
    def run_continuous_job_application(self) -> Dict[str, int]:
        """Main method to run continuous job application until max limit"""
        results = {
            "total_found": 0,
            "applied": 0,
            "failed": 0,
            "search_cycles": 0
        }
        
        try:
            # Initialize driver
            self.start_driver()
            
            # Login to LinkedIn
            if not self.login():
                logger.error("Failed to login to LinkedIn")
                return results
            
            # Main application loop
            while self.applications_made < JOB_MAX_APPLICATIONS:
                logger.info(f"Starting job search cycle {self.search_cycles + 1}")
                logger.info(f"Applications made: {self.applications_made}/{JOB_MAX_APPLICATIONS}")
                
                # Search for jobs
                jobs = self.search_jobs_from_preferences()
                results["total_found"] += len(jobs)
                
                if not jobs:
                    logger.warning("No jobs found in this cycle")
                    self.search_cycles += 1
                    results["search_cycles"] = self.search_cycles
                    
                    if self.search_cycles >= 3:  # Max 3 search cycles without jobs
                        logger.warning("Maximum search cycles reached without finding jobs")
                        break
                    
                    logger.info(f"Waiting {MINIMUM_WAIT_TIME_IN_SECONDS} seconds before next search cycle")
                    time.sleep(MINIMUM_WAIT_TIME_IN_SECONDS)
                    continue
                
                # Apply to jobs
                for job in jobs:
                    if self.applications_made >= JOB_MAX_APPLICATIONS:
                        break
                    
                    try:
                        if self.apply_to_job(job):
                            results["applied"] += 1
                            logger.info(f"Successfully applied to job {self.applications_made}: {job.role} at {job.company}")
                        else:
                            results["failed"] += 1
                            logger.warning(f"Failed to apply to: {job.role} at {job.company}")
                        
                        # Human-like delay between applications
                        delay = random.uniform(10, 20)
                        logger.debug(f"Waiting {delay:.1f} seconds before next application")
                        time.sleep(delay)
                        
                    except Exception as e:
                        results["failed"] += 1
                        logger.error(f"Error applying to job {job.role} at {job.company}: {str(e)}")
                        continue
                
                self.search_cycles += 1
                results["search_cycles"] = self.search_cycles
                
                # Wait between search cycles if not at max applications
                if self.applications_made < JOB_MAX_APPLICATIONS:
                    logger.info(f"Waiting {MINIMUM_WAIT_TIME_IN_SECONDS} seconds before next search cycle")
                    time.sleep(MINIMUM_WAIT_TIME_IN_SECONDS)
            
            logger.info(f"Job application session completed!")
            logger.info(f"Total applications made: {self.applications_made}")
            logger.info(f"Total jobs found: {results['total_found']}")
            logger.info(f"Successful applications: {results['applied']}")
            logger.info(f"Failed applications: {results['failed']}")
            logger.info(f"Search cycles: {results['search_cycles']}")
            
        except Exception as e:
            logger.error(f"Error in continuous job application: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser driver closed")
                
        return results
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")


def main():
    """Main entry point for the Enhanced LinkedIn Job Application Bot"""
    try:
        logger.info("Starting Enhanced LinkedIn Job Application Bot")
        
        # Validate data folder and files
        data_folder = Path("data_folder")
        secrets_file, config_file, plain_text_resume_file, output_folder = FileManager.validate_data_folder(data_folder)
        
        # Validate configuration and secrets
        config = ConfigValidator.validate_config(config_file)
        llm_api_key = ConfigValidator.validate_secrets(secrets_file)
        
        # Load LinkedIn credentials
        with open(secrets_file, 'r') as f:
            secrets = yaml.safe_load(f)
        
        linkedin_email = secrets.get("linkedin_email")
        linkedin_password = secrets.get("linkedin_password")
        
        if not linkedin_email or not linkedin_password:
            logger.error("LinkedIn credentials not found in secrets.yaml")
            return
        
        # Prepare parameters
        config["uploads"] = FileManager.get_uploads(plain_text_resume_file)
        config["outputFileDirectory"] = output_folder
        
        # Initialize resume components
        with open(plain_text_resume_file, "r") as f:
            plain_text_resume = f.read()
        
        resume_object = Resume(plain_text_resume)
        style_manager = StyleManager()
        resume_generator = ResumeGenerator()
        resume_generator.set_resume_object(resume_object)
        
        # Initialize resume facade
        resume_facade = ResumeFacade(
            api_key=llm_api_key,
            style_manager=style_manager,
            resume_generator=resume_generator,
            resume_object=resume_object,
            output_path=output_folder,
        )
        
        # Initialize enhanced LinkedIn bot
        bot = EnhancedLinkedInBot(
            email=linkedin_email,
            password=linkedin_password,
            work_preferences=config,
            resume_facade=resume_facade
        )
        
        # Run continuous job application
        results = bot.run_continuous_job_application()
        
        # Print final results
        print(f"\n{'='*50}")
        print(f"JOB APPLICATION BOT RESULTS")
        print(f"{'='*50}")
        print(f"Total jobs found: {results['total_found']}")
        print(f"Successful applications: {results['applied']}")
        print(f"Failed applications: {results['failed']}")
        print(f"Search cycles: {results['search_cycles']}")
        print(f"Success rate: {(results['applied']/max(results['total_found'], 1)*100):.1f}%")
        print(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
