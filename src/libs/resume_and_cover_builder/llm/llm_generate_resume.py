"""
Create a class that generates a resume based on a resume and a resume template.
"""
# app/libs/resume_and_cover_builder/gpt_resume.py
import os
import textwrap
from src.libs.resume_and_cover_builder.utils import LoggerChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Configure log file
log_folder = 'log/resume/gpt_resume'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
log_path = Path(log_folder).resolve()
logger.add(log_path / "gpt_resume.log", rotation="1 day", compression="zip", retention="7 days", level="DEBUG")

class LLMResumer:
    def __init__(self, openai_api_key, strings):
        self.llm_cheap = LoggerChatModel(
            ChatOllama(
                model="gemma3:1b", base_url="http://localhost:11434", temperature=0.4
            )
        )
        self.strings = strings

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        """
        Preprocess the template string by removing leading whitespace and indentation.
        Args:
            template (str): The template string to preprocess.
        Returns:
            str: The preprocessed template string.
        """
        return textwrap.dedent(template)

    def set_resume(self, resume) -> None:
        """
        Set the resume object to be used for generating the resume.
        Args:
            resume (Resume): The resume object to be used.
        """
        self.resume = resume

    def generate_header(self, data = None) -> str:
        """
        Generate the header section of the resume.
        Args:
            data (dict): The personal information to use for generating the header.
        Returns:
            str: The generated header section.
        """
        header_prompt_template = self._preprocess_template_string(
            self.strings.prompt_header
        )
        prompt = ChatPromptTemplate.from_template(header_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        input_data = {
            "personal_information": self.resume.personal_information
        } if data is None else data
        output = chain.invoke(input_data)
        return output
    
    def generate_education_section(self, data = None) -> str:
        """
        Generate the education section of the resume.
        Args:
            data (dict): The education details to use for generating the education section.
        Returns:
            str: The generated education section.
        """
        logger.debug("Starting education section generation")

        education_prompt_template = self._preprocess_template_string(self.strings.prompt_education)
        logger.debug(f"Education template: {education_prompt_template}")

        prompt = ChatPromptTemplate.from_template(education_prompt_template)
        logger.debug(f"Prompt: {prompt}")
        
        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")
        
        input_data = {
            "education_details": self.resume.education_details
        } if data is None else data
        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Education section generation completed")
        return output

    def generate_work_experience_section(self, data = None) -> str:
        """
        Generate the work experience section of the resume.
        Args:
            data (dict): The work experience details to use for generating the work experience section.
        Returns:
            str: The generated work experience section.
        """
        logger.debug("Starting work experience section generation")

        work_experience_prompt_template = self._preprocess_template_string(self.strings.prompt_working_experience)
        logger.debug(f"Work experience template: {work_experience_prompt_template}")

        prompt = ChatPromptTemplate.from_template(work_experience_prompt_template)
        logger.debug(f"Prompt: {prompt}")
        
        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")
        
        input_data = {
            "experience_details": self.resume.experience_details
        } if data is None else data
        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Work experience section generation completed")
        return output

    def generate_projects_section(self, data = None) -> str:
        """
        Generate the side projects section of the resume.
        Args:
            data (dict): The side projects to use for generating the side projects section.
        Returns:
            str: The generated side projects section.
        """
        logger.debug("Starting side projects section generation")

        projects_prompt_template = self._preprocess_template_string(self.strings.prompt_projects)
        logger.debug(f"Side projects template: {projects_prompt_template}")

        prompt = ChatPromptTemplate.from_template(projects_prompt_template)
        logger.debug(f"Prompt: {prompt}")
        
        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")
        
        input_data = {
            "projects": self.resume.projects
        } if data is None else data
        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Side projects section generation completed")
        return output

    def generate_achievements_section(self, data = None) -> str:
        """
        Generate the achievements section of the resume.
        Args:
            data (dict): The achievements to use for generating the achievements section.
        Returns:
            str: The generated achievements section.
        """
        logger.debug("Starting achievements section generation")

        achievements_prompt_template = self._preprocess_template_string(self.strings.prompt_achievements)
        logger.debug(f"Achievements template: {achievements_prompt_template}")

        prompt = ChatPromptTemplate.from_template(achievements_prompt_template)
        logger.debug(f"Prompt: {prompt}")

        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")

        input_data = {
            "achievements": self.resume.achievements,
            "certifications": self.resume.certifications,
        } if data is None else data
        logger.debug(f"Input data for the chain: {input_data}")

        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Achievements section generation completed")
        return output

    def generate_certifications_section(self, data = None) -> str:
        """
        Generate the certifications section of the resume.
        Returns:
            str: The generated certifications section.
        """
        logger.debug("Starting Certifications section generation")

        certifications_prompt_template = self._preprocess_template_string(self.strings.prompt_certifications)
        logger.debug(f"Certifications template: {certifications_prompt_template}")

        prompt = ChatPromptTemplate.from_template(certifications_prompt_template)
        logger.debug(f"Prompt: {prompt}")

        chain = prompt | self.llm_cheap | StrOutputParser()
        logger.debug(f"Chain created: {chain}")

        input_data = {
            "certifications": self.resume.certifications
        } if data is None else data
        logger.debug(f"Input data for the chain: {input_data}")

        output = chain.invoke(input_data)
        logger.debug(f"Chain invocation result: {output}")

        logger.debug("Certifications section generation completed")
        return output
    
    def generate_additional_skills_section(self, data = None) -> str:
        """
        Generate the additional skills section of the resume.
        Returns:
            str: The generated additional skills section.
        """
        additional_skills_prompt_template = self._preprocess_template_string(self.strings.prompt_additional_skills)
        
        skills = set()
        if self.resume.experience_details:
            for exp in self.resume.experience_details:
                if exp.skills_acquired:
                    skills.update(exp.skills_acquired)

        if self.resume.education_details:
            for edu in self.resume.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())
        prompt = ChatPromptTemplate.from_template(additional_skills_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        input_data = {
            "languages": self.resume.languages,
            "interests": self.resume.interests,
            "skills": skills,
        } if data is None else data
        output = chain.invoke(input_data)
        
        return output

    def generate_fallback_html_resume(self) -> str:
        """Generate a fallback HTML resume when LLM fails"""
        logger.warning("Using fallback HTML generation due to LLM failure")
        
        personal_info = self.resume.personal_information
        education = self.resume.education_details[0] if self.resume.education_details else None
        experience = self.resume.experience_details[:3] if self.resume.experience_details else []
        projects = self.resume.projects[:2] if self.resume.projects else []
        achievements = self.resume.achievements[:3] if self.resume.achievements else []
        certifications = self.resume.certifications[:3] if self.resume.certifications else []
        languages = self.resume.languages if self.resume.languages else []
        
        # Build header
        header_html = f"""
        <header>
            <h1>{personal_info.name} {personal_info.surname}</h1>
            <div class="contact-info">
                <p><span>{personal_info.city}, {personal_info.country}</span></p>
                <p><span>{personal_info.phone_prefix} {personal_info.phone}</span></p>
                <p><span>{personal_info.email}</span></p>
                <p><a href="{personal_info.linkedin}">LinkedIn</a></p>
                <p><a href="{personal_info.github}">GitHub</a></p>
            </div>
        </header>"""
        
        # Build education
        education_html = ""
        if education:
            education_html = f"""
        <section id="education">
            <h2>Education</h2>
            <div class="entry">
                <div class="entry-header">
                    <span class="entry-name">{education.institution}</span>
                    <span class="entry-location">{personal_info.city}, {personal_info.country}</span>
                </div>
                <div class="entry-details">
                    <span class="entry-title">{education.education_level} in {education.field_of_study}</span>
                    <span class="entry-year">{education.start_date} – {education.year_of_completion}</span>
                </div>
            </div>
        </section>"""
        
        # Build work experience
        work_html = ""
        if experience:
            work_html = "<section id='work-experience'><h2>Work Experience</h2>"
            for exp in experience:
                responsibilities = []
                if hasattr(exp, 'key_responsibilities') and exp.key_responsibilities:
                    for resp in exp.key_responsibilities:
                        if isinstance(resp, dict):
                            responsibilities.extend(resp.values())
                        else:
                            responsibilities.append(str(resp))
                
                resp_html = "\n".join([f"<li>{resp}</li>" for resp in responsibilities[:3]])
                
                work_html += f"""
            <div class="entry">
                <div class="entry-header">
                    <span class="entry-name">{exp.company}</span>
                    <span class="entry-location">{exp.location}</span>
                </div>
                <div class="entry-details">
                    <span class="entry-title">{exp.position}</span>
                    <span class="entry-year">{exp.employment_period}</span>
                </div>
                <ul class="compact-list">
                    {resp_html}
                </ul>
            </div>"""
            work_html += "</section>"
        
        # Build skills
        skills_html = ""
        if languages or any([experience, education]):
            skills_html = """
        <section id="skills-languages">
            <h2>Skills & Languages</h2>
            <div class="two-column">
                <ul class="compact-list">
                    <li>Flutter Development</li>
                    <li>React.js</li>
                    <li>Node.js</li>
                    <li>MongoDB</li>
                    <li>Full-Stack Development</li>
                </ul>
                <ul class="compact-list">
                    <li>Mobile App Development</li>
                    <li>MERN Stack</li>
                    <li>UI/UX Design</li>
                    <li>Database Systems</li>"""
            if languages:
                lang_text = ", ".join([f"{lang.language} ({lang.proficiency})" for lang in languages])
                skills_html += f"<li><strong>Languages:</strong> {lang_text}</li>"
            skills_html += """
                </ul>
            </div>
        </section>"""
        
        full_resume = f"""
    <body>
        {header_html}
        <main>
            {education_html}
            {work_html}
            {skills_html}
        </main>
    </body>"""
        
        return full_resume

    def generate_html_resume(self) -> str:
        """
        Generate the full HTML resume based on the resume object.
        Returns:
            str: The generated HTML resume.
        """
        try:
            def header_fn():
                if self.resume.personal_information:
                    return self.generate_header()
                return ""

            def education_fn():
                if self.resume.education_details:
                    return self.generate_education_section()
                return ""

            def work_experience_fn():
                if self.resume.experience_details:
                    return self.generate_work_experience_section()
                return ""

            def projects_fn():
                if self.resume.projects:
                    return self.generate_projects_section()
                return ""

            def achievements_fn():
                if self.resume.achievements:
                    return self.generate_achievements_section()
                return ""
            
            def certifications_fn():
                if self.resume.certifications:
                    return self.generate_certifications_section()
                return ""

            def additional_skills_fn():
                if (self.resume.experience_details or self.resume.education_details or
                    self.resume.languages or self.resume.interests):
                    return self.generate_additional_skills_section()
                return ""

            # Create a dictionary to map the function names to their respective callables
            functions = {
                "header": header_fn,
                "education": education_fn,
                "work_experience": work_experience_fn,
                "projects": projects_fn,
                "achievements": achievements_fn,
                "certifications": certifications_fn,
                "additional_skills": additional_skills_fn,
            }

            # Use ThreadPoolExecutor to run the functions in parallel with timeout
            results = {}
            try:
                with ThreadPoolExecutor() as executor:
                    future_to_section = {executor.submit(fn): section for section, fn in functions.items()}
                    for future in as_completed(future_to_section, timeout=60):  # 60 second timeout
                        section = future_to_section[future]
                        try:
                            result = future.result(timeout=10)  # 10 second timeout per section
                            if result and result.strip():
                                results[section] = result
                        except Exception as exc:
                            logger.error(f'{section} raised an exception: {exc}')
                            
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return self.generate_fallback_html_resume()
            
            # Check if we got enough content
            if len(results) < 2:  # Need at least header and one section
                logger.warning("Insufficient content from LLM, using fallback")
                return self.generate_fallback_html_resume()
                
            full_resume = "<body>\n"
            full_resume += f"  {results.get('header', '')}\n"
            full_resume += "  <main>\n"
            full_resume += f"    {results.get('education', '')}\n"
            full_resume += f"    {results.get('work_experience', '')}\n"
            full_resume += f"    {results.get('projects', '')}\n"
            full_resume += f"    {results.get('achievements', '')}\n"
            full_resume += f"    {results.get('certifications', '')}\n"
            full_resume += f"    {results.get('additional_skills', '')}\n"
            full_resume += "  </main>\n"
            full_resume += "</body>"
            
            # Final check - if content is too short, use fallback
            if len(full_resume.strip()) < 500:
                logger.warning("Generated content too short, using fallback")
                return self.generate_fallback_html_resume()
                
            return full_resume
            
        except Exception as e:
            logger.error(f"HTML generation failed completely: {e}")
            return self.generate_fallback_html_resume()
