## cold mail generator

### overview  
the cold mail generator is a python application designed to automate the process of sending personalized cold emails to professors. it utilizes advanced language models to generate email content based on provided prompts and professor details. the application is structured in a modular way, allowing for easy maintenance and extension.

### project structure
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
│   └── mailinglist-2 - sheet1.csv
├── cv-pdf
│   └── thyag_raj_cv.pdf
├── cv-texts
│   └── thyag_raj_cv_extracted.txt
├── requirements.txt
└── readme.md
```

### features
- **email generation**: generates personalized emails using language models from google gemini and openai.  
- **data loading**: loads professor data from csv files and context from text files.  
- **email sending**: connects to an smtp server to send emails with attachments.  
- **configuration management**: loads and validates configuration values from environment variables.

### installation
1. clone the repository:
   ```
   git clone <repository-url>
   cd coldmail-generator
   ```
2. install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### usage
1. set up your environment variables in a `.env` file:
   ```
   GEMINI_API_KEY=<your-gemini-api-key>
   OPENAI_API_KEY=<your-openai-api-key>
   EMAIL_ADDRESS=<your-email-address>
   EMAIL_PASSWORD=<your-email-password>
   ```
2. run the application:
   ```
   python main.py
   ```

## contributing
contributions are welcome! please open an issue or submit a pull request for any improvements or bug fixes.

---

Let me know if you want this version saved to a file or formatted for a specific platform like GitHub.
