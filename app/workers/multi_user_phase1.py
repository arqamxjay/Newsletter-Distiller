"""
Phase 1: Multi-User Access Layer
Gmail API authentication and message fetching for each user
"""

import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from googleapiclient import discovery
from app import db
from app.models import GmailToken, Newsletter

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


class MultiUserGmailAccessLayer:
    """Handles per-user Gmail OAuth and message fetching."""
    
    def __init__(self, user):
        """
        Initialize for a specific user.
        
        Args:
            user: User object from database
        """
        self.user = user
        self.gmail_token = user.gmail_token
        self.newsletter_label = user.preferences.newsletter_label if user.preferences else 'To-Summarize'
        self.service = self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate using stored OAuth token.
        Automatically refreshes if expired.
        """
        if not self.gmail_token:
            raise ValueError(f"No Gmail token found for user {self.user.email}")
        
        try:
            # Create credentials from stored token
            creds = Credentials(
                token=self.gmail_token.access_token,
                refresh_token=self.gmail_token.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=SCOPES
            )
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update token in database
                self.gmail_token.access_token = creds.token
                self.gmail_token.token_expires_at = creds.expiry
                db.session.commit()
            
            logger.info(f"Gmail authentication successful for {self.user.email}")
            return discovery.build('gmail', 'v1', credentials=creds)
        
        except RefreshError as e:
            logger.error(f"Token refresh failed for {self.user.email}: {e}")
            raise
        except Exception as e:
            logger.error(f"Gmail authentication failed for {self.user.email}: {e}")
            raise
    
    def fetch_newsletters(self):
        """
        Fetch unread newsletters with the specified label.
        
        Returns:
            List of newsletter objects
        """
        try:
            # Get label ID
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            label_id = None
            for label in labels:
                if label['name'] == self.newsletter_label:
                    label_id = label['id']
                    break
            
            if not label_id:
                logger.warning(f"Label '{self.newsletter_label}' not found for {self.user.email}")
                return []
            
            # Fetch unread messages with label
            query = f"label:{label_id} is:unread"
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} newsletters for {self.user.email}")
            
            newsletters = []
            for msg in messages:
                try:
                    newsletter = self._parse_message(msg['id'])
                    if newsletter:
                        newsletters.append(newsletter)
                except Exception as e:
                    logger.error(f"Error parsing message {msg['id']}: {e}")
            
            return newsletters
        
        except Exception as e:
            logger.error(f"Error fetching newsletters for {self.user.email}: {e}")
            return []
    
    def _parse_message(self, msg_id):
        """Parse a Gmail message into a newsletter object."""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            
            # Get body
            body = self._get_message_body(msg['payload'])
            
            # Create or update newsletter record
            newsletter = Newsletter.query.filter_by(
                user_id=self.user.id,
                gmail_message_id=msg_id
            ).first()
            
            if not newsletter:
                newsletter = Newsletter(
                    user_id=self.user.id,
                    gmail_message_id=msg_id,
                    original_subject=subject,
                    original_content=body,
                    status='pending'
                )
                db.session.add(newsletter)
                db.session.commit()
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': from_addr,
                'body': body,
                'db_id': newsletter.id
            }
        
        except Exception as e:
            logger.error(f"Error parsing message {msg_id}: {e}")
            return None
    
    def _get_message_body(self, payload):
        """Extract body from Gmail message payload."""
        if 'parts' in payload:
            return self._get_body_from_parts(payload['parts'])
        
        if 'body' in payload and 'data' in payload['body']:
            import base64
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return ''
    
    def _get_body_from_parts(self, parts):
        """Recursively extract body from message parts."""
        body = ''
        for part in parts:
            if part['mimeType'] == 'text/plain':
                if 'body' in part and 'data' in part['body']:
                    import base64
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                if 'body' in part and 'data' in part['body']:
                    import base64
                    body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                body += self._get_body_from_parts(part['parts'])
        
        return body
    
    def mark_as_read(self, msg_id):
        """Mark a message as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except Exception as e:
            logger.error(f"Error marking message {msg_id} as read: {e}")
