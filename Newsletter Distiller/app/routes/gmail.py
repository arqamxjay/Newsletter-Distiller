"""
Gmail OAuth routes
"""

from flask import Blueprint, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from app import db
from app.models import GmailToken
import os
import pickle

gmail_bp = Blueprint('gmail', __name__, url_prefix='/gmail')


@gmail_bp.route('/authorize')
@login_required
def authorize():
    """Initiate Gmail OAuth flow"""
    flow = Flow.from_client_secrets_file(
        os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json'),
        scopes=['https://www.googleapis.com/auth/gmail.modify'],
        redirect_uri=url_for('gmail.callback', _external=True)
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['oauth_state'] = state
    session['user_id'] = current_user.id
    
    return redirect(authorization_url)


@gmail_bp.route('/callback')
def callback():
    """Gmail OAuth callback"""
    state = session.get('oauth_state')
    user_id = session.get('user_id')
    
    if not state or not user_id:
        flash('OAuth state not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    flow = Flow.from_client_secrets_file(
        os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json'),
        scopes=['https://www.googleapis.com/auth/gmail.modify'],
        state=state,
        redirect_uri=url_for('gmail.callback', _external=True)
    )
    
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Store token
        gmail_token = GmailToken.query.filter_by(user_id=user_id).first()
        if not gmail_token:
            gmail_token = GmailToken(user_id=user_id)
        
        gmail_token.access_token = credentials.token
        gmail_token.refresh_token = credentials.refresh_token
        gmail_token.token_expires_at = credentials.expiry
        
        db.session.add(gmail_token)
        db.session.commit()
        
        flash('Gmail account connected successfully!', 'success')
    except Exception as e:
        flash(f'Failed to connect Gmail: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.settings'))


@gmail_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Gmail account"""
    GmailToken.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    flash('Gmail account disconnected.', 'success')
    return redirect(url_for('dashboard.settings'))
