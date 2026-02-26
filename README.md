# Newsletter Distiller 📨

An AI-powered web application that transforms cluttered newsletters into clean, actionable daily digests. Streamline your inbox and stay informed effortlessly.

**Website:** http://localhost:8888

## Overview

Multi-user web application that automates the entire newsletter processing pipeline:

## Features

✨ **Clean, Modern UI** - Responsive design with intuitive navigation
🔐 **Secure OAuth** - Safe Gmail integration with automatic token refresh
📊 **Dashboard** - Track processed newsletters and viewing statistics
⚙️ **Customizable** - Configure label, summary style, and sending preferences
🔄 **Multi-User Ready** - Each user has isolated Gmail tokens and settings
🎯 **Smart Labeling** - Automatic newsletter filtering by Gmail labels

## Screenshots

### Login Page
Beautiful, clean authentication interface with feature highlights
![Login](screenshots/login.png)

### Dashboard
Real-time stats and newsletter processing overview
![Dashboard](screenshots/dashboard.png)

### Settings
Customize Gmail connection and processing preferences
![Settings](screenshots/settings.png)

## Quick Start

### 1. Prerequisites

- Python 3.9+
- Gmail account with OAuth credentials
- (Optional) OpenAI API key for advanced summarization

### 2. Install & Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_web.txt

# Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
```

### 3. Run Locally

```bash
python -c "from app import create_app; app = create_app(); app.run(debug=True, port=8888)"
```

Visit **http://127.0.0.1:8888**

### 4. First Steps

1. **Sign up** with your email
2. **Connect Gmail** via OAuth (Settings page)
3. **Configure** label and summary style
4. **Process newsletters** - click the button or set up scheduled jobs

## Architecture

### Database Models

- **User** - Account info with relationship to tokens/preferences
- **GmailToken** - Secure OAuth token storage per user
- **UserPreferences** - Newsletter label, summary style, email settings  
- **Newsletter** - Processing history with status tracking

### Tech Stack
Place your `credentials.json` file in the project root directory.

## Running the Distiller

### Manual Run
```bash
python main.py
```

### First Run
On the first run, you'll be prompted to authorize Gmail API access in your browser.

## Scheduling

### Option 1: Cron Job (macOS/Linux)
```bash
# Add daily 8 AM run
(crontab -l 2>/dev/null; echo "0 8 * * * cd /path/to/Newsletter\ Distiller && python main.py") | crontab -

# View cron jobs
crontab -l

# Remove cron job
crontab -e  # Then delete the line
```

### Option 2: GitHub Actions (Recommended)
1. Push your code to GitHub
2. Go to repository settings → Secrets
3. Add the following secrets:
   - `GMAIL_CREDENTIALS_FILE` (base64 encoded credentials.json)
   - `SENDER_EMAIL`
   - `RECIPIENT_EMAIL`
   - `AI_PROVIDER`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
   - `NEWSLETTER_LABEL`
   - `GMAIL_APP_PASSWORD`

The workflow will run automatically at 8:00 AM UTC daily.

### Option 3: macOS Launchd
Create `~/Library/LaunchAgents/com.newsletter.distiller.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.newsletter.distiller</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Then run:
```bash
launchctl load ~/Library/LaunchAgents/com.newsletter.distiller.plist
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `GMAIL_CREDENTIALS_FILE` | credentials.json | Path to OAuth credentials |
| `NEWSLETTER_LABEL` | To-Summarize | Gmail label for newsletters |
| `AI_PROVIDER` | openai | AI backend: `openai` or `ollama` |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model to use |
| `OPENAI_API_KEY` | - | Your OpenAI API key |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server address |
| `OLLAMA_MODEL` | llama3 | Ollama model to use |
| `MAX_TOKENS` | 2000 | Max tokens per newsletter |
| `DIGEST_SUBJECT` | Your Daily Newsletter Digest | Email subject line |
| `SMTP_SERVER` | smtp.gmail.com | SMTP server for sending |
| `SMTP_PORT` | 587 | SMTP port |

## Troubleshooting

### Gmail Authentication Fails
- Delete `token.pickle` and run `python main.py` again
- Ensure `credentials.json` is in the project root
- Check that Gmail API is enabled in Google Cloud Console

### No Newsletters Found
- Create the label "To-Summarize" in Gmail
- Set up a Gmail filter to apply this label to newsletters
- Mark some emails as unread with the label

### OpenAI API Errors
- Verify your `OPENAI_API_KEY` is correct
- Check your OpenAI account has credits available
- Ensure the model name matches your account's access level

### Ollama Connection Fails
- Ensure Ollama is running: `ollama serve`
- Check that the model is installed: `ollama list`
- Verify `OLLAMA_BASE_URL` is correct

### Email Sending Fails
- Use an app-specific password, not your main Gmail password
- Enable "Less secure app access" if not using 2FA
- Check `SENDER_EMAIL` and `RECIPIENT_EMAIL` are correct

## Development

### Project Structure
```
Newsletter Distiller/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── phases/
    ├── phase1_access.py      # Gmail API access
    ├── phase2_cleaning.py    # HTML sanitization
    ├── phase3_intelligence.py # AI summarization
    ├── phase4_delivery.py    # Digest compilation & sending
    └── phase5_scheduling.py  # Scheduling utilities
```

### Adding New Features

1. **Custom Summarization Prompt**: Edit `_create_prompt()` in `phase3_intelligence.py`
2. **Custom Email Template**: Edit `_create_html_template()` in `phase4_delivery.py`
3. **New AI Provider**: Create a new method in `IntelligenceLayer`
4. **Slack Notifications**: Add a method to `DeliverySystem` for Slack integration

## Performance Tips

- **Limit newsletters fetched**: Adjust `maxResults` in `phase1_access.py`
- **Use GPT-3.5 instead of GPT-4**: Saves 70% on API costs
- **Batch processing**: Process multiple newsletters in parallel (future enhancement)
- **Cache summaries**: Store previously summarized newsletters to avoid re-processing

## Security Notes

- **Never commit** `.env` or `credentials.json` to GitHub
- **Use app-specific passwords** for Gmail, not your main password
- **Store secrets** in environment variables or GitHub Secrets, not in code
- **Rotate API keys** periodically
- **Set read-only scopes** if possible (current Gmail scope allows modifications)

## Future Enhancements

- [ ] Slack/Discord digest delivery
- [ ] Web dashboard for digest management
- [ ] Custom summarization templates per sender
- [ ] Sentiment analysis and categorization
- [ ] Search and archive older digests
- [ ] Multi-language support
- [ ] Database storage for digests
- [ ] A/B testing different summarization models

## License

MIT License - Feel free to modify and distribute

## Support

For issues, questions, or feature requests, please open an issue or contact the maintainer.

---

**Happy digesting! 🚀**
