# filepath: /Users/thyag/Desktop/projects/coldmail-generator/cold_email_generator.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
# Removed: from openai import OpenAI
import google.generativeai as genai # Added Gemini
from dotenv import load_dotenv # Added dotenv
from tqdm import tqdm
import time
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EXCEL_PATH = "/Users/thyag/Desktop/projects/coldmail-generator/mailing list/NYU Dubai - Sheet2 (1).csv"
CV_PDF_PATH = "coldmail-generator/cv-pdf/Thyag_Raj_CV.pdf"
CV_TEXT_PATH = "coldmail-generator/cv-texts/Thyag_Raj_CV_extracted.txt"
PROMPT_TEMPLATE_PATH = "coldmail-generator/prompt-template/prompt.txt" # Added prompt file path

# --- Error Handling for missing environment variables ---
if not all([EMAIL, APP_PASSWORD, GEMINI_API_KEY, EXCEL_PATH, CV_PDF_PATH, CV_TEXT_PATH, PROMPT_TEMPLATE_PATH]):
    missing = [var for var, val in locals().items() if var in ["EMAIL", "APP_PASSWORD", "GEMINI_API_KEY", "EXCEL_PATH", "CV_PDF_PATH", "CV_TEXT_PATH", "PROMPT_TEMPLATE_PATH"] and not val]
    raise ValueError(f"Missing environment variables or file paths: {', '.join(missing)}. Please check your .env file and ensure all files exist.")
# --- End Error Handling ---


# Email settings
DELAY_BETWEEN_EMAILS = 3  # seconds
EMAIL_SUBJECT = "Application for Research Assistant or Visiting Student Position"

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash') # Or other suitable Gemini model

# --- Function to read text files ---
def read_text_file(file_path, error_message_prefix):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {error_message_prefix} file not found at {file_path}")
        return None # Return None to indicate failure
    except Exception as e:
        print(f"Error reading {error_message_prefix} file: {e}")
        return None # Return None to indicate failure

# Read CV text and Prompt Template once
CV_CONTEXT = read_text_file(CV_TEXT_PATH, "CV text")
EMAIL_PROMPT_TEMPLATE = read_text_file(PROMPT_TEMPLATE_PATH, "Prompt template")

# --- Exit if essential files couldn't be read ---
if CV_CONTEXT is None or EMAIL_PROMPT_TEMPLATE is None:
    raise SystemExit("Exiting: Could not read essential CV or Prompt template file.")
# --- End File Reading Check ---


class coldmail:
    def __init__(self, professor_name, university, email, research_interests, attachment_path):
        # Generate email content using Gemini and CV context
        message_text = self.generate_email(professor_name, university, research_interests, CV_CONTEXT)

        if not message_text: # Handle potential generation failure
            print(f"Skipping email to {email} due to generation failure.")
            return # Avoid sending empty email

        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = email
        msg['Subject'] = EMAIL_SUBJECT

        msg.attach(MIMEText(message_text, 'plain'))

        # Use CV_PDF_PATH for the attachment
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    filename = os.path.basename(attachment_path)
                    part = MIMEApplication(f.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
            except Exception as e:
                print(f"Error attaching file {attachment_path}: {e}")

        self.email_message = msg.as_string()
        self.recipient = email
        # self.send_mail() # Moved sending logic to main block

    # Updated generate_email method for Gemini
    def generate_email(self, professor_name, university, research_interests, cv_text):
        # Format the prompt using the loaded template
        prompt = EMAIL_PROMPT_TEMPLATE.format(
            cv_text=cv_text,
            research_interests=research_interests,
            professor_name=professor_name,
            university=university
        )
        try:
            response = gemini_model.generate_content(prompt)
            # Basic check if response has text (may need refinement based on Gemini API)
            if response.text:
                return response.text.strip()
            else:
                print(f"Warning: Gemini response for {professor_name} seems empty.")
                # Attempt to access parts if text is empty (structure might vary)
                if response.parts:
                     return "".join(part.text for part in response.parts).strip()
                return None # Indicate failure
        except Exception as e:
            print(f"Error generating email content for {professor_name}: {e}")
            return None # Indicate failure


    # send_mail method remains largely the same, but will be called from main loop
    def send_mail(self, server): # Pass server instance
        try:
            server.sendmail(EMAIL, self.recipient, self.email_message)
            print(f"Email sent successfully to {self.recipient}")
            return True # Indicate success
        except Exception as e:
            print(f"Failed to send email to {self.recipient}: {str(e)}")
            return False # Indicate failure

if __name__ == "__main__":
    server = None # Initialize server to None
    try:
        # --- Determine file type and read data ---
        if EXCEL_PATH.endswith('.xlsx'):
            df = pd.read_excel(EXCEL_PATH)
        elif EXCEL_PATH.endswith('.csv'):
            df = pd.read_csv(EXCEL_PATH)
        else:
            raise ValueError(f"Unsupported file format for EXCEL_PATH: {EXCEL_PATH}. Use .xlsx or .csv")
        # --- End file reading ---

        # Connect to email server
        print("Connecting to SMTP server...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL, APP_PASSWORD)
        print("Successfully logged in!")

        # Convert DataFrame rows to list of dictionaries
        # Ensure column names match your CSV/Excel file exactly (case-sensitive)
        # Common names might be 'Name', 'University', 'Email', 'Research Interests'
        # Adjust '.get()' calls below if your column names differ.
        professor_list = df.to_dict('records')

        # Send emails
        for professor in tqdm(professor_list, desc="Processing emails", unit="email"):
            # Get data safely using .get() with default None
            prof_name = professor.get('name') # Adjust 'name' if column name is different
            prof_uni = professor.get('university') # Adjust 'university'
            prof_email = professor.get('email') # Adjust 'email'
            prof_interests = professor.get('research_interests') # Adjust 'research_interests'

            # Skip if essential data is missing or email is invalid
            if not all([prof_name, prof_uni, prof_email, prof_interests]) or pd.isna(prof_email):
                print(f"Skipping entry due to missing data: Name={prof_name}, Email={prof_email}")
                continue

            # Create email object
            email_instance = coldmail(
                prof_name,
                prof_uni,
                prof_email,
                prof_interests,
                CV_PDF_PATH # Pass the PDF path for attachment
            )

            # Send the email if generation was successful
            if hasattr(email_instance, 'email_message'): # Check if init completed
               if email_instance.send_mail(server): # Pass server object
                   time.sleep(DELAY_BETWEEN_EMAILS) # Wait only after successful send
               else:
                   print(f"Halting due to send failure for {prof_email}. Check credentials/server.")
                   break # Optional: Stop if one email fails

    except FileNotFoundError:
        print(f"Error: Input file not found at {EXCEL_PATH}. Please check the EXCEL_PATH in your .env file.")
    except ValueError as ve:
         print(f"Configuration Error: {ve}")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your GMAIL_EMAIL and GMAIL_APP_PASSWORD in .env.")
    except SystemExit as se: # Catch the SystemExit raised earlier
        print(se)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        if server:
            print("Quitting SMTP server.")
            server.quit()