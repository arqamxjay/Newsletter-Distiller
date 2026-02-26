"""
Phase 4: The Delivery System
Digest compilation and email transmission
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)


class DeliverySystem:
    """Compiles digests and sends via email."""
    
    def __init__(self):
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
    
    def compile_digest(self, newsletters):
        """
        Compiles all newsletter summaries into a single HTML digest.
        """
        try:
            digest_html = self._create_html_template(newsletters)
            logger.info("Digest compiled successfully")
            return digest_html
        
        except Exception as e:
            logger.error(f"Error compiling digest: {str(e)}")
            raise
    
    def _create_html_template(self, newsletters):
        """
        Creates an HTML template with newsletter summaries.
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        
        # Build newsletter sections
        newsletter_sections = ""
        for nl in newsletters:
            section = self._create_newsletter_section(nl)
            newsletter_sections += section
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 5px 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            padding: 20px;
        }}
        .newsletter {{
            margin-bottom: 30px;
            border-left: 4px solid #667eea;
            padding-left: 20px;
        }}
        .newsletter-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .newsletter-source {{
            font-weight: 600;
            color: #667eea;
            font-size: 16px;
        }}
        .newsletter-subject {{
            color: #555;
            font-size: 14px;
            margin-bottom: 8px;
        }}
        .summary {{
            margin: 12px 0;
            color: #444;
            font-size: 14px;
            line-height: 1.8;
        }}
        .summary li {{
            margin-bottom: 8px;
        }}
        .summary ul {{
            margin: 8px 0;
            padding-left: 20px;
        }}
        .read-more {{
            margin-top: 10px;
        }}
        .read-more a {{
            color: #667eea;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
        }}
        .read-more a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            background-color: #f9f9f9;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #eee;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📨 Your Daily Digest</h1>
            <p>{date_str}</p>
        </div>
        
        <div class="content">
            {newsletter_sections}
        </div>
        
        <div class="footer">
            <p>Newsletter Distiller • Automated intelligence summary</p>
            <p><a href="#">Manage preferences</a></p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _create_newsletter_section(self, newsletter):
        """Creates an HTML section for a single newsletter."""
        sender = newsletter.get('sender', 'Unknown Source')
        subject = newsletter.get('subject', '')
        summary = newsletter.get('summary', [])
        links = newsletter.get('links', [])
        
        # Build summary bullets
        summary_html = "<ul>"
        for bullet in summary:
            summary_html += f"<li>{bullet}</li>"
        summary_html += "</ul>"
        
        # Build links
        links_html = ""
        if links:
            links_html = '<div class="read-more">'
            for link in links[:3]:  # Show top 3 links
                text = link.get('text', 'Read more')[:50]  # Truncate long text
                url = link.get('url', '#')
                links_html += f'<a href="{url}" target="_blank">→ {text}</a><br>'
            links_html += '</div>'
        
        section = f"""
        <div class="newsletter">
            <div class="newsletter-header">
                <span class="newsletter-source">{sender}</span>
            </div>
            {f'<div class="newsletter-subject">{subject}</div>' if subject else ''}
            <div class="summary">
                {summary_html}
            </div>
            {links_html}
        </div>
        """
        
        return section
    
    def send_digest(self, html_content):
        """
        Sends the compiled digest via Gmail SMTP.
        """
        try:
            if not self.app_password:
                logger.warning(
                    "GMAIL_APP_PASSWORD not set. Skipping email send. "
                    "See README for setup instructions."
                )
                return False
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = os.getenv(
                'DIGEST_SUBJECT',
                'Your Daily Newsletter Digest'
            )
            message['From'] = self.sender_email
            message['To'] = self.recipient_email
            
            # Attach HTML
            part = MIMEText(html_content, 'html')
            message.attach(part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.sendmail(
                    self.sender_email,
                    self.recipient_email,
                    message.as_string()
                )
            
            logger.info(f"Digest sent to {self.recipient_email}")
            return True
        
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "SMTP authentication failed. Check SENDER_EMAIL and GMAIL_APP_PASSWORD."
            )
            raise
        except Exception as e:
            logger.error(f"Error sending digest: {str(e)}")
            raise
