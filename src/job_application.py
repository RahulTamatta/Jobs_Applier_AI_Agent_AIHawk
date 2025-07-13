"""
Job Application class for managing job application data.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from src.job import Job


@dataclass
class JobApplication:
    """
    Represents a job application with all necessary information.
    """
    job: Job
    application: Dict[str, Any] = field(default_factory=dict)
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    
    def __post_init__(self):
        """Initialize application data structure if empty."""
        if not self.application:
            self.application = {
                "job_id": self.job.link,
                "company": self.job.company,
                "position": self.job.role,
                "location": self.job.location,
                "apply_method": self.job.apply_method,
                "application_date": None,
                "status": "pending",
                "questions_and_answers": {},
                "additional_info": {}
            }
    
    def add_question_answer(self, question: str, answer: str):
        """Add a question-answer pair to the application."""
        self.application["questions_and_answers"][question] = answer
    
    def set_status(self, status: str):
        """Set the application status."""
        self.application["status"] = status
    
    def add_additional_info(self, key: str, value: Any):
        """Add additional information to the application."""
        self.application["additional_info"][key] = value
