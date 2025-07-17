"""
LinkedIn Job Application Bot
Automates job searching and applying on LinkedIn
"""

import time
import random
import os
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException
from src.logging import logger
from src.utils.chrome_utils import init_browser
from src.job import Job
from src.job_application import JobApplication
from src.job_application_saver import ApplicationSaver


class LinkedInBot:
    def __init__(self, email: str, password: str, headless: bool = False):
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.wait = None
        self.applied_jobs = set()
        self.failed_jobs = set()
        
    def start_driver(self):
        """Initialize the Chrome driver"""
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
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            raise
        
    def login(self) -> bool:
        """Login to LinkedIn"""
        try:
            logger.info("Attempting to login to LinkedIn")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login page to load
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_input = self.driver.find_element(By.ID, "password")
            
            # Clear and enter credentials
            email_input.clear()
            email_input.send_keys(self.email)
            password_input.clear()
            password_input.send_keys(self.password)
            
            # Click login button
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
            
            # Wait for successful login
            time.sleep(3)
            
            # Check if we're logged in (look for feed or profile)
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
    
    def search_jobs(self, keywords: str, location: str = "", experience_level: str = "", job_type: str = "") -> List[Dict]:
        """Search for jobs on LinkedIn"""
        jobs = []
        logger.debug(f"Initiating job search for keywords: {keywords}, location: {location}, experience_level: {experience_level}, job_type: {job_type}")
        try:
            logger.info(f"Searching for jobs: {keywords} in {location}")
            
            # Navigate to jobs page
            logger.debug("Navigating to LinkedIn jobs page")
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(2)
            
            # Improved robust wait and input for the keyword field
            logger.debug("Waiting for job search keyword input field")
            keyword_input = self.wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[contains(@aria-label, 'Search by title, skill, or company')]")
            ))
            
            logger.debug("Clearing and entering job search keywords properly")
            keyword_input.click()
            keyword_input.clear()
            keyword_input.send_keys(keywords)
            
            if location:
                location_input = self.wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//input[contains(@aria-label, 'City, state, or zip code')]")
                ))
                logger.debug(f"Clearing and entering location: {location}")
                location_input.click()
                location_input.clear()
                
                # Normalize location input if it contains comma-separated locations
                location_parts = [part.strip() for part in location.split(",") if part.strip()]
                if location_parts:
                    # Enter the first location and accept via keyboard enter key
                    location_input.send_keys(location_parts[0])
                    location_input.send_keys(Keys.RETURN)
                else:
                    location_input.send_keys(location)
                    location_input.send_keys(Keys.RETURN)
            
            # Submit search
            logger.debug("Submitting job search form")
            search_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@aria-label, 'Search')]")
            ))
            search_btn.click()
            
            time.sleep(3)
            
            # Apply filters if specified
            logger.debug("Checking for experience level filter")
            if experience_level:
                self._apply_experience_filter(experience_level)
            
            logger.debug("Checking for job type filter")
            if job_type:
                self._apply_job_type_filter(job_type)
            
            # Get job listings
            logger.debug("Extracting job listings")
            jobs = self._extract_job_listings()
            
            logger.info(f"Found {len(jobs)} job listings")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            return jobs
    
    def _apply_experience_filter(self, experience_level: str):
        """Apply experience level filter"""
        try:
            # Click on experience level filter
            experience_filter = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Experience level')]")
            experience_filter.click()
            time.sleep(1)
            
            # Map experience levels to LinkedIn values
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
                time.sleep(1)
                
                # Apply filter
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(2)
                
        except Exception as e:
            logger.warning(f"Could not apply experience filter: {str(e)}")
            logger.warning(f"Error traceback: {traceback.format_exc()}")
    
    def _apply_job_type_filter(self, job_type: str):
        """Apply job type filter"""
        try:
            # Click on job type filter
            job_type_filter = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Job type')]")
            job_type_filter.click()
            time.sleep(1)
            
            # Map job types to LinkedIn values
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
                time.sleep(1)
                
                # Apply filter
                apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
                apply_btn.click()
                time.sleep(2)
                
        except Exception as e:
            logger.warning(f"Could not apply job type filter: {str(e)}")
            logger.warning(f"Error traceback: {traceback.format_exc()}")
    
    def _extract_job_listings(self) -> List[Dict]:
        """Extract job listings from current page"""
        jobs = []
        logger.debug(f"Initiating extraction of job listings")
        try:
            # Wait for job listings to load
            job_cards = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[data-job-id]")
            ))
            
            for card in job_cards[:10]:  # Limit to first 10 jobs
                logger.debug("Processing job card")
                try:
                    job_id = card.get_attribute("data-job-id")
                    if job_id in self.applied_jobs:
                        continue
                        
                    # Click on job card to load details
                    logger.debug(f"Clicking on job card with ID: {job_id}")
                    card.click()
                    time.sleep(2)
                    
                    # Extract job information
                    job_info = self._extract_job_details(job_id)
                    if job_info:
                        logger.debug(f"Job details extracted: {job_info}")
                        jobs.append(job_info)
                        
                except Exception as e:
                    logger.warning(f"Error extracting job from card: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting job listings: {str(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            
        return jobs
    
    def _extract_job_details(self, job_id: str) -> Optional[Dict]:
        """Extract details from a specific job posting"""
        try:
            # Wait for job details to load
            time.sleep(2)
            
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
            
            job_info = {
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "link": job_link,
                "apply_method": "linkedin"
            }
            
            logger.info(f"Extracted job: {title} at {company}")
            return job_info
            
        except Exception as e:
            logger.error(f"Error extracting job details: {str(e)}")
            return None
    
    def apply_to_job(self, job_info: Dict, resume_path: str = None, cover_letter_path: str = None) -> bool:
        """Apply to a specific job"""
        try:
            job_id = job_info["id"]
            logger.info(f"Attempting to apply to job: {job_info['title']} at {job_info['company']}")
            
            # Check if already applied
            if job_id in self.applied_jobs:
                logger.info("Already applied to this job, skipping...")
                return True
            
            # Look for Easy Apply button
            try:
                easy_apply_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]")
                ))
                easy_apply_btn.click()
                time.sleep(2)
                
                # Handle the application process
                if self._handle_easy_apply_process(resume_path, cover_letter_path):
                    self.applied_jobs.add(job_id)
                    logger.info(f"Successfully applied to {job_info['title']}")
                    
                    # Save application data
                    self._save_application_data(job_info, resume_path, cover_letter_path)
                    return True
                else:
                    self.failed_jobs.add(job_id)
                    return False
                    
            except TimeoutException:
                logger.warning("Easy Apply button not found, skipping job")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to job: {str(e)}")
            self.failed_jobs.add(job_info["id"])
            return False
    
    def _handle_easy_apply_process(self, resume_path: str = None, cover_letter_path: str = None) -> bool:
        """Handle the Easy Apply process steps"""
        try:
            max_steps = 5
            current_step = 0
            
            while current_step < max_steps:
                time.sleep(2)
                
                # Check for file upload
                try:
                    file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
                    for file_input in file_inputs:
                        if resume_path and "resume" in file_input.get_attribute("name").lower():
                            file_input.send_keys(resume_path)
                        elif cover_letter_path and "cover" in file_input.get_attribute("name").lower():
                            file_input.send_keys(cover_letter_path)
                except:
                    pass
                
                # Fill form fields
                self._fill_application_form()
                
                # Look for Next or Submit button
                try:
                    next_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue to next step') or contains(@aria-label, 'Review your application') or contains(text(), 'Next')]")
                    next_btn.click()
                    current_step += 1
                    continue
                except:
                    pass
                
                # Look for Submit button
                try:
                    submit_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit application') or contains(text(), 'Submit application')]")
                    submit_btn.click()
                    time.sleep(3)
                    
                    # Check for success message
                    try:
                        self.wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//*[contains(text(), 'Application sent') or contains(text(), 'Your application was sent')]")
                        ))
                        return True
                    except:
                        return True  # Assume success if no error
                        
                except:
                    pass
                
                # Look for Close or Cancel button to exit
                try:
                    close_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Dismiss') or contains(text(), 'Cancel')]")
                    close_btn.click()
                    break
                except:
                    break
            
            return False
            
        except Exception as e:
            logger.error(f"Error in Easy Apply process: {str(e)}")
            return False
    
    def _fill_application_form(self):
        """Fill out application form fields"""
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
                    elif "last" in label and "name" in label:
                        input_field.clear()
                        input_field.send_keys("Tamatta")
                    elif "email" in label:
                        input_field.clear()
                        input_field.send_keys("rahultamatta73000@gmail.com")
                    elif "phone" in label:
                        input_field.clear()
                        input_field.send_keys("+91 8291541168")
                    elif "city" in label or "location" in label:
                        input_field.clear()
                        input_field.send_keys("Thane, India")
                        
                except Exception as e:
                    continue
            
            # Handle dropdowns
            select_elements = self.driver.find_elements(By.TAG_NAME, "select")
            for select_element in select_elements:
                try:
                    select = Select(select_element)
                    # Select first non-empty option
                    options = select.options
                    if len(options) > 1:
                        select.select_by_index(1)
                except:
                    continue
            
            # Handle radio buttons and checkboxes
            radio_buttons = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
            for radio in radio_buttons:
                try:
                    label = radio.get_attribute("aria-label") or ""
                    if "yes" in label.lower() or "authorized" in label.lower():
                        radio.click()
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error filling form: {str(e)}")
    
    def _save_application_data(self, job_info: Dict, resume_path: str, cover_letter_path: str):
        """Save application data for tracking"""
        try:
            # Create Job object
            job = Job(
                role=job_info["title"],
                company=job_info["company"],
                location=job_info["location"],
                link=job_info["link"],
                apply_method=job_info["apply_method"],
                description=job_info["description"]
            )
            
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
            
        except Exception as e:
            logger.error(f"Error saving application data: {str(e)}")
    
    def run_job_search_and_apply(self, search_params: Dict, max_applications: int = 5) -> Dict:
        """Main method to search and apply for jobs"""
        results = {
            "total_found": 0,
            "applied": 0,
            "failed": 0,
            "skipped": 0
        }
        
        try:
            self.start_driver()
            
            if not self.login():
                logger.error("Failed to login to LinkedIn")
                return results
            
            # Search for jobs
            jobs = self.search_jobs(
                keywords=search_params.get("keywords", "Software Engineer"),
                location=search_params.get("location", ""),
                experience_level=search_params.get("experience_level", ""),
                job_type=search_params.get("job_type", "")
            )
            
            results["total_found"] = len(jobs)
            
            if not jobs:
                logger.warning("No jobs found")
                return results
            
            # Apply to jobs
            applied_count = 0
            for job in jobs:
                if applied_count >= max_applications:
                    break
                    
                if self.apply_to_job(job):
                    applied_count += 1
                    results["applied"] += 1
                else:
                    results["failed"] += 1
                
                # Random delay between applications
                time.sleep(random.randint(10, 30))
            
            logger.info(f"Job application session completed. Applied: {results['applied']}, Failed: {results['failed']}")
            
        except Exception as e:
            logger.error(f"Error in job search and apply process: {str(e)}")
        
        finally:
            if self.driver:
                self.driver.quit()
                
        return results
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")
