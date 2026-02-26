"""
Phase 5: The Scheduling & Deployment
Cron job setup and automation configuration
"""

import os
import logging
import subprocess
import platform

logger = logging.getLogger(__name__)


class SchedulingManager:
    """Manages scheduling and deployment options."""
    
    @staticmethod
    def setup_cron_job(hour=8, minute=0):
        """
        Sets up a daily cron job to run the Newsletter Distiller.
        
        Args:
            hour: Hour to run (0-23, default 8 for 8 AM)
            minute: Minute to run (0-59, default 0)
        """
        if platform.system() == "Windows":
            logger.error("Cron jobs are not available on Windows. Use Task Scheduler instead.")
            return False
        
        try:
            script_path = os.path.abspath("main.py")
            python_path = os.path.abspath(os.path.dirname(__file__))
            
            # Cron job format: minute hour * * * command
            cron_command = f"{minute} {hour} * * * cd {python_path} && python {script_path}"
            
            # Install cron job
            subprocess.run(
                f'(crontab -l 2>/dev/null; echo "{cron_command}") | crontab -',
                shell=True,
                check=True
            )
            
            logger.info(f"Cron job installed to run at {hour:02d}:{minute:02d} daily")
            return True
        
        except Exception as e:
            logger.error(f"Error setting up cron job: {str(e)}")
            return False
    
    @staticmethod
    def setup_github_actions():
        """
        Creates a GitHub Actions workflow file for automated daily runs.
        Requires repository to be on GitHub with Actions enabled.
        """
        workflow_content = """name: Newsletter Distiller Daily Run

on:
  schedule:
    # Runs at 8:00 AM UTC every day
    - cron: '0 8 * * *'
  workflow_dispatch:

jobs:
  distill-newsletters:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Create .env file
        run: |
          cat > .env << EOF
          GMAIL_CREDENTIALS_FILE=${{ secrets.GMAIL_CREDENTIALS_FILE }}
          SENDER_EMAIL=${{ secrets.SENDER_EMAIL }}
          RECIPIENT_EMAIL=${{ secrets.RECIPIENT_EMAIL }}
          AI_PROVIDER=${{ secrets.AI_PROVIDER }}
          OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
          OPENAI_MODEL=${{ secrets.OPENAI_MODEL }}
          NEWSLETTER_LABEL=${{ secrets.NEWSLETTER_LABEL }}
          GMAIL_APP_PASSWORD=${{ secrets.GMAIL_APP_PASSWORD }}
          EOF
      
      - name: Run Newsletter Distiller
        run: python main.py

"""
        
        # Create workflows directory
        workflows_dir = '.github/workflows'
        os.makedirs(workflows_dir, exist_ok=True)
        
        workflow_file = os.path.join(workflows_dir, 'newsletter_distiller.yml')
        
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        logger.info(f"GitHub Actions workflow created at {workflow_file}")
        logger.info("Add your secrets to GitHub repository settings:")
        logger.info("  - GMAIL_CREDENTIALS_FILE")
        logger.info("  - SENDER_EMAIL")
        logger.info("  - RECIPIENT_EMAIL")
        logger.info("  - AI_PROVIDER")
        logger.info("  - OPENAI_API_KEY")
        logger.info("  - OPENAI_MODEL")
        logger.info("  - NEWSLETTER_LABEL")
        logger.info("  - GMAIL_APP_PASSWORD")
        
        return True
    
    @staticmethod
    def get_setup_instructions():
        """Returns setup instructions for different platforms."""
        return """
=== Newsletter Distiller Scheduling Setup ===

Option 1: Local Cron Job (macOS/Linux)
--------------------------------------
1. Run: python -c "from phases.phase5_scheduling import SchedulingManager; SchedulingManager.setup_cron_job(8, 0)"
2. Verify: crontab -l

Option 2: GitHub Actions (Recommended)
--------------------------------------
1. Push your code to GitHub
2. Run: python -c "from phases.phase5_scheduling import SchedulingManager; SchedulingManager.setup_github_actions()"
3. Add secrets in GitHub repository settings
4. Workflow will run automatically at 8:00 AM UTC daily

Option 3: Manual Run
-------------------
Just run: python main.py

Option 4: Docker
---------------
TODO: Implement Docker support

=== Important Notes ===
- Ensure .env file is properly configured
- For Gmail API: Use app-specific passwords (not your main password)
- Store sensitive credentials in environment variables or GitHub secrets
- Test the script manually before scheduling
"""
