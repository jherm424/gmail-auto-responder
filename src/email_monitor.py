"""
Email Monitoring Module
Monitors Gmail inbox for new emails and triggers auto-responses
"""

import base64
import email
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from googleapiclient.errors import HttpError

class EmailMonitor:
    """Monitor Gmail inbox for new emails requiring auto-responses"""

    def __init__(self, gmail_service, config):
        self.service = gmail_service
        self.config = config
        self.processed_emails = set()  # Track processed email IDs
        self.last_check = datetime.now() - timedelta(minutes=5)  # Start with 5min lookback

    def get_unread_emails(self, max_results=50):
        """
        Fetch unread emails from Gmail inbox
        Returns list of email message objects
        """
        try:
            # Query for unread emails
            query = 'is:unread in:inbox'

            # Add time filter to only check recent emails
            time_filter = self.last_check.strftime('%Y/%m/%d')
            query += f' after:{time_filter}'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            # Get detailed message data
            email_list = []
            for message in messages:
                try:
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()

                    # Skip if already processed
                    if message['id'] in self.processed_emails:
                        continue

                    email_data = self._parse_email(msg)
                    if email_data:
                        email_list.append(email_data)

                except HttpError as e:
                    print(f"Error fetching email {message['id']}: {e}")
                    continue

            return email_list

        except HttpError as e:
            print(f"Error fetching emails: {e}")
            return []

    def _parse_email(self, message):
        """Parse Gmail message into structured email data"""
        try:
            headers = message['payload'].get('headers', [])

            # Extract headers
            email_data = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'subject': '',
                'from': '',
                'to': '',
                'date': '',
                'body': '',
                'has_attachments': False
            }

            for header in headers:
                name = header['name'].lower()
                value = header['value']

                if name == 'subject':
                    email_data['subject'] = value
                elif name == 'from':
                    email_data['from'] = value
                elif name == 'to':
                    email_data['to'] = value
                elif name == 'date':
                    email_data['date'] = value

            # Extract email body
            email_data['body'] = self._extract_body(message['payload'])

            # Check for attachments
            email_data['has_attachments'] = self._has_attachments(message['payload'])

            return email_data

        except Exception as e:
            print(f"Error parsing email: {e}")
            return None

    def _extract_body(self, payload):
        """Extract email body from payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        else:
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body

    def _has_attachments(self, payload):
        """Check if email has attachments"""
        if 'parts' in payload:
            for part in payload['parts']:
                if 'filename' in part and part['filename']:
                    return True
        return False

    def should_auto_respond(self, email_data, rules):
        """
        Check if email should receive an auto-response based on rules
        Returns (should_respond: bool, rule_name: str, template: str)
        """
        # Check exclusion rules first
        if self._is_excluded(email_data, rules.get('exclusions', {})):
            return False, None, None

        # Check each rule in priority order
        for rule in sorted(rules.get('rules', []), key=lambda x: x.get('priority', 10)):
            if self._matches_rule(email_data, rule):
                return True, rule['name'], rule['response_template']

        return False, None, None

    def _is_excluded(self, email_data, exclusions):
        """Check if email matches exclusion criteria"""

        # Check excluded from addresses
        for excluded_addr in exclusions.get('from_addresses', []):
            if excluded_addr.lower() in email_data['from'].lower():
                return True

        # Check excluded subjects
        for excluded_subject in exclusions.get('subject_contains', []):
            if excluded_subject.lower() in email_data['subject'].lower():
                return True

        # Check excluded domains
        from_email = email_data['from']
        domain_match = re.search(r'@([^>]+)', from_email)
        if domain_match:
            domain = domain_match.group(1).strip()
            if domain in exclusions.get('from_domain', []):
                return True

        return False

    def _matches_rule(self, email_data, rule):
        """Check if email matches rule conditions"""
        conditions = rule.get('conditions', [])

        # Empty conditions match everything (catch-all rule)
        if not conditions:
            return True

        # Check subject contains
        if 'subject_contains' in rule['conditions']:
            subject_keywords = rule['conditions']['subject_contains']
            if not any(keyword.lower() in email_data['subject'].lower()
                      for keyword in subject_keywords):
                return False

        # Check from domain exclusions
        if 'from_domain_not' in rule['conditions']:
            excluded_domains = rule['conditions']['from_domain_not']
            from_email = email_data['from']
            domain_match = re.search(r'@([^>]+)', from_email)
            if domain_match:
                domain = domain_match.group(1).strip()
                if domain in excluded_domains:
                    return False

        # Check attachment requirement
        if 'has_attachments' in rule['conditions']:
            required_attachments = rule['conditions']['has_attachments']
            if email_data['has_attachments'] != required_attachments:
                return False

        return True

    def mark_as_processed(self, email_id):
        """Mark email as processed to avoid duplicate responses"""
        self.processed_emails.add(email_id)

    def update_last_check(self):
        """Update the last check timestamp"""
        self.last_check = datetime.now()