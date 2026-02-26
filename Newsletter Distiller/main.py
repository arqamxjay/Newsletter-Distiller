#!/usr/bin/env python3
"""
Newsletter Distiller - Main Entry Point
Orchestrates the five-phase pipeline: Fetch → Clean → Summarize → Compile → Send
"""

import logging
from datetime import datetime
from dotenv import load_dotenv

from phases.phase1_access import GmailAccessLayer
from phases.phase2_cleaning import CleaningEngine
from phases.phase3_intelligence import IntelligenceLayer
from phases.phase4_delivery import DeliverySystem
from phases.phase5_scheduling import SchedulingManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def run_newsletter_distiller():
    """
    Executes the complete Newsletter Distiller pipeline.
    """
    try:
        logger.info("=" * 60)
        logger.info("Starting Newsletter Distiller Pipeline")
        logger.info("=" * 60)
        
        # Phase 1: Access Layer - Fetch unread newsletters
        logger.info("\n[PHASE 1] Fetching newsletters from Gmail...")
        access_layer = GmailAccessLayer()
        newsletters = access_layer.fetch_newsletters()
        logger.info(f"Retrieved {len(newsletters)} newsletters")
        
        if not newsletters:
            logger.info("No newsletters to process. Exiting.")
            return
        
        # Phase 2: Cleaning Engine - Sanitize HTML
        logger.info("\n[PHASE 2] Cleaning newsletter content...")
        cleaning_engine = CleaningEngine()
        cleaned_newsletters = cleaning_engine.clean_all(newsletters)
        logger.info(f"Cleaned {len(cleaned_newsletters)} newsletters")
        
        # Phase 3: Intelligence Layer - Summarize with AI
        logger.info("\n[PHASE 3] Generating AI summaries...")
        intelligence_layer = IntelligenceLayer()
        summarized_newsletters = intelligence_layer.summarize_all(cleaned_newsletters)
        logger.info(f"Summarized {len(summarized_newsletters)} newsletters")
        
        # Phase 4: Delivery System - Compile and send digest
        logger.info("\n[PHASE 4] Compiling and sending digest...")
        delivery_system = DeliverySystem()
        digest_html = delivery_system.compile_digest(summarized_newsletters)
        delivery_system.send_digest(digest_html)
        logger.info("Digest sent successfully")
        
        # Mark newsletters as processed
        logger.info("\n[CLEANUP] Marking newsletters as processed...")
        access_layer.mark_as_processed(newsletters)
        logger.info("Cleanup complete")
        
        logger.info("\n" + "=" * 60)
        logger.info("Newsletter Distiller Pipeline Completed Successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run_newsletter_distiller()
