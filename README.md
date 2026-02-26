# Newsletter Distiller 📨

An intelligent automation system that transforms your cluttered newsletter inbox into a high-value "intelligence report" using AI.

## Overview

The Newsletter Distiller automates the entire newsletter processing pipeline:

1. **Fetch** - Pulls unread newsletters from Gmail using OAuth 2.0
2. **Clean** - Sanitizes HTML and extracts clean text and links
3. **Summarize** - Uses AI (OpenAI or Ollama) to generate 3-bullet summaries
4. **Compile** - Merges all summaries into an elegant daily digest
5. **Send** - Delivers the digest via email and marks originals as read

## Architecture

```
[Gmail API] → [Phase 1: Access] → [Phase 2: Cleaning] → [Phase 3: Intelligence]
                                                              ↓
                                                    [Phase 4: Delivery]
                                                              ↓
                                                    [Phase 5: Scheduling]
```

## Prerequisites

### Gmail Setup
1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the **Gmail API**
   - Create an OAuth 2.0 credential (Desktop application)
   - Download the credentials file as `credentials.json`

2. **Create Gmail Filter**
   - In Gmail, create a filter for newsletters
   - Apply a label (e.g., "To-Summarize")
   - This prevents the bot from processing personal emails

3. **Generate App-Specific Password**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already done
   - Create an app-specific password for "Mail" on "macOS"
   - Save this password for later

### AI Provider Setup

**Option A: OpenAI (Recommended for speed & quality)**
- Sign up at [OpenAI](https://platform.openai.com/)
- Create an API key
- Set `AI_PROVIDER=openai` in `.env`

**Option B: Ollama (Free & Private)**
- Install [Ollama](https://ollama.ai/)
- Pull a model: `ollama pull llama3`
- Run: `ollama serve`
- Set `AI_PROVIDER=ollama` in `.env`

## Installation

### 1. Clone/Download the Repository
```bash
cd "Newsletter Distiller"
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
# Gmail Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.pickle
SENDER_EMAIL=your-email@gmail.com
RECIPIENT_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password

# AI Configuration
AI_PROVIDER=openai  # or ollama
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Gmail Settings
NEWSLETTER_LABEL=To-Summarize
```

### 5. Add Credentials
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
