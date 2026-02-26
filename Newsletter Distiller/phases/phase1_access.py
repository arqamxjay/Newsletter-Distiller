"""
Phase 1: The Access Layer
Gmail API authentication and message fetching
"""

import os
import logging
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class GmailAccessLayer:
    """Handles OAuth 2.0 authentication and Gmail message fetching."""
    
    def __init__(self):
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')
        self.newsletter_label = os.getenv('NEWSLETTER_LABEL', 'To-Summarize')
        
        self.service = self._authenticate()
    
    def _authenticate(self):
        """
        Authenticates with Gmail API using OAuth 2.0.
        Creates or refreshes the token.pickle file.
        """
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new credentials
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"{self.credentials_file} not found. "
                    "Download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save token for next run
        with open(self.token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        logger.info("Gmail authentication successful")
        
        return discovery.build('gmail', 'v1', credentials=creds)
    
    def fetch_newsletters(self):
        """
        Fetches all unread newsletters with the specified label.
        Returns a list of newsletter objects with metadata.
        """
        try:
            # Get label ID for the newsletter label
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            label_id = None
            for label in labels:
                if label['name'] == self.newsletter_label:
                    label_id = label['id']
                    break
            
            if not label_id:
                logger.warning(
                    f"Label '{self.newsletter_label}' not found. "
                    "Please create this label in Gmail."
                )
                return []
            
            # Query for unread messages with the label
            query = f'label:{self.newsletter_label} is:unread'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10  # Adjust as needed
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread newsletters")
            
            # Fetch full message details
            newsletters = []
            for message in messages:
                full_message = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                newsletter = self._parse_message(full_message)
                newsletters.append(newsletter)
            
            return newsletters
        
        except Exception as e:
            logger.error(f"Error fetching newsletters: {str(e)}")
            return []
    
    def _parse_message(self, message):
        """Extracts relevant data from a Gmail message."""
        headers = message['payload']['headers']
        
        # Extract headers
        subject = next(
            (h['value'] for h in headers if h['name'] == 'Subject'),
            'No Subject'
        )
        sender = next(
            (h['value'] for h in headers if h['name'] == 'From'),
            'Unknown Sender'
        )
        date = next(
            (h['value'] for h in headers if h['name'] == 'Date'),
            'Unknown Date'
        )
        
        # Extract body
        body = self._get_message_body(message)
        
        return {
            'id': message['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'processed': False
        }
    
    def _get_message_body(self, message):
        """Extracts the body from a Gmail message (handles multipart)."""
        try:
            if 'parts' in message['payload']:
                # Multipart message
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        if 'data' in part['body']:
                            import base64
                            return base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8')
                    elif part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            import base64
                            return base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8')
            else:
                # Simple message
                if 'data' in message['payload']['body']:
                    import base64
                    return base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting message body: {str(e)}")
        
        return ""
    
    def mark_as_processed(self, newsletters):
        """
        Marks newsletters as read after processing.
        Optionally adds a 'Processed' label.
        """
        try:
            for newsletter in newsletters:
                # Remove UNREAD label
                self.service.users().messages().modify(
                    userId='me',
                    id=newsletter['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            
            logger.info(f"Marked {len(newsletters)} newsletters as read")
        
        except Exception as e:
            logger.error(f"Error marking newsletters as processed: {str(e)}")
