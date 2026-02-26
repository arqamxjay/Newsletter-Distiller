"""
Background job processor using Celery
"""

import logging
from celery import Celery
from app import create_app, db
from app.models import User, Newsletter
from app.workers.multi_user_phase1 import MultiUserGmailAccessLayer
from phases.phase2_cleaning import CleaningEngine
from phases.phase3_intelligence import IntelligenceLayer
from phases.phase4_delivery import DeliverySystem

logger = logging.getLogger(__name__)

# Create Flask app
flask_app = create_app()

# Create Celery app
celery_app = Celery(__name__)
celery_app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task
def process_user_newsletters(user_id):
    """
    Background task to process newsletters for a specific user.
    
    Args:
        user_id: ID of the user to process newsletters for
    """
    with flask_app.app_context():
        try:
            user = User.query.get(user_id)
            if not user or not user.gmail_token:
                logger.warning(f"Cannot process: User {user_id} not found or no Gmail token")
                return {'status': 'error', 'message': 'User or Gmail token not found'}
            
            logger.info(f"Starting newsletter processing for {user.email}")
            
            # Phase 1: Fetch newsletters
            access_layer = MultiUserGmailAccessLayer(user)
            newsletters = access_layer.fetch_newsletters()
            
            if not newsletters:
                logger.info(f"No newsletters found for {user.email}")
                return {'status': 'success', 'processed': 0, 'message': 'No newsletters to process'}
            
            logger.info(f"Found {len(newsletters)} newsletters for {user.email}")
            
            # Phase 2-4: Process each newsletter
            cleaning_engine = CleaningEngine()
            intelligence_layer = IntelligenceLayer()
            delivery_system = DeliverySystem()
            
            processed_count = 0
            for newsletter_data in newsletters:
                try:
                    newsletter_id = newsletter_data['db_id']
                    newsletter = Newsletter.query.get(newsletter_id)
                    
                    # Phase 2: Clean
                    newsletter.status = 'processing'
                    db.session.commit()
                    
                    cleaned = cleaning_engine.clean(newsletter.original_content)
                    newsletter.cleaned_content = cleaned
                    
                    # Phase 3: Summarize
                    summary = intelligence_layer.summarize(
                        cleaned,
                        style=user.preferences.summary_style if user.preferences else 'bullet-points'
                    )
                    newsletter.summary = summary
                    
                    # Phase 4: Deliver
                    if user.preferences and user.preferences.auto_send:
                        delivery_system.send_summary(
                            to_email=user.preferences.send_to_email or user.email,
                            subject=f"Summary: {newsletter.original_subject}",
                            content=summary
                        )
                    
                    # Mark as complete
                    newsletter.status = 'completed'
                    from datetime import datetime
                    newsletter.processed_at = datetime.utcnow()
                    db.session.commit()
                    
                    # Mark as read in Gmail
                    access_layer.mark_as_read(newsletter.gmail_message_id)
                    
                    processed_count += 1
                    logger.info(f"Processed newsletter {newsletter_id} for {user.email}")
                
                except Exception as e:
                    logger.error(f"Error processing newsletter for {user.email}: {e}")
                    if newsletter:
                        newsletter.status = 'failed'
                        db.session.commit()
            
            logger.info(f"Completed processing {processed_count} newsletters for {user.email}")
            return {
                'status': 'success',
                'processed': processed_count,
                'user': user.email
            }
        
        except Exception as e:
            logger.error(f"Error in process_user_newsletters: {e}")
            return {'status': 'error', 'message': str(e)}


@celery_app.task
def process_all_users():
    """
    Background task to process newsletters for all users with Gmail tokens.
    """
    with flask_app.app_context():
        users_with_tokens = User.query.filter(
            User.gmail_token.isnot(None)
        ).all()
        
        results = []
        for user in users_with_tokens:
            result = process_user_newsletters.delay(user.id)
            results.append({
                'user_id': user.id,
                'email': user.email,
                'task_id': result.id
            })
        
        logger.info(f"Queued {len(results)} users for newsletter processing")
        return results
