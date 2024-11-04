import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from openai import OpenAI
from tqdm import tqdm
import time
import pandas as pd

# Configuration
EMAIL = "your.email@gmail.com"
APP_PASSWORD = "your_app_password"  # Gmail App Password
OPENAI_API_KEY = "your_openai_api_key"

# File paths
EXCEL_PATH = "path/to/your/professors_list.xlsx"
CV_PATH = "path/to/your/cv.pdf"

# Email settings
DELAY_BETWEEN_EMAILS = 3  # seconds
EMAIL_SUBJECT = "Application for Research Assistant or Visiting Student Position"

client = OpenAI(api_key=OPENAI_API_KEY)

class coldmail:
    def __init__(self, professor_name, university, email, research_interests, attachment_path):
        message_text = self.generate_email(professor_name, university, research_interests)
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = EMAIL_SUBJECT

        msg.attach(MIMEText(message_text, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                filename = os.path.basename(attachment_path)
                part = MIMEApplication(f.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)
        
        self.email_message = msg.as_string()
        self.recipient = email
        self.send_mail()

    def generate_email(self, professor_name, university, research_interests):
        completion = client.chat.completions.create(
            model="gpt-4",  # Updated to standard model name
            messages=[
                {"role": "system", "content": """
                You are a cold email writer for Research Assistant or Visiting Researcher positions. 
                Write a professional email with the following structure:

                1. Introduction paragraph with student background
                2. Research experience in bullet points
                3. Technical skills paragraph
                4. Closing paragraph expressing interest in the lab

                Guidelines:
                - Keep it under 200 words
                - Be professional and courteous
                - Personalize to the professor's research
                - Avoid overly promotional language
                - Include relevant technical background
                - Make clear connection between student's interests and professor's work
                """},
                {
                    "role": "user",
                    "content": f"The Professor's name is {professor_name} from {university}. Their research interests are {research_interests}."
                }
            ]
        )
        
        return completion.choices[0].message.content

    def send_mail(self):
        try:
            server.sendmail(EMAIL, self.recipient, self.email_message)
            print(f"Email sent successfully to {self.recipient}")
        except Exception as e:
            print(f"Failed to send email to {self.recipient}: {str(e)}")

if __name__ == "__main__":
    try:
        # Read the Excel file
        df = pd.read_excel(EXCEL_PATH)
        
        # Connect to email server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL, APP_PASSWORD)
        print("Successfully logged in!")

        # Convert DataFrame rows to list of dictionaries
        professor_list = df.to_dict('records')

        # Send emails
        for professor in tqdm(professor_list, desc="Sending emails", unit="email"):
            # Skip if email contains "NaN" or research interests are NaN
            if pd.isna(professor['email']) or pd.isna(professor['research_interests']):
                print(f"Skipping {professor['name']} due to missing data")
                continue
                
            coldmail(
                professor["name"],
                professor["university"],
                professor["email"],
                professor["research_interests"],
                CV_PATH
            )
            time.sleep(DELAY_BETWEEN_EMAILS)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'server' in locals():
            server.quit()
