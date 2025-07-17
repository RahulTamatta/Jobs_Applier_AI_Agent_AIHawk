import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configurations
# Replace these with actual configurations or load them from an environment/config file
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
USERNAME = 'your-email@example.com'
PASSWORD = 'your-email-password'

# Replace with actual paths
RESUME_PATH = 'path/to/generated/resume.pdf'
COVER_LETTER_PATH = 'path/to/generated/cover_letter.pdf'

# Function to send email

def send_application_email(to_email, subject, body, attachments=[]):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    for file in attachments:
        attachment = open(file, 'rb')
        mime = MIMEText(attachment.read(), 'base64', 'utf-8')
        mime['Content-Type'] = 'application/octet-stream'
        mime['Content-Disposition'] = f'attachment; filename={file}'
        msg.attach(mime)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.sendmail(USERNAME, to_email, msg.as_string())
        print('Application sent successfully!')
    except Exception as e:
        print(f'Failed to send application: {e}')

# Example usage
if __name__ == "__main__":
    job_email = 'hr@example.com'
    subject = 'Application for Job Position'
    body = 'Dear Hiring Manager,\n\nPlease find attached my resume and cover letter for your consideration.\n\nBest Regards,\nYour Name'

    send_application_email(job_email, subject, body, [RESUME_PATH, COVER_LETTER_PATH])

