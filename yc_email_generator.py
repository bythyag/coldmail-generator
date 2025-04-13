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

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
EMAIL = os.getenv("EMAIL_ADDRESS")
APP_PASSWORD = os.getenv("EMAIL_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# --- Updated Path for YC CSV ---
YC_LIST_PATH = "/Users/thyag/Desktop/projects/coldmail-generator/mailing list/india - Sheet3.csv"
# --- End Path Update ---
CV_PDF_PATH = "coldmail-generator/cv-pdf/Thyag_Raj.pdf" # Assuming same CV
CV_TEXT_PATH = "coldmail-generator/cv-texts/Thyag_Raj_extracted.txt" # Assuming same CV text
# --- Added YC Prompt Path ---
YC_PROMPT_TEMPLATE_PATH = "coldmail-generator/prompt-template/yc_prompt.txt"
# --- End YC Prompt Path ---

# --- Define Email Columns to check ---
RECIPIENT_EMAIL_COLUMNS = [
    'Person 1 Email',
    'Person 2 Email',
    'Person 3 Email',
    'Person 4 Email'
]
# --- Define Corresponding Name Columns ---
RECIPIENT_NAME_COLUMNS = [
    'Person 1 Name',
    'Person 2 Name',
    'Person 3 Name',
    'Person 4 Name'
]
# Ensure the order matches the email columns
# --- End Column Definitions ---


# --- Error Handling for missing environment variables/paths ---
if not all([EMAIL, APP_PASSWORD, GEMINI_API_KEY, YC_LIST_PATH, CV_PDF_PATH, CV_TEXT_PATH, YC_PROMPT_TEMPLATE_PATH]):
    missing = [var for var, val in locals().items() if var in ["EMAIL", "APP_PASSWORD", "GEMINI_API_KEY", "YC_LIST_PATH", "CV_PDF_PATH", "CV_TEXT_PATH", "YC_PROMPT_TEMPLATE_PATH"] and not val]
    raise ValueError(f"Missing environment variables or file paths: {', '.join(missing)}. Please check your .env file and ensure all files exist.")
# --- End Error Handling ---


# Email settings
DELAY_BETWEEN_EMAILS = 5  # Delay between each individual email send
# EMAIL_SUBJECT will be generated dynamically per company

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash') # Updated model

# --- Function to read text files (Unchanged) ---
def read_text_file(file_path, error_message_prefix):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {error_message_prefix} file not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading {error_message_prefix} file: {e}")
        return None

# --- Function to validate email (basic check) ---
def is_valid_email(email):
    if pd.isna(email) or not isinstance(email, str):
        return False
    # Basic check for presence of '@' and '.'
    return '@' in email and '.' in email.split('@')[-1]

# --- Function to validate name (basic check) ---
def is_valid_name(name):
    return pd.notna(name) and isinstance(name, str) and name.strip() != ""


# Read CV text and YC Prompt Template once
CV_CONTEXT = read_text_file(CV_TEXT_PATH, "CV text")
YC_EMAIL_PROMPT_TEMPLATE = read_text_file(YC_PROMPT_TEMPLATE_PATH, "YC Prompt template")

# --- Exit if essential files couldn't be read ---
if CV_CONTEXT is None or YC_EMAIL_PROMPT_TEMPLATE is None:
    raise SystemExit("Exiting: Could not read essential CV or YC Prompt template file.")
# --- End File Reading Check ---


class YCEmailGenerator:
    # --- __init__ remains largely the same, but recipient_emails will usually be a list of one ---
    def __init__(self, greeting, company_name, recipient_emails, short_desc, full_desc, attachment_path):
        if not isinstance(recipient_emails, list): # Ensure it's a list
             recipient_emails = [recipient_emails]
        self.recipients = recipient_emails # Store the list (usually just one email)
        self.company_name = company_name
        self.greeting = greeting # Store the specific greeting for this recipient

        # Generate email content using Gemini, CV context, and company info
        # The greeting passed here is now specific to the individual recipient
        # The generate_email function will attempt to strip the AI-generated greeting
        message_body_content = self.generate_email(self.greeting, company_name, short_desc, full_desc, CV_CONTEXT)

        if not message_body_content: # Handle potential generation failure
            # Updated print statement for clarity
            print(f"Skipping email to {self.recipients[0]} for {company_name} due to generation failure.")
            self.email_message = None # Ensure message is None if generation fails
            return # Avoid proceeding

        # Extract subject from the generated template (first line)
        try:
            # Handle potential empty lines before subject
            # message_body_content should now contain Subject + Body (without greeting)
            lines = message_body_content.strip().split('\n')
            subject_line = lines[0]
            body_content_only = '\n'.join(lines[1:]) # This is the body after the subject

            if subject_line.lower().startswith("subject:"):
                self.subject = subject_line[len("subject:"):].strip()
                # Use the body content directly as greeting was stripped in generate_email
                message_text = body_content_only.strip()
            else: # Fallback if subject line format is wrong
                print(f"Warning: Could not parse subject for {company_name} (Recipient: {self.recipients[0]}). Using default.")
                self.subject = f"Interest in {company_name} - Thyag Raj" # Default Subject
                # Use the full message_body_content if subject parsing failed
                message_text = message_body_content.strip()
        except (ValueError, IndexError): # Catch potential errors if message_body is empty or malformed
             print(f"Warning: Could not parse subject/body for {company_name} (Recipient: {self.recipients[0]}). Using default subject.")
             self.subject = f"Interest in {company_name} - Thyag Raj" # Default Subject
             # Use the full message_body_content if parsing failed
             message_text = message_body_content.strip()


        msg = MIMEMultipart()
        msg['From'] = EMAIL
        # --- Set 'To' header - will contain only the single recipient ---
        msg['To'] = self.recipients[0] # Directly use the single recipient email
        msg['Subject'] = self.subject

        # Attach the body text (greeting should have been stripped by generate_email)
        msg.attach(MIMEText(message_text, 'plain'))

        # Attach CV
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    filename = os.path.basename(attachment_path)
                    part = MIMEApplication(f.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
            except Exception as e:
                print(f"Error attaching file {attachment_path} for {self.recipients[0]}: {e}")

        self.email_message = msg.as_string()


    # --- generate_email attempts to strip the AI-generated greeting ---
    def generate_email(self, greeting, company_name, short_desc, full_desc, cv_text):
        # Format the prompt using the loaded YC template
        # Includes greeting placeholder (now specific to the recipient)
        # The prompt asks the AI *to* include the greeting.
        prompt = YC_EMAIL_PROMPT_TEMPLATE.format(
            contact_name=greeting, # Pass the specific greeting
            cv_text=cv_text or "N/A",
            short_desc=short_desc or "N/A",
            full_desc=full_desc or "N/A",
            company_name=company_name or "your company"
        )
        try:
            # Ensure you replace '[Your Name]' and potentially other placeholders
            # in the template or here if they are static.
            prompt = prompt.replace("[Your Name]", "Thyag Raj") # Replace with actual name
            # Add other static replacements if needed

            response = gemini_model.generate_content(prompt)

            generated_text = ""
            # --- Handle potential differences in Gemini response structure ---
            try:
                if hasattr(response, 'text') and response.text:
                    generated_text = response.text.strip()
                elif hasattr(response, 'parts') and response.parts:
                     generated_text = "".join(part.text for part in response.parts).strip()
                # Add more checks if the API response structure changes
            except Exception as e:
                 # Include recipient info if possible (though greeting is the best proxy here)
                 print(f"Warning: Could not extract text from Gemini response for {company_name} (Greeting: {greeting}). Error: {e}")
                 return None # Indicate failure if text extraction fails

            if not generated_text:
                 print(f"Warning: Gemini response for {company_name} (Greeting: {greeting}) seems empty.")
                 return None

            # --- RESTORED GREETING STRIPPING LOGIC ---
            # Remove the helper sections from the generated text
            # Also remove the {greeting} line as it's handled separately now
            parts = generated_text.split("---")
            main_content_with_greeting = parts[0].strip() # This includes Subject and AI-generated greeting
            # Remove the first line if it matches the greeting pattern
            lines = main_content_with_greeting.split('\n')
            # Check if the first non-empty line matches the greeting
            first_line_index = 0
            while first_line_index < len(lines) and not lines[first_line_index].strip():
                first_line_index += 1

            # Check if the line *after* the subject matches the greeting
            subject_line_index = first_line_index
            greeting_line_index = -1
            if subject_line_index < len(lines) and lines[subject_line_index].lower().startswith("subject:"):
                # Look for the greeting on the line *after* the subject
                potential_greeting_index = subject_line_index + 1
                # Skip potential blank lines between subject and greeting
                while potential_greeting_index < len(lines) and not lines[potential_greeting_index].strip():
                    potential_greeting_index += 1
                if potential_greeting_index < len(lines) and lines[potential_greeting_index].strip() == greeting:
                    greeting_line_index = potential_greeting_index

            if greeting_line_index != -1:
                 # Reconstruct content: Subject + lines after the greeting
                 subject_line = lines[subject_line_index]
                 body_after_greeting = '\n'.join(lines[greeting_line_index+1:]).strip()
                 main_content = f"{subject_line}\n\n{body_after_greeting}" # Add back spacing
            else:
                 # If greeting wasn't found where expected, return the original content
                 # (Subject + AI-generated greeting + Body)
                 # The __init__ method will use this directly.
                 print(f"Debug: Could not strip expected greeting '{greeting}' after subject for {company_name}. Using full AI output.")
                 main_content = main_content_with_greeting


            return main_content # Return Subject + Body (hopefully without AI greeting)

        except Exception as e:
            print(f"Error generating email content for {company_name} (Greeting: {greeting}): {e}")
            return None


    # --- send_mail remains the same, uses self.recipients (list of one) ---
    def send_mail(self, server):
        if not self.email_message: # Don't try to send if generation failed
             return False
        try:
            # Pass the list of recipients (containing one email) to sendmail
            server.sendmail(EMAIL, self.recipients, self.email_message)
            # Updated print statement for individual sending
            print(f"Email sent successfully to {self.recipients[0]} at {self.company_name}")
            return True
        except Exception as e:
            # Include recipient in the error message
            print(f"Failed to send email to {self.recipients[0]}: {str(e)}")
            return False

if __name__ == "__main__":
    server = None
    emails_sent_count = 0
    emails_skipped_count = 0
    try:
        # --- Read the YC CSV file ---
        try:
            df = pd.read_csv(YC_LIST_PATH)
            print(f"Successfully loaded {len(df)} companies from {YC_LIST_PATH}")
        except FileNotFoundError:
             print(f"Error: Input file not found at {YC_LIST_PATH}. Please check the path.")
             raise # Re-raise to be caught by the outer try-except
        except Exception as e:
             print(f"Error reading CSV file {YC_LIST_PATH}: {e}")
             raise # Re-raise
        # --- End file reading ---

        # Connect to email server
        print("Connecting to SMTP server...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL, APP_PASSWORD)
        print("Successfully logged in!")

        # Convert DataFrame rows to list of dictionaries
        company_list = df.to_dict('records')

        # --- Modified loop to send individual emails ---
        print(f"Processing {len(company_list)} companies...")
        # Use tqdm on the company list, but process individuals inside
        for index, company in enumerate(tqdm(company_list, desc="Processing Companies", unit="company")):
            # Get company-level data safely
            company_name = company.get('Company Name')
            short_desc = company.get('Description')
            full_desc = company.get('Full Description')

            # --- Basic Company-Level Validation ---
            if not company_name:
                 print(f"Skipping row {index + 2} due to missing Company Name.")
                 emails_skipped_count += len(RECIPIENT_EMAIL_COLUMNS) # Estimate skips
                 continue
            # Optional: Add check for descriptions if they are critical for your prompt
            if not short_desc and not full_desc:
                 print(f"Warning: Skipping company {company_name} (Row {index + 2}) due to missing descriptions.")
                 emails_skipped_count += len(RECIPIENT_EMAIL_COLUMNS) # Estimate skips
                 continue

            # --- Iterate through each potential contact pair ---
            contacts_found_for_company = False
            for name_col, email_col in zip(RECIPIENT_NAME_COLUMNS, RECIPIENT_EMAIL_COLUMNS):
                if email_col not in company:
                    # Optional: print(f"Debug: Column '{email_col}' not found in row {index + 2}.")
                    continue # Skip if email column doesn't exist for this row

                email = company[email_col]
                name = company.get(name_col) # Use .get() for name as it might be missing

                # --- Validate individual email ---
                if not is_valid_email(email):
                    # Optional: print(f"Debug: Invalid or missing email in column '{email_col}' for {company_name}.")
                    continue # Skip this specific contact if email is invalid

                contacts_found_for_company = True # Mark that we found at least one valid email for this company
                recipient_email = email.strip()

                # --- Construct the Individual Greeting ---
                greeting = f"Dear Team at {company_name}," # Fallback greeting
                first_name = None
                if is_valid_name(name):
                    # Extract first name if possible for brevity
                    first_name = str(name).split()[0]
                    greeting = f"Dear {first_name},"
                # else: # Optional: Use a generic placeholder if name is invalid/missing
                #    greeting = "Dear Team Member,"

                print(f"\nProcessing contact: {recipient_email} at {company_name} (Greeting: {greeting})")

                # --- Create email object for the individual recipient ---
                email_instance = YCEmailGenerator(
                    greeting=greeting,              # Pass the specific greeting
                    company_name=company_name,
                    recipient_emails=[recipient_email], # Pass email as a list
                    short_desc=short_desc,
                    full_desc=full_desc,
                    attachment_path=CV_PDF_PATH     # Pass the PDF path
                )

                # Send the email if generation was successful
                if email_instance.email_message:
                   if email_instance.send_mail(server):
                       emails_sent_count += 1
                       print(f"Waiting {DELAY_BETWEEN_EMAILS} seconds...")
                       time.sleep(DELAY_BETWEEN_EMAILS) # Wait only after successful send
                   else:
                       emails_skipped_count += 1
                       # Consider if you want to stop entirely on a single failure
                       print(f"Send failure for {recipient_email}. Continuing to next contact/company.")
                       # break # Uncomment this line to stop the entire script on first send failure
                else:
                    emails_skipped_count += 1
                    print(f"Skipping send for {recipient_email} due to generation/initialization failure.")

            # --- End of loop for contacts within a company ---
            if not contacts_found_for_company:
                print(f"Skipping company {company_name} (Row {index + 2}): No valid email addresses found in specified columns.")
                # emails_skipped_count is implicitly handled as we didn't attempt sends

        # --- End of loop for companies ---

    except FileNotFoundError:
        # Already handled during file reading, but keep for safety
        print(f"Error: Input file not found. Please check the path in YC_LIST_PATH.")
    except ValueError as ve:
         print(f"Configuration Error: {ve}")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your EMAIL_ADDRESS and EMAIL_PASSWORD in .env.")
    except SystemExit as se:
        print(se) # Print message from SystemExit
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        import traceback
        print(f"\nAn unexpected error occurred: {str(e)}")
        print("Traceback:")
        traceback.print_exc() # Print detailed traceback for debugging
    finally:
        if server:
            print("\nQuitting SMTP server.")
            server.quit()
        print(f"\n--- Summary ---")
        print(f"Emails Sent Successfully: {emails_sent_count}")
        print(f"Emails Skipped/Failed: {emails_skipped_count}")
        print("Script finished.")