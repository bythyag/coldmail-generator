class EmailSender:
    """Handles SMTP connection and email sending."""
    def __init__(self, config):
        self.config = config
        self.server = None

    def connect(self):
        """Connects and logs into the SMTP server."""
        try:
            print(f"Connecting to SMTP server {self.config.smtp_server}:{self.config.smtp_port}...")
            self.server = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
            self.server.login(self.config.email_address, self.config.email_password)
            print("Successfully logged into email server.")
            return True
        except smtplib.SMTPAuthenticationError:
            print("\nError: SMTP Authentication failed. Check your EMAIL_ADDRESS and EMAIL_PASSWORD/.env.")
            print("If using Gmail, ensure you're using an App Password.")
            self.server = None
            return False
        except smtplib.SMTPException as e:
            print(f"\nAn SMTP error occurred during connection: {e}")
            self.server = None
            return False
        except Exception as e:
            print(f"\nAn unexpected error occurred during connection: {str(e)}")
            self.server = None
            return False

    def send(self, recipient, body, attachment_path=None):
        """Creates and sends an email."""
        if not self.server:
            print("Error: Not connected to SMTP server. Cannot send email.")
            return False
        if not self.config.email_address:
            print("Error: Sender email address not configured.")
            return False

        msg = MIMEMultipart()
        msg['From'] = self.config.email_address
        msg['To'] = recipient

        # Extract subject from the generated body
        try:
            subject_line, email_body = body.split('\n', 1)
            if subject_line.lower().startswith("subject:"):
                msg['Subject'] = subject_line.split(":", 1)[1].strip()
                msg.attach(MIMEText(email_body.strip(), 'plain'))
            else:
                print("Warning: LLM did not provide subject line in expected format. Using default.")
                msg['Subject'] = f"Inquiry: Research Position - Thyag Raj"  # Fallback subject
                msg.attach(MIMEText(body.strip(), 'plain'))
        except ValueError:
            print("Warning: Could not parse subject from LLM output. Using default.")
            msg['Subject'] = f"Inquiry: Research Position - Thyag Raj"  # Fallback subject
            msg.attach(MIMEText(body.strip(), 'plain'))

        # Attach CV PDF
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    filename = os.path.basename(attachment_path)
                    part = MIMEApplication(f.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    msg.attach(part)
                    print(f"Attached file: {filename}")
            except Exception as e:
                print(f"Error attaching file {attachment_path}: {e}")
        elif attachment_path:
            print(f"Warning: Attachment file not found at {attachment_path}")

        try:
            self.server.sendmail(self.config.email_address, recipient, msg.as_string())
            print(f"Email sent successfully to {recipient}")
            return True
        except smtplib.SMTPException as e:
            print(f"SMTP Error sending email to {recipient}: {e}")
            return False
        except Exception as e:
            print(f"Failed to send email to {recipient}: {str(e)}")
            return False

    def disconnect(self):
        """Disconnects from the SMTP server."""
        if self.server:
            print("Quitting email server connection.")
            self.server.quit()
            self.server = None