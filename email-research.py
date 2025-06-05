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
CONTACT_LIST_PATH = os.getenv("CONTACT_LIST_PATH", "professors_list.csv")
CV_PDF_PATH = os.getenv("CV_PDF_PATH", "cv/cv.pdf")
CV_TEXT_PATH = os.getenv("CV_TEXT_PATH", "cv/cv_extracted.txt")
PROMPT_TEMPLATE_PATH = os.getenv("PROMPT_TEMPLATE_PATH", "coldmail-generator/prompt-template/email-research.txt")

# Email settings
DELAY_BETWEEN_EMAILS = int(os.getenv("EMAIL_DELAY", 5))
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "Application for Research Assistant Position")

# Validate required configuration
required_vars = {
    'EMAIL_ADDRESS': EMAIL,
    'EMAIL_PASSWORD': APP_PASSWORD, 
    'GEMINI_API_KEY': GEMINI_API_KEY,
    'CONTACT_LIST_PATH': CONTACT_LIST_PATH,
    'CV_PDF_PATH': CV_PDF_PATH,
    'CV_TEXT_PATH': CV_TEXT_PATH,
    'PROMPT_TEMPLATE_PATH': PROMPT_TEMPLATE_PATH
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

def validate_email(email):
    """Validate email address format."""
    if pd.isna(email) or not isinstance(email, str):
        return False
    email = email.strip()
    return '@' in email and '.' in email.split('@')[-1] and len(email) > 5

def validate_required_data(data_dict, required_fields):
    """Validate that all required fields are present and non-empty."""
    for field in required_fields:
        value = data_dict.get(field)
        if pd.isna(value) or not str(value).strip():
            return False, field
    return True, None

# Load essential files once
print("Loading essential files...")
CV_CONTEXT = read_text_file(CV_TEXT_PATH, "CV text")
EMAIL_PROMPT_TEMPLATE = read_text_file(PROMPT_TEMPLATE_PATH, "Email prompt template")

if not CV_CONTEXT or not EMAIL_PROMPT_TEMPLATE:
    raise SystemExit("Cannot proceed without CV text and email prompt template files.")

# Add sender configuration
SENDER_NAME = os.getenv("SENDER_NAME", "Your Name")  # Add this after other env variables
SENDER_DETAILS = {
    'name': SENDER_NAME,
    'email': EMAIL,
}

required_vars.update({
    'SENDER_NAME': SENDER_NAME
})

class ResearchPositionEmailGenerator:
    """Email generator for research position applications following cultural and academic guidelines."""
    
    def __init__(self, professor_name, university, email, research_interests, attachment_path=None):
        self.professor_name = professor_name
        self.university = university
        self.recipient_email = email.strip()
        self.research_interests = research_interests
        self.attachment_path = attachment_path
        self.email_message = None
        self.subject = self._generate_subject()
        
        # Generate email content
        message_content = self.generate_email_content()
        
        if not message_content:
            print(f"Failed to generate email content for {professor_name} at {university}")
            return
        
        # Create email message
        self.create_email_message(message_content)
    
    def _generate_subject(self):
        """Generate a contextual subject line."""
        return f"Research Opportunity Inquiry - {SENDER_NAME} ({self.university})"
    
    def generate_email_content(self):
        """Generate personalized email content following cultural and academic guidelines."""
        try:
            # Create a more detailed prompt context
            prompt = EMAIL_PROMPT_TEMPLATE.format(
                cv_text=CV_CONTEXT,
                professor_name=self.professor_name,
                university=self.university,
                research_interests=self.research_interests
            )
            
            # Add specific instructions for tone and style
            context_prompt = f"""
            Generate an email following Indian academic courtesy and professionalism:
            - From: {SENDER_NAME}
            - To: Professor {self.professor_name} at {self.university}
            - Research Focus: {self.research_interests}
            
            Please maintain:
            1. Professional warmth with appropriate cultural respect
            2. Clear connection between sender's background and professor's work
            3. Specific references to the research interests
            4. Authentic and personal tone while maintaining academic decorum
            """
            
            # Combine prompts
            full_prompt = f"{context_prompt}\n\n{prompt}"
            
            response = gemini_model.generate_content(full_prompt)
            
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'parts') and response.parts:
                return "".join(part.text for part in response.parts).strip()
            else:
                print(f"Warning: Empty response from Gemini for {self.professor_name}")
                return None
                
        except Exception as e:
            print(f"Error generating email content for {self.professor_name}: {e}")
            return None
    
    def create_email_message(self, message_body):
        """Create the complete email message with proper formatting and attachments."""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{SENDER_NAME} <{EMAIL}>"
            msg['To'] = self.recipient_email
            msg['Subject'] = self.subject
            
            # Attach message body
            msg.attach(MIMEText(message_body, 'plain'))
            
            # Attach CV if path provided and file exists
            if self.attachment_path and os.path.exists(self.attachment_path):
                self.attach_file(msg, self.attachment_path)
            elif self.attachment_path:
                print(f"Warning: Attachment file not found at {self.attachment_path}")
            
            self.email_message = msg.as_string()
            
        except Exception as e:
            print(f"Error creating email message for {self.professor_name}: {e}")
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
            print(f"Email sent successfully to {self.professor_name} ({self.recipient_email})")
            return True
        except Exception as e:
            print(f"Failed to send email to {self.professor_name} ({self.recipient_email}): {e}")
            return False

