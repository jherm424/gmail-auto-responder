#!/usr/bin/env python3
"""
Gmail Auto-Responder Main Application
Automated email response system for Gmail accounts
"""

import os
import sys
import time
import yaml
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gmail_auth import GmailAuthenticator
from email_monitor import EmailMonitor
from response_generator import ResponseGenerator

class GmailAutoResponder:
    """Main application class for Gmail auto-responder"""

    def __init__(self, config_file='config/response_rules.yaml'):
        # Load environment variables
        load_dotenv()

        # Setup logging
        self.setup_logging()

        # Load configuration
        self.config = self.load_config(config_file)

        # Initialize components
        self.authenticator = GmailAuthenticator()
        self.gmail_service = None
        self.monitor = None
        self.responder = None

        # Runtime settings
        self.test_mode = os.getenv('TEST_MODE', 'true').lower() == 'true'
        self.draft_mode = os.getenv('DRAFT_MODE', 'true').lower() == 'true'
        self.check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 5))
        self.max_emails_per_run = int(os.getenv('MAX_EMAILS_PER_RUN', 10))

    def setup_logging(self):
        """Configure logging"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/gmail_responder.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger(__name__)

    def load_config(self, config_file):
        """Load response rules configuration"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.logger.info(f"Loaded configuration from {config_file}")
                return config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config: {e}")
            sys.exit(1)

    def initialize(self):
        """Initialize Gmail connection and components"""
        self.logger.info("Initializing Gmail Auto-Responder...")

        # Authenticate with Gmail
        try:
            self.gmail_service = self.authenticator.authenticate()
            self.logger.info("Gmail authentication successful")
        except Exception as e:
            self.logger.error(f"Gmail authentication failed: {e}")
            return False

        # Test connection
        if not self.authenticator.test_connection():
            self.logger.error("Gmail connection test failed")
            return False

        # Initialize monitor and responder
        self.monitor = EmailMonitor(self.gmail_service, self.config)
        self.responder = ResponseGenerator(self.gmail_service)

        if self.test_mode:
            self.logger.warning("🧪 RUNNING IN TEST MODE - No emails will be sent")
        elif self.draft_mode:
            self.logger.info("📝 RUNNING IN DRAFT MODE - Creating drafts instead of sending emails")

        return True

    def process_emails(self):
        """Process new emails and send auto-responses"""
        self.logger.info("Checking for new emails...")

        try:
            # Get unread emails
            emails = self.monitor.get_unread_emails(max_results=self.max_emails_per_run)

            if not emails:
                self.logger.info("No new emails found")
                return

            self.logger.info(f"Found {len(emails)} new emails to process")

            responses_sent = 0

            for email_data in emails:
                try:
                    self.logger.info(f"Processing email from: {email_data['from']}")
                    self.logger.info(f"Subject: {email_data['subject']}")

                    # Check if email should get auto-response
                    should_respond, rule_name, template_name = self.monitor.should_auto_respond(
                        email_data, self.config
                    )

                    if should_respond:
                        if self.draft_mode:
                            self.logger.info(f"Creating draft with rule: {rule_name}, template: {template_name}")
                        else:
                            self.logger.info(f"Auto-responding with rule: {rule_name}, template: {template_name}")

                        # Generate response
                        response_content = self.responder.generate_response(
                            email_data, template_name
                        )

                        # Create draft or send response based on mode
                        if self.draft_mode and not self.test_mode:
                            # Create draft
                            if self.responder.create_draft_response(email_data, response_content, False):
                                responses_sent += 1
                                self.monitor.mark_as_processed(email_data['id'])
                            else:
                                self.logger.error(f"Failed to create draft for {email_data['from']}")
                        else:
                            # Use legacy send method (which now creates drafts too)
                            if self.responder.send_response(email_data, response_content, self.test_mode):
                                responses_sent += 1
                                self.monitor.mark_as_processed(email_data['id'])
                            else:
                                self.logger.error(f"Failed to create response for {email_data['from']}")

                    else:
                        self.logger.info("Email does not match auto-response rules")
                        self.monitor.mark_as_processed(email_data['id'])

                except Exception as e:
                    self.logger.error(f"Error processing email {email_data.get('id', 'unknown')}: {e}")

            if self.draft_mode and not self.test_mode:
                self.logger.info(f"Processed {len(emails)} emails, created {responses_sent} drafts")
            else:
                self.logger.info(f"Processed {len(emails)} emails, sent {responses_sent} responses")

            # Update last check time
            self.monitor.update_last_check()

        except Exception as e:
            self.logger.error(f"Error during email processing: {e}")

    def run_once(self):
        """Run one cycle of email checking and responding"""
        if not self.initialize():
            self.logger.error("Initialization failed")
            return False

        self.process_emails()
        return True

    def run_continuously(self):
        """Run continuously, checking emails at intervals"""
        if not self.initialize():
            self.logger.error("Initialization failed")
            return

        self.logger.info(f"Starting continuous monitoring (checking every {self.check_interval} minutes)")

        try:
            while True:
                self.process_emails()

                # Wait for next check
                self.logger.info(f"Waiting {self.check_interval} minutes until next check...")
                time.sleep(self.check_interval * 60)

        except KeyboardInterrupt:
            self.logger.info("Stopping Gmail Auto-Responder (Ctrl+C pressed)")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")

    def validate_setup(self):
        """Validate configuration and templates"""
        self.logger.info("Validating setup...")

        # Check credentials file
        credentials_path = self.authenticator.credentials_path
        if not os.path.exists(credentials_path):
            self.logger.error(f"Gmail credentials file not found: {credentials_path}")
            self.logger.info("Download credentials.json from Google Cloud Console and place in config/")
            return False

        # Initialize responder for validation
        if not self.responder:
            self.responder = ResponseGenerator(None)  # Don't need service for validation

        # Validate templates
        templates_dir = 'templates'
        rules = self.config.get('rules', [])

        for rule in rules:
            template_name = rule.get('response_template')
            if template_name:
                is_valid, message = self.responder.validate_template(template_name)
                if not is_valid:
                    self.logger.error(f"Template validation failed: {message}")
                    return False

        self.logger.info("✅ Setup validation passed")
        return True

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Auto-Responder')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--validate', action='store_true', help='Validate setup and exit')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode (no emails sent)')
    parser.add_argument('--draft-mode', action='store_true', help='Create drafts instead of sending emails')
    parser.add_argument('--send-mode', action='store_true', help='Send emails directly (overrides draft mode)')

    args = parser.parse_args()

    # Create app instance
    app = GmailAutoResponder()

    # Override modes if specified
    if args.test_mode:
        app.test_mode = True
    if args.draft_mode:
        app.draft_mode = True
    if args.send_mode:
        app.draft_mode = False

    if args.validate:
        # Validate setup
        if app.validate_setup():
            print("✅ Setup validation passed")
            sys.exit(0)
        else:
            print("❌ Setup validation failed")
            sys.exit(1)

    elif args.once:
        # Run once
        if app.run_once():
            print("✅ Single run completed successfully")
        else:
            print("❌ Single run failed")
            sys.exit(1)

    else:
        # Run continuously
        app.run_continuously()

if __name__ == '__main__':
    main()