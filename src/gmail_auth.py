"""
Gmail API Authentication Module
Handles OAuth 2.0 authentication for Gmail API access
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailAuthenticator:
    """Handle Gmail API authentication and service creation"""

    def __init__(self, credentials_path='config/credentials.json', token_path='config/token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    def authenticate(self):
        """
        Authenticate with Gmail API using OAuth 2.0
        Returns Gmail service object
        """
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, go through OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail API credentials file not found at {self.credentials_path}. "
                        "Please download your credentials from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        return self.service

    def get_service(self):
        """Get authenticated Gmail service"""
        if not self.service:
            return self.authenticate()
        return self.service

    def test_connection(self):
        """Test Gmail API connection"""
        try:
            service = self.get_service()
            # Try to get user profile to test connection
            profile = service.users().getProfile(userId='me').execute()
            print(f"✅ Successfully connected to Gmail for: {profile['emailAddress']}")
            return True
        except Exception as e:
            print(f"❌ Gmail API connection failed: {e}")
            return False