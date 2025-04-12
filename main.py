from src.config import Config
from src.mailer import ColdMailer

if __name__ == "__main__":
    try:
        app_config = Config()
        mailer = ColdMailer(app_config)
        mailer.run()
    except ValueError as e:  # Catch config validation errors
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred at the top level: {e}")

    print("Goodbye!")
    print("-" * 30)