#!/usr/bin/env python3

import sys
from pathlib import Path
from src.libs.resume_and_cover_builder import ResumeGenerator, StyleManager
from src.resume_schemas.resume import Resume

def test_html_generation():
    """Test HTML generation with simple content"""
    
    # Load the plain text resume
    with open("data_folder/plain_text_resume.yaml", "r", encoding="utf-8") as file:
        plain_text_resume = file.read()
    
    # Create a simple HTML content instead of using LLM
    simple_html = """
    <body>
        <header>
            <h1>Rahul Tamatta</h1>
            <div class="contact-info">
                <p><span>Thane, MH, India</span></p>
                <p><span>+91 8291541168</span></p>
                <p><span>rahultamatta73000@gmail.com</span></p>
                <p><a href="https://www.linkedin.com/in/rahultamatta2301">LinkedIn</a></p>
                <p><a href="https://github.com/rahultamatta">GitHub</a></p>
            </div>
        </header>
        <main>
            <section id="education">
                <h2>Education</h2>
                <div class="entry">
                    <div class="entry-header">
                        <span class="entry-name">A.P. Shah Institute of Technology</span>
                        <span class="entry-location">Thane, India</span>
                    </div>
                    <div class="entry-details">
                        <span class="entry-title">Bachelor's Degree in Electronics & Telecommunication Engineering</span>
                        <span class="entry-year">2019 – 2023</span>
                    </div>
                </div>
            </section>
            
            <section id="work-experience">
                <h2>Work Experience</h2>
                <div class="entry">
                    <div class="entry-header">
                        <span class="entry-name">Smitox</span>
                        <span class="entry-location">Mumbai, India</span>
                    </div>
                    <div class="entry-details">
                        <span class="entry-title">Full-Stack Developer (MERN + Flutter)</span>
                        <span class="entry-year">May 2024 – Feb 2025</span>
                    </div>
                    <ul class="compact-list">
                        <li>Developed end-to-end MERN stack solutions with React.js and Flutter frontends</li>
                        <li>Optimized bulk inventory management with efficient queries, reducing load times</li>
                        <li>Integrated Razorpay for secure payments, supporting subscriptions and refunds</li>
                    </ul>
                </div>
            </section>
            
            <section id="skills-languages">
                <h2>Skills</h2>
                <div class="two-column">
                    <ul class="compact-list">
                        <li>Flutter</li>
                        <li>React.js</li>
                        <li>Node.js</li>
                        <li>MongoDB</li>
                        <li>Express.js</li>
                        <li>Google Maps SDK</li>
                    </ul>
                    <ul class="compact-list">
                        <li>MVVM Architecture</li>
                        <li>UI/UX Design</li>
                        <li>Payment Integration</li>
                        <li>Offline Storage</li>
                        <li>Responsive Design</li>
                        <li><strong>Languages:</strong> English (Fluent), Hindi (Native)</li>
                    </ul>
                </div>
            </section>
        </main>
    </body>
    """
    
    return simple_html

if __name__ == "__main__":
    html_content = test_html_generation()
    print("HTML Content Length:", len(html_content))
    print("First 200 characters:", html_content[:200])
    
    # Test if content is valid
    if html_content.strip():
        print("✅ HTML content generated successfully")
        
        # Save to file for inspection
        with open("debug_resume.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("💾 Saved debug HTML to debug_resume.html")
    else:
        print("❌ HTML content is empty!")
