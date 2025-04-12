class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        """Generates content based on prompts."""
        pass

class GeminiClient(LLMClient):
    """Client for Google Gemini API."""
    def __init__(self, api_key: str):
        self.model = None
        if not api_key:
            print("Warning: Google API Key not provided. GeminiClient will be inactive.")
            return
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("Google Gemini initialized successfully.")
        except Exception as e:
            print(f"Warning: Failed to initialize Google Gemini: {e}")
            self.model = None

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.model:
            print("Gemini model not available.")
            return None
        try:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error during Gemini API call: {e}")
            return None

class OpenAIClient(LLMClient):
    """Client for OpenAI API."""
    def __init__(self, api_key: str):
        self.client = None
        if not api_key:
            print("Warning: OpenAI API Key not provided. OpenAIClient will be inactive.")
            return
        try:
            self.client = OpenAI(api_key=api_key)
            print("OpenAI client initialized successfully.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")
            self.client = None

    def generate(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.client:
            print("OpenAI client not available.")
            return None
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"Error during OpenAI API call: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with OpenAI: {e}")
            return None