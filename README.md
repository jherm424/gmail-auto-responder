# Gmail Auto-Responder

An automated email response system for your Google Gmail account using Python and the Gmail API.

## Features
- Monitor incoming emails automatically
- Intelligent response based on email content
- **Creates drafts instead of sending emails automatically** (for safety)
- Customizable response templates
- Safe testing mode
- Comprehensive logging
- Support for multiple response rules

## Project Structure
```
gmail-auto-responder/
├── src/                    # Main application code
├── config/                 # Configuration files
├── templates/              # Email response templates
├── logs/                   # Application logs
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── setup.py              # Installation script
```

## Security Notes
- Uses OAuth 2.0 for secure Gmail API access
- **Creates drafts by default - never sends emails automatically**
- No passwords stored in plain text
- All credentials handled securely
- Local execution only
- You review and send drafts manually

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Set up Gmail API credentials
3. Configure response templates
4. Run in test mode first: `python src/main.py --test-mode`
5. Run in draft mode: `python src/main.py --draft-mode`
6. Check Gmail drafts folder to review generated responses

## Development
This project follows security best practices and never exposes sensitive information.