class ColdMailer:
    """Orchestrates the cold emailing process."""
    def __init__(self, config: Config):
        self.config = config
        self.data_loader = DataLoader()
        self.gemini_client = GeminiClient(config.google_api_key)
        self.openai_client = OpenAIClient(config.openai_api_key)
        self.email_generator = EmailGenerator(self.gemini_client, self.openai_client)  # Gemini as primary
        self.email_sender = EmailSender(config)

    def run(self):
        """Executes the main cold emailing workflow."""
        print("Starting Cold Mail Generator...")

        # Load prompts and context
        system_prompt = self.data_loader.load_text_file(self.config.system_prompt_path)
        user_prompt_template = self.data_loader.load_text_file(self.config.user_prompt_template_path)
        cv_context = self.data_loader.load_text_file(self.config.cv_context_path)

        if not all([system_prompt, user_prompt_template, cv_context]):
            print("Error: Failed to load necessary prompt or context files. Exiting.")
            return

        # Load professor data
        professor_list = self.data_loader.load_professor_list(self.config.csv_path)
        if not professor_list:
            print("Error: Failed to load professor list. Exiting.")
            return

        # Connect to email server
        if not self.email_sender.connect():
            print("Error: Failed to connect to email server. Exiting.")
            return

        # Process and send emails
        try:
            for professor in tqdm(professor_list, desc="Processing professors", unit="email"):
                print("-" * 30)
                prof_name = professor.get('name', 'N/A')
                prof_email = professor.get('email')
                prof_interests = professor.get('research_interests')
                print(f"Processing: {prof_name} ({prof_email})")

                # Validate professor data
                if pd.isna(prof_email) or not isinstance(prof_email, str) or '@' not in prof_email:
                    print(f"Skipping {prof_name} due to invalid or missing email.")
                    continue
                if pd.isna(prof_interests):
                    print(f"Warning: Missing research interests for {prof_name}. Email might be less personalized.")
                    # Consider skipping if interests are mandatory: continue

                # Generate email content
                email_body = self.email_generator.generate_email(
                    system_prompt,
                    user_prompt_template,
                    professor,
                    cv_context
                )

                if email_body:
                    # Send the email
                    self.email_sender.send(
                        prof_email,
                        email_body,
                        self.config.cv_attachment_path
                    )
                else:
                    print(f"Skipping email to {prof_email} due to generation failure.")

                # Wait before sending the next email
                print(f"Waiting for {self.config.delay_between_emails} seconds...")
                time.sleep(self.config.delay_between_emails)

        except Exception as e:
            print(f"\nAn unexpected error occurred during processing: {str(e)}")
        finally:
            self.email_sender.disconnect()
            print("-" * 30)
            print("Script finished.")
            print("Note: Ensure to check your email account for sent items and any potential issues.")
            print("-" * 30)