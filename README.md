## cold email generator

an automated system for generating personalized outreach emails to research positions and ai companies using google's gemini ai.

### installation

install required dependencies:

```bash
pip install pandas python-dotenv google-generativeai tqdm
```

configure environment variables in `.env`:

```env
email_address=your.email@gmail.com
email_password=your_gmail_app_password
gemini_api_key=your_gemini_api_key
sender_name="your full name"
email_delay=5
```

### file structure

the system requires your cv in both pdf format at `cv/cv.pdf` and text format at `cv/cv_extracted.txt`. email templates belong in the `prompt-template/` directory. contact information should be prepared in csv format with appropriate columns for each use case.

### execution

run `python email-research.py` for academic positions or `python email-company.py` for company outreach. the system processes your contact list and generates personalized emails based on the provided templates and cv information.

### configuration requirements

gmail authentication requires two-factor authentication with an app password rather than your standard account password. the system includes configurable delays between sends to maintain appropriate sending patterns.

review generated content before transmission to ensure accuracy and appropriateness for your specific outreach objectives.
