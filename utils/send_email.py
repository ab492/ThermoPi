import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os 

# Load environment variables from .env file
load_dotenv()
personal_email = os.getenv("PERSONAL_EMAIL")

def send_email(subject, body, to_email):
    from_email = os.getenv("THERMOPI_EMAIL_ACCOUNT")
    app_password = os.getenv("THERMOPI_EMAIL_ACCOUNT_APP_PASSWORD")

    # Create the root message and fill in the from, to, and subject headers
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
send_email("Hello from Python", "<h1>This is a test email sent from Python!</h1>", personal_email)
