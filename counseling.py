import json
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from models import CounselingSession

# Create blueprint
counseling_bp = Blueprint('counseling', __name__)


@counseling_bp.route('/')
def index():
    """Counseling module home page"""
    return render_template('counseling/index.html')


@counseling_bp.route('/session', methods=['GET', 'POST'])
@login_required
def new_session():
    """Create a new counseling session"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        topic = request.form.get('topic')
        notes = request.form.get('notes')
        scripture_references = request.form.get('scripture_references')
        
        # Simple validation
        if not title or not topic:
            flash('Title and Topic are required.', 'danger')
            return redirect(url_for('counseling.new_session'))
        
        # Create new counseling session
        new_session = CounselingSession(
            title=title,
            description=description,
            topic=topic,
            notes=notes,
            scripture_references=scripture_references,
            user_id=current_user.id
        )
        
        try:
            db.session.add(new_session)
            db.session.commit()
            flash('Counseling session created successfully!', 'success')
            return redirect(url_for('counseling.view_session', id=new_session.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating counseling session: {str(e)}', 'danger')
            return redirect(url_for('counseling.new_session'))
    
    # Common counseling topics
    topics = [
        'Marriage', 'Family', 'Grief', 'Addiction', 'Anxiety', 
        'Depression', 'Faith Crisis', 'Relationships', 'Career', 
        'Financial Stewardship', 'Forgiveness', 'Guilt'
    ]
    
    return render_template('counseling/session.html', topics=topics)


@counseling_bp.route('/my_sessions')
@login_required
def my_sessions():
    """View all counseling sessions created by the current user"""
    sessions = CounselingSession.query.filter_by(user_id=current_user.id).order_by(CounselingSession.created_at.desc()).all()
    return render_template('counseling/my_sessions.html', sessions=sessions)


@counseling_bp.route('/session/<int:id>')
@login_required
def view_session(id):
    """View a specific counseling session"""
    session = CounselingSession.query.get_or_404(id)
    
    # Check if the user is the owner of the session
    if session.user_id != current_user.id:
        flash('You do not have permission to view this counseling session.', 'danger')
        return redirect(url_for('counseling.my_sessions'))
    
    # Parse scripture references if stored as JSON
    try:
        scripture_refs = json.loads(session.scripture_references) if session.scripture_references else []
    except:
        scripture_refs = session.scripture_references.split(',') if session.scripture_references else []
    
    return render_template(
        'counseling/view_session.html',
        session=session,
        scripture_refs=scripture_refs
    )


@counseling_bp.route('/session/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_session(id):
    """Edit an existing counseling session"""
    session = CounselingSession.query.get_or_404(id)
    
    # Check if the user is the owner of the session
    if session.user_id != current_user.id:
        flash('You do not have permission to edit this counseling session.', 'danger')
        return redirect(url_for('counseling.my_sessions'))
    
    if request.method == 'POST':
        session.title = request.form.get('title')
        session.description = request.form.get('description')
        session.topic = request.form.get('topic')
        session.notes = request.form.get('notes')
        session.scripture_references = request.form.get('scripture_references')
        
        try:
            db.session.commit()
            flash('Counseling session updated successfully!', 'success')
            return redirect(url_for('counseling.view_session', id=session.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating counseling session: {str(e)}', 'danger')
    
    # Common counseling topics
    topics = [
        'Marriage', 'Family', 'Grief', 'Addiction', 'Anxiety', 
        'Depression', 'Faith Crisis', 'Relationships', 'Career', 
        'Financial Stewardship', 'Forgiveness', 'Guilt'
    ]
    
    # Parse scripture references if stored as JSON
    try:
        scripture_refs = json.loads(session.scripture_references) if session.scripture_references else []
    except:
        scripture_refs = session.scripture_references.split(',') if session.scripture_references else []
    
    return render_template(
        'counseling/edit_session.html',
        session=session,
        topics=topics,
        scripture_refs=scripture_refs
    )


@counseling_bp.route('/session/<int:id>/delete', methods=['POST'])
@login_required
def delete_session(id):
    """Delete a counseling session"""
    session = CounselingSession.query.get_or_404(id)
    
    # Check if the user is the owner of the session
    if session.user_id != current_user.id:
        flash('You do not have permission to delete this counseling session.', 'danger')
        return redirect(url_for('counseling.my_sessions'))
    
    try:
        db.session.delete(session)
        db.session.commit()
        flash('Counseling session deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting counseling session: {str(e)}', 'danger')
    
    return redirect(url_for('counseling.my_sessions'))


@counseling_bp.route('/api/suggest_scriptures', methods=['POST'])
@login_required
def suggest_scriptures():
    """API endpoint to suggest scripture references for counseling topics"""
    data = request.get_json()
    topic = data.get('topic')
    
    if not topic:
        return jsonify({'success': False, 'message': 'Topic is required'})
    
    # Scripture reference suggestions for common counseling topics
    scripture_suggestions = {
        'Marriage': ['Ephesians 5:22-33', 'Genesis 2:24', '1 Corinthians 7:1-16', 'Proverbs 5:18-19'],
        'Family': ['Deuteronomy 6:6-9', 'Ephesians 6:1-4', 'Proverbs 22:6', 'Psalm 127:3-5'],
        'Grief': ['Psalm 34:18', 'Matthew 5:4', 'John 11:35', '2 Corinthians 1:3-4', 'Revelation 21:4'],
        'Addiction': ['1 Corinthians 10:13', 'James 4:7', 'Romans 6:16-18', 'Galatians 5:1'],
        'Anxiety': ['Philippians 4:6-7', 'Matthew 6:25-34', '1 Peter 5:7', 'Isaiah 41:10'],
        'Depression': ['Psalm 42:11', 'Isaiah 40:31', 'Jeremiah 29:11', 'Romans 8:38-39'],
        'Faith Crisis': ['Hebrews 11:1-6', 'Mark 9:24', '2 Corinthians 5:7', 'Romans 10:17'],
        'Relationships': ['John 13:34-35', '1 Corinthians 13:4-7', 'Romans 12:18', 'Ephesians 4:2-3'],
        'Career': ['Colossians 3:23-24', 'Proverbs 16:3', 'Jeremiah 29:11', 'Philippians 4:13'],
        'Financial Stewardship': ['Malachi 3:10', 'Proverbs 3:9-10', 'Luke 16:10-12', 'Matthew 6:24'],
        'Forgiveness': ['Matthew 6:14-15', 'Ephesians 4:31-32', 'Colossians 3:13', 'Luke 23:34'],
        'Guilt': ['Romans 8:1', 'Psalm 103:12', '1 John 1:9', 'Isaiah 43:25']
    }
    
    # Get scripture suggestions for the topic, or provide a default if not found
    suggestions = scripture_suggestions.get(topic, ['John 3:16', 'Romans 8:28', 'Philippians 4:13'])
    
    return jsonify({
        'success': True,
        'scriptures': suggestions
    })


@counseling_bp.route('/api/counseling_advice', methods=['POST'])
@login_required
def counseling_advice():
    """API endpoint to get advice for counseling situations"""
    data = request.get_json()
    topic = data.get('topic')
    situation = data.get('situation', '')
    
    if not topic:
        return jsonify({'success': False, 'message': 'Topic is required'})
    
    # In a real application, this would call an AI model or service
    # For now, we'll return generic advice based on the topic
    advice_map = {
        'Marriage': 'Focus on communication, mutual respect, and spending quality time together.',
        'Family': 'Establish clear boundaries and expectations, and prioritize regular family time.',
        'Grief': 'Acknowledge the pain, allow time for healing, and seek support from community.',
        'Addiction': 'Recognize the problem, seek professional help, and develop healthy alternatives.',
        'Anxiety': 'Practice mindfulness, focus on what can be controlled, and establish routines.',
        'Depression': 'Seek professional help, maintain social connections, and engage in physical activity.',
        'Faith Crisis': 'Ask questions openly, study scripture, and connect with mature believers.',
        'Relationships': 'Practice active listening, express needs clearly, and resolve conflicts quickly.',
        'Career': 'Align work with values, maintain work-life balance, and seek continuous growth.',
        'Financial Stewardship': 'Create a budget, avoid debt, give generously, and save consistently.',
        'Forgiveness': 'Acknowledge hurt, choose to forgive, and focus on moving forward.',
        'Guilt': 'Distinguish between conviction and condemnation, practice self-forgiveness, and make amends when possible.'
    }
    
    advice = advice_map.get(topic, 'Seek wisdom from scripture and prayer. Consider professional counseling if needed.')
    
    return jsonify({
        'success': True,
        'advice': advice
    })