def load_contact_list(file_path):
    """Load contact list from CSV or Excel file."""
    try:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}. Use CSV or Excel files.")
        
        print(f"Successfully loaded {len(df)} contacts from {file_path}")
        return df
    
    except FileNotFoundError:
        print(f"Error: Contact list file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading contact list: {e}")
        return None

def normalize_column_names(df):
    """Normalize column names to standard format."""
    column_mapping = {
        'name': ['name', 'professor_name', 'prof_name', 'full_name'],
        'university': ['university', 'institution', 'college', 'school'],
        'email': ['email', 'email_address', 'contact_email'],
        'research_interests': ['research_interests', 'research_areas', 'interests', 'research_focus']
    }
    
    # Create reverse mapping
    reverse_mapping = {}
    for standard_name, variations in column_mapping.items():
        for variation in variations:
            reverse_mapping[variation.lower()] = standard_name
    
    # Rename columns
    df_columns_lower = {col: col.lower() for col in df.columns}
    new_column_names = {}
    
    for original_col in df.columns:
        lower_col = original_col.lower()
        if lower_col in reverse_mapping:
            new_column_names[original_col] = reverse_mapping[lower_col]
    
    df = df.rename(columns=new_column_names)
    return df

def main():
    """Main execution function."""
    smtp_server = None
    emails_sent = 0
    emails_skipped = 0
    
    try:
        # Load contact list
        df = load_contact_list(CONTACT_LIST_PATH)
        if df is None:
            return
        
        # Normalize column names
        df = normalize_column_names(df)
        
        # Validate required columns exist
        required_columns = ['name', 'university', 'email', 'research_interests']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns in contact list: {missing_columns}")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Connect to SMTP server
        print("Connecting to SMTP server...")
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(EMAIL, APP_PASSWORD)
        print("Successfully connected to email server!")
        
        # Process each contact
        contact_list = df.to_dict('records')
        
        for contact in tqdm(contact_list, desc="Processing contacts", unit="email"):
            # Validate required data
            is_valid, missing_field = validate_required_data(contact, required_columns)
            
            if not is_valid:
                print(f"Skipping contact due to missing {missing_field}: {contact.get('name', 'Unknown')}")
                emails_skipped += 1
                continue
            
            # Validate email format
            if not validate_email(contact['email']):
                print(f"Skipping contact due to invalid email: {contact['name']}")
                emails_skipped += 1
                continue
            
            # Generate and send email
            email_generator = ResearchPositionEmailGenerator(
                professor_name=contact['name'],
                university=contact['university'],
                email=contact['email'],
                research_interests=contact['research_interests'],
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
                print(f"Skipped {contact['name']} due to email generation failure")
    
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Please check your email credentials in the .env file")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    finally:
        if smtp_server:
            smtp_server.quit()
            print("Disconnected from email server")
        
        print(f"\n--- Email Campaign Summary ---")
        print(f"Emails sent successfully: {emails_sent}")
        print(f"Emails skipped or failed: {emails_skipped}")
        print(f"Total contacts processed: {emails_sent + emails_skipped}")

if __name__ == "__main__":
    main()