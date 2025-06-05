import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm
import time
import pandas as pd

# Load environment variables
load_dotenv()

# Configuration from environment variables
EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COMPANY_LIST_PATH = os.getenv("COMPANY_LIST_PATH", "ai_companies.csv")
CV_PDF_PATH = os.getenv("CV_PDF_PATH", "cv/cv.pdf")
CV_TEXT_PATH = os.getenv("CV_TEXT_PATH", "cv/cv_extracted.txt")
PROMPT_TEMPLATE_PATH = os.getenv("PROMPT_TEMPLATE_PATH", "prompt-template/email-company.txt")

# Email settings
DELAY_BETWEEN_EMAILS = int(os.getenv("EMAIL_DELAY", 5))
SENDER_NAME = os.getenv("SENDER_NAME", "Your Name")

# Validate required configuration
required_vars = {
    'EMAIL_ADDRESS': EMAIL,
    'EMAIL_PASSWORD': APP_PASSWORD,
    'GEMINI_API_KEY': GEMINI_API_KEY,
    'COMPANY_LIST_PATH': COMPANY_LIST_PATH,
    'CV_PDF_PATH': CV_PDF_PATH,
    'CV_TEXT_PATH': CV_TEXT_PATH,
    'PROMPT_TEMPLATE_PATH': PROMPT_TEMPLATE_PATH,
    'SENDER_NAME': SENDER_NAME
}

missing_vars = [var for var, val in required_vars.items() if not val]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file.")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def read_text_file(file_path, description=""):
    """Read a text file with comprehensive error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                print(f"Warning: {description} file at {file_path} is empty.")
                return None
            return content
    except FileNotFoundError:
        print(f"Error: {description} file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading {description} file at {file_path}: {e}")
        return None

class CompanyEmailGenerator:
    """Email generator for AI company applications."""
    
    def __init__(self, contact_name, company_name, email, short_desc, full_desc, attachment_path=None):
        self.contact_name = contact_name
        self.company_name = company_name
        self.recipient_email = email.strip()
        self.short_desc = short_desc
        self.full_desc = full_desc
        self.attachment_path = attachment_path
        self.email_message = None
        
        # Generate email content
        message_content = self.generate_email_content()
        
        if not message_content:
            print(f"Failed to generate email content for {contact_name} at {company_name}")
            return
        
        # Create email message
        self.create_email_message(message_content)

    def generate_email_content(self):
        """Generate personalized email content for company outreach."""
        try:
            prompt = EMAIL_PROMPT_TEMPLATE.format(
                contact_name=self.contact_name,
                company_name=self.company_name,
                cv_text=CV_CONTEXT,
                short_desc=self.short_desc,
                full_desc=self.full_desc
            )
            
            response = gemini_model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                print(f"Warning: Empty response from Gemini for {self.company_name}")
                return None
                
        except Exception as e:
            print(f"Error generating email content for {self.company_name}: {e}")
            return None

    def create_email_message(self, message_content):
        """Create the complete email message with proper formatting and attachments."""
        try:
            # Parse subject from generated content
            lines = message_content.strip().split('\n')
            if lines[0].lower().startswith("subject:"):
                subject = lines[0][8:].strip()
                body = '\n'.join(lines[1:]).strip()
            else:
                subject = f"Interest in {self.company_name} - {SENDER_NAME}"
                body = message_content
            
            msg = MIMEMultipart()
            msg['From'] = f"{SENDER_NAME} <{EMAIL}>"
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            if self.attachment_path and os.path.exists(self.attachment_path):
                self.attach_file(msg, self.attachment_path)
            
            self.email_message = msg.as_string()
            
        except Exception as e:
            print(f"Error creating email message for {self.company_name}: {e}")
            self.email_message = None

    def attach_file(self, msg, file_path):
        """Attach a file to the email message."""
        try:
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                part = MIMEApplication(file.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file {file_path}: {e}")

    def send_email(self, smtp_server):
        """Send the email using the provided SMTP server."""
        if not self.email_message:
            return False
        
        try:
            smtp_server.sendmail(EMAIL, [self.recipient_email], self.email_message)
            print(f"Email sent successfully to {self.contact_name} at {self.company_name}")
            return True
        except Exception as e:
            print(f"Failed to send email to {self.contact_name}: {e}")
            return False

def main():
    """Main execution function."""
    smtp_server = None
    emails_sent = 0
    emails_skipped = 0
    
    try:
        # Load required files
        global CV_CONTEXT, EMAIL_PROMPT_TEMPLATE
        CV_CONTEXT = read_text_file(CV_TEXT_PATH, "CV text")
        EMAIL_PROMPT_TEMPLATE = read_text_file(PROMPT_TEMPLATE_PATH, "Email prompt template")

        if not CV_CONTEXT or not EMAIL_PROMPT_TEMPLATE:
            raise SystemExit("Cannot proceed without CV text and email prompt template files.")
        
        # Load company list
        df = pd.read_csv(COMPANY_LIST_PATH)
        print(f"Successfully loaded {len(df)} companies from CSV")
        
        # Connect to SMTP server
        print("Connecting to SMTP server...")
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(EMAIL, APP_PASSWORD)
        print("Successfully connected to email server!")
        
        # Process each company
        company_list = df.to_dict('records')
        
        for company in tqdm(company_list, desc="Processing companies", unit="email"):
            if pd.isna(company.get('email')) or pd.isna(company.get('company_name')):
                print(f"Skipping company due to missing required information")
                emails_skipped += 1
                continue
            
            email_generator = CompanyEmailGenerator(
                contact_name=company.get('contact_name', f"Team at {company['company_name']}"),
                company_name=company['company_name'],
                email=company['email'],
                short_desc=company.get('short_description', ''),
                full_desc=company.get('full_description', ''),
                attachment_path=CV_PDF_PATH
            )
            
            if email_generator.email_message:
                if email_generator.send_email(smtp_server):
                    emails_sent += 1
                    time.sleep(DELAY_BETWEEN_EMAILS)
                else:
                    emails_skipped += 1
            else:
                emails_skipped += 1
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        if smtp_server:
            smtp_server.quit()
            print("Disconnected from email server")
        
        print(f"\n--- Email Campaign Summary ---")
        print(f"Emails sent successfully: {emails_sent}")
        print(f"Emails skipped or failed: {emails_skipped}")
        print(f"Total companies processed: {emails_sent + emails_skipped}")

if __name__ == "__main__":
    main()