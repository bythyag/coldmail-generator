class EmailGenerator:
    """Generates email content using LLM clients with fallback."""
    def __init__(self, primary_client: LLMClient | None, fallback_client: LLMClient | None):
        self.primary_client = primary_client
        self.fallback_client = fallback_client
        if not primary_client and not fallback_client:
             raise ValueError("Error: At least one LLM client must be provided and initialized.")

    def generate_email(self, system_prompt: str, user_prompt_template: str, professor_details: dict, cv_context: str) -> str | None:
        """Generates personalized email content."""
        user_prompt = user_prompt_template.format(
            professor_name=professor_details.get('name', 'N/A'),
            university=professor_details.get('university', 'N/A'),
            research_interests=professor_details.get('research_interests', 'N/A'),
            cv_context=cv_context
        )

        email_content = None
        if self.primary_client:
            print("Attempting email generation with primary client...")
            email_content = self.primary_client.generate(system_prompt, user_prompt)
            if email_content:
                print(f"Generated email using {type(self.primary_client).__name__}.")
                return email_content
            else:
                 print(f"{type(self.primary_client).__name__} failed or is unavailable.")

        if self.fallback_client:
            print("Falling back to secondary client...")
            email_content = self.fallback_client.generate(system_prompt, user_prompt)
            if email_content:
                print(f"Generated email using {type(self.fallback_client).__name__}.")
                return email_content
            else:
                print(f"{type(self.fallback_client).__name__} failed or is unavailable.")

        print("Error: All configured LLM clients failed to generate email content.")
        return None