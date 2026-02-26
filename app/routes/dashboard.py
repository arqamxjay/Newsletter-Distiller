"""
Dashboard routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import UserPreferences, Newsletter

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard"""
    newsletters = Newsletter.query.filter_by(user_id=current_user.id).order_by(
        Newsletter.created_at.desc()
    ).limit(10).all()
    
    stats = {
        'total': Newsletter.query.filter_by(user_id=current_user.id).count(),
        'completed': Newsletter.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).count(),
        'pending': Newsletter.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).count(),
    }
    
    return render_template('dashboard/index.html', newsletters=newsletters, stats=stats)


@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    prefs = current_user.preferences or UserPreferences(user_id=current_user.id)
    
    if request.method == 'POST':
        prefs.newsletter_label = request.form.get('newsletter_label', 'To-Summarize')
        prefs.summary_style = request.form.get('summary_style', 'bullet-points')
        prefs.auto_send = request.form.get('auto_send') == 'on'
        prefs.send_to_email = request.form.get('send_to_email', current_user.email)
        
        if not prefs.user_id:
            prefs.user_id = current_user.id
        
        db.session.add(prefs)
        db.session.commit()
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('dashboard.settings'))
    
    return render_template('dashboard/settings.html', prefs=prefs)


@dashboard_bp.route('/process', methods=['POST'])
@login_required
def process_newsletters():
    """Trigger newsletter processing"""
    if not current_user.gmail_token:
        flash('Please connect your Gmail account first!', 'error')
        return redirect(url_for('dashboard.settings'))
    
    try:
        # Import here to avoid circular imports
        from app.workers.tasks import process_user_newsletters
        task = process_user_newsletters.delay(current_user.id)
        flash(f'Processing started! Task ID: {task.id}', 'info')
    except Exception as e:
        flash(f'Error starting processing: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.index'))
