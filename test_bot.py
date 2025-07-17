#!/usr/bin/env python3
"""
Test script for the Enhanced LinkedIn Job Application Bot

This script performs basic validation tests to ensure the bot can run properly.
"""

import sys
from pathlib import Path
import traceback

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test core imports
        from src.logging import logger
        from src.job import Job
        from src.job_application import JobApplication
        from src.job_application_saver import ApplicationSaver
        from src.utils.chrome_utils import init_browser
        from src.libs.resume_and_cover_builder import ResumeFacade, ResumeGenerator, StyleManager
        from src.resume_schemas.resume import Resume
        from main import ConfigValidator, FileManager
        
        print("✅ All core imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_configuration():
    """Test that configuration files exist and are valid"""
    print("🔍 Testing configuration...")
    
    try:
        # Check required files exist
        required_files = [
            "data_folder/secrets.yaml",
            "data_folder/work_preferences.yaml", 
            "data_folder/plain_text_resume.yaml"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Missing file: {file_path}")
                return False
        
        # Test configuration validation
        data_folder = Path("data_folder")
        secrets_file, config_file, plain_text_resume_file, output_folder = FileManager.validate_data_folder(data_folder)
        
        config = ConfigValidator.validate_config(config_file)
        llm_api_key = ConfigValidator.validate_secrets(secrets_file)
        
        # Check LinkedIn credentials
        import yaml
        with open(secrets_file, 'r') as f:
            secrets = yaml.safe_load(f)
        
        if not secrets.get("linkedin_email"):
            print("❌ Missing linkedin_email in secrets.yaml")
            return False
            
        if not secrets.get("linkedin_password"):
            print("❌ Missing linkedin_password in secrets.yaml")
            return False
        
        print("✅ Configuration validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False

def test_resume_components():
    """Test that resume generation components work"""
    print("🔍 Testing resume components...")
    
    try:
        # Initialize resume components
        plain_text_resume_file = Path("data_folder/plain_text_resume.yaml")
        
        with open(plain_text_resume_file, "r") as f:
            plain_text_resume = f.read()
        
        resume_object = Resume(plain_text_resume)
        style_manager = StyleManager()
        resume_generator = ResumeGenerator()
        resume_generator.set_resume_object(resume_object)
        
        print("✅ Resume components initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Resume components error: {str(e)}")
        return False

def test_job_objects():
    """Test that job-related objects can be created"""
    print("🔍 Testing job objects...")
    
    try:
        # Create test job
        job = Job(
            role="Software Engineer",
            company="TestCorp",
            location="Remote",
            link="https://linkedin.com/jobs/test",
            apply_method="linkedin",
            description="Test job description"
        )
        
        # Create job application
        job_application = JobApplication(
            job=job,
            resume_path="test_resume.pdf",
            cover_letter_path="test_cover.pdf"
        )
        
        print("✅ Job objects created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Job objects error: {str(e)}")
        return False

def test_logging():
    """Test that logging is working"""
    print("🔍 Testing logging...")
    
    try:
        from src.logging import logger
        
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        logger.error("Error message test")
        
        print("✅ Logging working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Logging error: {str(e)}")
        return False

def test_chrome_driver():
    """Test that Chrome driver can be initialized"""
    print("🔍 Testing Chrome driver...")
    
    try:
        from src.utils.chrome_utils import init_browser
        
        # Try to initialize browser (but don't actually open it)
        print("   Attempting to initialize Chrome driver...")
        driver = init_browser()
        
        if driver:
            print("   Chrome driver initialized successfully")
            driver.quit()
            print("   Chrome driver closed")
            print("✅ Chrome driver test successful")
            return True
        else:
            print("❌ Chrome driver initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Chrome driver error: {str(e)}")
        return False

def test_bot_import():
    """Test that the enhanced bot can be imported"""
    print("🔍 Testing bot import...")
    
    try:
        from linkedin_job_application_bot import EnhancedLinkedInBot
        print("✅ Enhanced LinkedIn bot imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Bot import error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Starting Enhanced LinkedIn Job Application Bot Tests\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Resume Components Test", test_resume_components),
        ("Job Objects Test", test_job_objects),
        ("Logging Test", test_logging),
        ("Chrome Driver Test", test_chrome_driver),
        ("Bot Import Test", test_bot_import)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            failed += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Success rate: {(passed/(passed+failed)*100):.1f}%")
    print(f"{'='*60}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The bot is ready to run.")
        print("   You can now run: python main.py")
        print("   And select 'Run LinkedIn Job Application Bot'")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues before running the bot.")
        print("   Check the error messages above for troubleshooting.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
