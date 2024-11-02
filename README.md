# Academic Cold Email Generator

An automated tool for sending personalized cold emails to professors for research positions. This tool uses OpenAI's GPT to generate customized emails based on your profile and each professor's research interests.

## Features

- 📧 Automated email generation using OpenAI's GPT
- 🎯 Personalization based on professor's research interests
- 📎 Support for CV attachments
- 📊 Bulk processing using Excel spreadsheets
- ⏱️ Rate limiting to prevent email blocking
- 🔒 Secure credential management

## Prerequisites

- Python 3.7+
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833?hl=en) enabled
- OpenAI API key
- Excel file with professor details

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/academic-cold-email-generator.git
cd academic-cold-email-generator
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password
OPENAI_API_KEY=your-openai-api-key
```

## Setup

### 1. Gmail App Password
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Scroll down and select "App passwords"
4. Create a new app password for "Mail"
5. Copy the generated password to your `.env` file

### 2. OpenAI API Key
1. Create an account on [OpenAI](https://platform.openai.com/)
2. Generate an API key
3. Copy the key to your `.env` file

### 3. Professor Details Excel File
Create an Excel file with the following columns:
- `name`: Professor's name
- `university`: University name
- `email`: Professor's email address
- `research_interests`: Brief description of their research interests

Example format:
| name | university | email | research_interests |
|------|------------|-------|-------------------|
| Dr. Jane Smith | Stanford University | jane@stanford.edu | Machine Learning, NLP |

## Configuration

Update the `user_details` dictionary in the script with your information:

```python
user_details = {
    "name": "Your Name",
    "degree": "B.Tech/M.Tech/etc",
    "university": "Your University",
    "research_interests": "Your research interests",
    "experience": """
    • Project/Research Experience 1
    • Project/Research Experience 2
    • Relevant coursework or thesis
    """
}
```

## Usage

1. Update the paths in the script:
```python
paths = {
    "excel_file": "path/to/professors_list.xlsx",
    "cv_file": "path/to/your/cv.pdf"  # Optional
}
```

2. Run the script:
```bash
python cold_email_generator.py
```

The script will:
1. Read professor details from the Excel file
2. Generate personalized emails using GPT
3. Send emails with your CV attached
4. Wait for a specified delay between emails
5. Log the success/failure of each email

## Customization

### Email Template
The email template can be customized by modifying the `_generate_system_prompt` method in the `ColdEmailGenerator` class. The current template includes:
- Introduction
- Research experience (bullet points)
- Research interest alignment
- Closing paragraph

### Rate Limiting
Adjust the delay between emails by modifying the `delay` parameter in `process_professors_list`:
```python
process_professors_list(excel_path, email_generator, user_details, cv_path, delay=5)  # 5 seconds delay
```

## Best Practices

1. Start with a small test batch of emails
2. Review the generated emails before sending them in bulk
3. Keep delays between emails to avoid triggering spam filters
4. Ensure your CV is up-to-date and in PDF format
5. Double-check all professor details in the Excel file
6. Make sure your Gmail account has enough sending quota

## Troubleshooting

### Common Issues:

1. **Gmail Authentication Error**
   - Verify your app password is correct
   - Ensure 2FA is enabled on your Google account
   - Check if less secure app access is disabled

2. **OpenAI API Error**
   - Verify your API key
   - Check your OpenAI account balance
   - Ensure you're using a supported GPT model

3. **Excel File Errors**
   - Verify the column names match exactly
   - Check for missing or malformed data
   - Ensure the file path is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational purposes only. Be sure to follow all applicable institutional policies and email regulations when sending cold emails.

---
Made with ❤️ by [Your Name]
