"""
Phase 2: The Cleaning Engine
HTML sanitization and text extraction
"""

import re
import logging
from bs4 import BeautifulSoup
import os

logger = logging.getLogger(__name__)


class CleaningEngine:
    """Sanitizes newsletter HTML and extracts clean text and links."""
    
    def __init__(self):
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
    
    def clean_all(self, newsletters):
        """Cleans all newsletters and returns processed list."""
        cleaned = []
        for newsletter in newsletters:
            cleaned_newsletter = self.clean_single(newsletter)
            cleaned.append(cleaned_newsletter)
        return cleaned
    
    def clean_single(self, newsletter):
        """
        Cleans a single newsletter:
        1. Strips HTML tags (keeps text from <p> and <div>)
        2. Preserves links
        3. Truncates to token limit
        """
        try:
            body = newsletter.get('body', '')
            
            # Parse HTML
            soup = BeautifulSoup(body, 'html.parser')
            
            # Extract text and links
            clean_text, links = self._extract_text_and_links(soup)
            
            # Truncate to token limit
            clean_text = self._truncate_text(clean_text)
            
            # Add to newsletter
            newsletter['clean_body'] = clean_text
            newsletter['links'] = links
            
            logger.debug(
                f"Cleaned newsletter: {newsletter['subject'][:50]}... "
                f"({len(clean_text)} chars)"
            )
            
            return newsletter
        
        except Exception as e:
            logger.error(f"Error cleaning newsletter: {str(e)}")
            newsletter['clean_body'] = ""
            newsletter['links'] = []
            return newsletter
    
    def _extract_text_and_links(self, soup):
        """Extracts text from paragraphs/divs and collects links."""
        text_parts = []
        links = []
        
        # Remove script and style tags
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Extract text from paragraphs and divs
        for tag in soup.find_all(['p', 'div', 'li', 'td', 'h1', 'h2', 'h3']):
            text = tag.get_text(strip=True)
            if text:
                text_parts.append(text)
        
        # Extract links
        for link in soup.find_all('a', href=True):
            url = link['href']
            link_text = link.get_text(strip=True)
            
            # Filter out tracking pixels and very short links
            if url.startswith('http') and len(link_text) > 0:
                links.append({
                    'text': link_text,
                    'url': url
                })
        
        clean_text = '\n\n'.join(text_parts)
        return clean_text, links
    
    def _truncate_text(self, text):
        """
        Truncates text based on token approximation.
        Uses 4 characters ≈ 1 token rule.
        """
        approx_tokens = len(text) / 4
        
        if approx_tokens > self.max_tokens:
            # Truncate to approximately max_tokens
            max_chars = self.max_tokens * 4
            text = text[:max_chars]
            text = text.rsplit('\n\n', 1)[0]  # Cut at paragraph boundary
            text += "\n\n[TRUNCATED - Content was too long]"
        
        return text
