"""
Response Generator Module
Generates and sends automated email responses
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.errors import HttpError

class ResponseGenerator:
    """Generate and send automated email responses"""

    def __init__(self, gmail_service, templates_dir='templates'):
        self.service = gmail_service
        self.templates_dir = templates_dir

    def load_template(self, template_name):
        """Load email template from file"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.txt")

        if not os.path.exists(template_path):
            # Fallback to general template
            template_path = os.path.join(self.templates_dir, "general.txt")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template {template_name}: {e}")
            return self._get_fallback_template()

    def _get_fallback_template(self):
        """Fallback template if file loading fails"""
        return """Subject: Re: {original_subject}

Hello,

Thank you for your email. I have received your message and will respond as soon as possible.

Best regards,
Josh Herreman

---
This is an automated response."""

    def generate_response(self, original_email, template_name):
        """Generate response email from template"""
        template = self.load_template(template_name)

        # Replace template variables
        response_content = template.format(
            original_subject=original_email['subject'],
            sender_name=self._extract_sender_name(original_email['from']),
            current_date=self._get_current_date()
        )

        return response_content

    def _extract_sender_name(self, from_field):
        """Extract sender name from email 'from' field"""
        # Try to extract name from "Name <email@domain.com>" format
        if '<' in from_field:
            name = from_field.split('<')[0].strip()
            if name:
                return name

        # Fallback to the part before @ in email
        email_part = from_field.split('<')[-1].replace('>', '').strip()
        return email_part.split('@')[0]

    def _get_current_date(self):
        """Get current date in a readable format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")

    def send_response(self, original_email, response_content, test_mode=True):
        """Send automated response email"""
        try:
            # Parse response content to extract subject and body
            lines = response_content.strip().split('\n')
            subject_line = lines[0] if lines[0].startswith('Subject:') else f"Re: {original_email['subject']}"
            subject = subject_line.replace('Subject:', '').strip()

            # Find where body starts (after empty line)
            body_start = 1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '':
                    body_start = i + 1
                    break

            body = '\n'.join(lines[body_start:])

            if test_mode:
                print(f"🧪 TEST MODE - Would send response:")
                print(f"To: {original_email['from']}")
                print(f"Subject: {subject}")
                print(f"Body preview: {body[:100]}...")
                return True

            # Create email message
            message = MIMEText(body)
            message['to'] = original_email['from']
            message['subject'] = subject

            # Add reference headers for threading
            if 'id' in original_email:
                message['In-Reply-To'] = f"<{original_email['id']}>"
                message['References'] = f"<{original_email['id']}>"

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send email
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message, 'threadId': original_email.get('thread_id')}
            ).execute()

            print(f"✅ Response sent successfully to {original_email['from']}")
            return True

        except HttpError as e:
            print(f"❌ Error sending response: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending response: {e}")
            return False

    def validate_template(self, template_name):
        """Validate that template exists and is properly formatted"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.txt")

        if not os.path.exists(template_path):
            return False, f"Template file not found: {template_path}"

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for required format
            if not content.strip().startswith('Subject:'):
                return False, "Template must start with 'Subject:' line"

            return True, "Template is valid"

        except Exception as e:
            return False, f"Error reading template: {e}"