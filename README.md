## Cold Mail Generator

### Overview
The Cold Mail Generator is a Python application designed to automate the process of sending personalized cold emails to professors. It utilizes advanced language models to generate email content based on provided prompts and professor details. The application is structured in a modular way, allowing for easy maintenance and extension.

### Project Structure
```
coldmail-generator
├── src
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── email_generator.py
│   ├── email_sender.py
│   ├── llm_clients.py
│   └── mailer.py
├── main.py
├── prompts
│   ├── system_prompt.txt
│   └── user_prompt_template.txt
├── mailing list
│   └── mailinglist-2 - Sheet1.csv
├── cv-pdf
│   └── Thyag_Raj_CV.pdf
├── cv-texts
│   └── Thyag_Raj_CV_extracted.txt
├── requirements.txt
└── README.md
```

### Features
- **Email Generation**: Generates personalized emails using language models from Google Gemini and OpenAI.
- **Data Loading**: Loads professor data from CSV files and context from text files.
- **Email Sending**: Connects to an SMTP server to send emails with attachments.
- **Configuration Management**: Loads and validates configuration values from environment variables.

### Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd coldmail-generator
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Usage
1. Set up your environment variables in a `.env` file:
   ```
   GEMINI_API_KEY=<your-gemini-api-key>
   OPENAI_API_KEY=<your-openai-api-key>
   EMAIL_ADDRESS=<your-email-address>
   EMAIL_PASSWORD=<your-email-password>
   ```
2. Run the application:
   ```
   python main.py
   ```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.