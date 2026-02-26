"""
Phase 3: The Intelligence Layer
AI-powered summarization using OpenAI or Ollama
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)


class IntelligenceLayer:
    """Handles AI summarization with support for OpenAI and Ollama."""
    
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        
        if self.provider == 'openai':
            self.client = self._init_openai()
        elif self.provider == 'ollama':
            self.ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")
    
    def _init_openai(self):
        """Initializes OpenAI client."""
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            return OpenAI(api_key=api_key)
        except ImportError:
            logger.error("OpenAI library not installed. Run: pip install openai")
            raise
    
    def summarize_all(self, newsletters):
        """Summarizes all newsletters."""
        summarized = []
        for newsletter in newsletters:
            summarized_newsletter = self.summarize_single(newsletter)
            summarized.append(summarized_newsletter)
        return summarized
    
    def summarize_single(self, newsletter):
        """
        Generates a 3-bullet summary for a single newsletter.
        """
        try:
            content = newsletter.get('clean_body', '')
            sender = newsletter.get('sender', 'Unknown')
            
            if not content or len(content.strip()) < 50:
                logger.warning(f"Newsletter from {sender} is too short to summarize")
                newsletter['summary'] = ["No content to summarize"]
                return newsletter
            
            # Create the summarization prompt
            prompt = self._create_prompt(content, sender)
            
            # Get summary from AI provider
            if self.provider == 'openai':
                summary = self._summarize_with_openai(prompt)
            elif self.provider == 'ollama':
                summary = self._summarize_with_ollama(prompt)
            
            # Parse bullet points
            bullets = self._parse_bullets(summary)
            
            newsletter['summary'] = bullets
            logger.info(f"Summarized newsletter from {sender}")
            
            return newsletter
        
        except Exception as e:
            logger.error(f"Error summarizing newsletter: {str(e)}")
            newsletter['summary'] = ["Error during summarization"]
            return newsletter
    
    def _create_prompt(self, content, sender):
        """Creates a structured prompt for the AI."""
        return f"""You are a professional research assistant. Below is a newsletter from {sender}.

NEWSLETTER CONTENT:
{content}

Please summarize the top 3 most important takeaways into concise bullet points (1-2 sentences each). 
Maintain a neutral, informative tone.

Provide only the bullet points, starting each with a dash (-)."""
    
    def _summarize_with_openai(self, prompt):
        """Calls OpenAI GPT model for summarization."""
        try:
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional research assistant specializing in synthesizing information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _summarize_with_ollama(self, prompt):
        """Calls local Ollama model for summarization."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.5
                },
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(
                    f"Ollama API returned {response.status_code}: {response.text}"
                )
            
            result = response.json()
            return result.get('response', '')
        
        except requests.exceptions.ConnectionError:
            logger.error(
                f"Cannot connect to Ollama at {self.ollama_url}. "
                "Ensure Ollama is running."
            )
            raise
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise
    
    def _parse_bullets(self, text):
        """Parses bullet points from AI response."""
        bullets = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove common bullet markers
            if line.startswith('- '):
                line = line[2:]
            elif line.startswith('• '):
                line = line[2:]
            elif line.startswith('* '):
                line = line[2:]
            elif line and line[0].isdigit() and '.' in line:
                # Remove numbered bullets like "1. "
                line = line.split('.', 1)[1].strip()
            
            if line:
                bullets.append(line)
        
        # Return only first 3 bullets
        return bullets[:3] if bullets else ["Unable to extract summary"]
