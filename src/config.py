class Config:
    """Loads and holds configuration values."""
    def __init__(self):
        self.google_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")

        # File Paths
        self.csv_path = "/Users/thyag/Desktop/projects/coldmail-generator/mailing list/mailinglist-2 - Sheet1.csv"
        self.cv_attachment_path = "/Users/thyag/Desktop/projects/coldmail-generator/cv-pdf/Thyag_Raj_CV.pdf"
        self.cv_context_path = "/Users/thyag/Desktop/projects/coldmail-generator/cv-texts/Thyag_Raj_CV_extracted.txt"
        self.prompts_dir = "/Users/thyag/Desktop/projects/coldmail-generator/prompts"
        self.system_prompt_path = os.path.join(self.prompts_dir, "system_prompt.txt")
        self.user_prompt_template_path = os.path.join(self.prompts_dir, "user_prompt_template.txt")

        # Email Settings
        self.delay_between_emails = 5  # seconds
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 465

        self.validate()

    def validate(self):
        """Basic validation of essential configuration."""
        if not all([self.google_api_key, self.openai_api_key, self.email_address, self.email_password]):
            raise ValueError("Error: Missing one or more required environment variables (API keys, Email credentials).")