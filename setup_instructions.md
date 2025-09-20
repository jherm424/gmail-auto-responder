# Gmail Auto-Responder Setup Instructions

## Prerequisites
- Python 3.7 or higher
- Gmail account
- Google Cloud Project with Gmail API enabled

## Step 1: Google Cloud Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Gmail API**
   - In the console, go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it

3. **Create Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials file as `credentials.json`

## Step 2: Project Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/jherm424/gmail-auto-responder.git
   cd gmail-auto-responder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup configuration**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Place your Google credentials
   mkdir -p config
   mv ~/Downloads/credentials.json config/
   ```

4. **Edit configuration files**
   - Edit `.env` file with your preferences
   - Modify `config/response_rules.yaml` for your response rules
   - Customize templates in `templates/` directory

## Step 3: Testing

1. **Validate setup**
   ```bash
   python src/main.py --validate
   ```

2. **Test run (no emails sent)**
   ```bash
   python src/main.py --once --test-mode
   ```

3. **Single run (creates drafts)**
   ```bash
   python src/main.py --once --draft-mode
   ```

4. **Single run (actually sends emails - use with caution)**
   ```bash
   python src/main.py --once --send-mode
   ```

## Step 4: Production Deployment

1. **Run continuously (creates drafts)**
   ```bash
   python src/main.py --draft-mode
   ```

2. **Run continuously (actually sends emails - use with extreme caution)**
   ```bash
   python src/main.py --send-mode
   ```

2. **Run as system service (optional)**
   - Create systemd service file
   - Enable auto-start on boot

## Important Security Notes

⚠️ **Security Considerations:**
- **Application creates drafts by default - never sends emails automatically**
- Keep `credentials.json` and `token.json` secure
- Never commit credentials to version control
- Use test mode first to verify behavior
- Review all drafts in Gmail before sending
- Review response templates carefully
- Monitor logs for unexpected behavior
- Use `--send-mode` only when absolutely certain

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Ensure `config/credentials.json` exists
   - Check file permissions

2. **"Authentication failed"**
   - Re-download credentials from Google Cloud
   - Delete `config/token.json` and re-authenticate

3. **"No emails found"**
   - Check Gmail API quotas
   - Verify account has unread emails
   - Check response rules configuration

### Getting Help

- Check logs in `logs/gmail_responder.log`
- Review configuration in `config/response_rules.yaml`
- Test individual components using validation mode

## Configuration Examples

### Custom Response Rule
```yaml
- name: "custom_rule"
  conditions:
    - subject_contains: ["urgent", "important"]
    - from_domain_not: ["spam.com"]
  response_template: "urgent_response"
  priority: 1
```

### Custom Template
Create `templates/urgent_response.txt`:
```
Subject: Re: {original_subject} - Urgent Response

Hello,

I've received your urgent message and will prioritize a response.

Best regards,
Your Name
```