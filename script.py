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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ColdEmailGenerator:
    def __init__(self):
        """
        Initialize the cold email generator with credentials from environment variables.
        Required environment variables:
        - SENDER_EMAIL: Gmail address to send emails from
        - GMAIL_APP_PASSWORD: Gmail app-specific password
        - OPENAI_API_KEY: OpenAI API key
        """
        self.email = os.getenv('SENDER_EMAIL')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if not all([self.email, self.app_password, self.client.api_key]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

    # Rest of the class implementation remains the same...
    # [Previous methods remain unchanged]

if __name__ == "__main__":
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
    email_generator = ColdEmailGenerator()
    
    # Process and send emails
    process_professors_list(
        paths["excel_file"],
        email_generator,
        user_details,
        paths["cv_file"]
    )
