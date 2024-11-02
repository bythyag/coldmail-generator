import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from openai import OpenAI
from tqdm import tqdm
import time
import pandas as pd
from typing import Optional

class ColdEmailGenerator:
    def __init__(self, sender_email: str, app_password: str, openai_key: str):
        """
        Initialize the cold email generator with necessary credentials.
        
        Args:
            sender_email: Gmail address to send emails from
            app_password: Gmail app-specific password
            openai_key: OpenAI API key
        """
        self.email = sender_email
        self.app_password = app_password
        self.client = OpenAI(api_key=openai_key)
        
    def _generate_system_prompt(self, name: str, degree: str, university: str, 
                              research_interests: str, experience: str) -> str:
        """Generate the system prompt for GPT based on user details."""
        return f"""
        You are a cold email writer for Research Assistant or Visiting Researcher positions.
        Write a cold email for {name}, who is pursuing {degree} at {university}.
        Their research interests are in {research_interests}.
        
        Here is their relevant experience:
        {experience}
        
        Guidelines for the email:
        - Write 3-4 concise paragraphs
        - Highlight research experience in bullet points
        - Personalize to the professor's research interests
        - Maintain professional and courteous tone
        - Keep under 200 words
        - Don't mention professor's university name
        - Don't use hyperbolic terms like "deep expertise" or "extensive experience"
        - Don't include subject line or personal contact information
        - Format should be:
          - Greeting
          - Introduction paragraph
          - Research experience bullets
          - Research interest alignment
          - Closing paragraph
          - Professional signature
        """

    def generate_email(self, professor_name: str, professor_university: str, 
                      research_interests: str, user_details: dict) -> str:
        """
        Generate a customized cold email using OpenAI's API.
        """
        system_prompt = self._generate_system_prompt(
            name=user_details['name'],
            degree=user_details['degree'],
            university=user_details['university'],
            research_interests=user_details['research_interests'],
            experience=user_details['experience']
        )
        
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"The Professor's name is {professor_name} from {professor_university}. Their research interests are {research_interests}."}
            ]
        )
        
        return completion.choices[0].message.content

    def send_email(self, recipient: str, subject: str, message: str, 
                  attachment_path: Optional[str] = None) -> bool:
        """
        Send an email with optional attachment.
        Returns True if successful, False otherwise.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            if attachment_path:
                with open(attachment_path, 'rb') as f:
                    filename = os.path.basename(attachment_path)
                    part = MIMEApplication(f.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.email, self.app_password)
            server.send_message(msg)
            server.quit()
            return True
            
        except Exception as e:
            print(f"Failed to send email to {recipient}: {str(e)}")
            return False

def process_professors_list(excel_path: str, email_generator: ColdEmailGenerator, 
                          user_details: dict, cv_path: Optional[str] = None,
                          delay: int = 3):
    """
    Process a list of professors from an Excel file and send cold emails.
    
    Args:
        excel_path: Path to Excel file containing professor details
        email_generator: Initialized ColdEmailGenerator instance
        user_details: Dictionary containing user's details
        cv_path: Optional path to CV file
        delay: Delay between emails in seconds
    """
    try:
        df = pd.read_excel(excel_path)
        professor_list = df.to_dict('records')
        
        for professor in tqdm(professor_list, desc="Sending emails", unit="email"):
            if pd.isna(professor['email']) or pd.isna(professor['research_interests']):
                print(f"Skipping {professor['name']} due to missing data")
                continue
                
            message = email_generator.generate_email(
                professor["name"],
                professor["university"],
                professor["research_interests"],
                user_details
            )
            
            subject = f"Application for Research Position - {user_details['name']} ({user_details['university']})"
            
            success = email_generator.send_email(
                professor["email"],
                subject,
                message,
                cv_path
            )
            
            if success:
                print(f"Email sent successfully to {professor['email']}")
            
            time.sleep(delay)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # User configuration
    config = {
        "sender_email": "your.email@gmail.com",
        "app_password": "your-app-specific-password",
        "openai_key": "your-openai-api-key"
    }
    
    # User details
    user_details = {
        "name": "Your Name",
        "degree": "B.Tech/M.Tech/etc",
        "university": "Your University",
        "research_interests": "Your research interests",
        "experience": """
        • Project/Research Experience 1
        • Project/Research Experience 2
        • Relevant coursework or thesis
        """
    }
    
    # Paths configuration
    paths = {
        "excel_file": "path/to/professors_list.xlsx",
        "cv_file": "path/to/your/cv.pdf"  # Optional
    }
    
    # Initialize email generator
    email_generator = ColdEmailGenerator(
        config["sender_email"],
        config["app_password"],
        config["openai_key"]
    )
    
    # Process and send emails
    process_professors_list(
        paths["excel_file"],
        email_generator,
        user_details,
        paths["cv_file"]
    )
