import json
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from models import Sermon, SermonSeries

# Create blueprint
sermon_bp = Blueprint('sermon', __name__)


@sermon_bp.route('/')
def index():
    """Sermon builder module home page"""
    return render_template('sermon/index.html')


@sermon_bp.route('/build', methods=['GET', 'POST'])
@login_required
def build():
    """Build a new sermon"""
    if request.method == 'POST':
        title = request.form.get('title')
        scripture_passage = request.form.get('scripture_passage')
        theme = request.form.get('theme')
        content = request.form.get('content')
        outline = request.form.get('outline')  # This could be JSON
        illustrations = request.form.get('illustrations')  # This could be JSON
        
        # Simple validation
        if not title or not scripture_passage:
            flash('Title and Scripture Passage are required.', 'danger')
            return redirect(url_for('sermon.build'))
        
        # Create new sermon
        new_sermon = Sermon(
            title=title,
            scripture_passage=scripture_passage,
            theme=theme,
            content=content,
            outline=outline,
            illustrations=illustrations,
            user_id=current_user.id
        )
        
        try:
            db.session.add(new_sermon)
            db.session.commit()
            flash('Sermon created successfully!', 'success')
            return redirect(url_for('sermon.view_sermon', id=new_sermon.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sermon: {str(e)}', 'danger')
            return redirect(url_for('sermon.build'))
    
    return render_template('sermon/build.html')


@sermon_bp.route('/my_sermons')
@login_required
def my_sermons():
    """View all sermons created by the current user"""
    sermons = Sermon.query.filter_by(user_id=current_user.id).order_by(Sermon.created_at.desc()).all()
    return render_template('sermon/my_sermons.html', sermons=sermons)


@sermon_bp.route('/sermon/<int:id>')
@login_required
def view_sermon(id):
    """View a specific sermon"""
    sermon = Sermon.query.get_or_404(id)
    
    # Check if the user is the owner of the sermon
    if sermon.user_id != current_user.id:
        flash('You do not have permission to view this sermon.', 'danger')
        return redirect(url_for('sermon.my_sermons'))
    
    # Parse JSON fields if needed
    try:
        outline = json.loads(sermon.outline) if sermon.outline else []
    except:
        outline = []
    
    try:
        illustrations = json.loads(sermon.illustrations) if sermon.illustrations else []
    except:
        illustrations = []
    
    return render_template(
        'sermon/view_sermon.html',
        sermon=sermon,
        outline=outline,
        illustrations=illustrations
    )


@sermon_bp.route('/sermon/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sermon(id):
    """Edit an existing sermon"""
    sermon = Sermon.query.get_or_404(id)
    
    # Check if the user is the owner of the sermon
    if sermon.user_id != current_user.id:
        flash('You do not have permission to edit this sermon.', 'danger')
        return redirect(url_for('sermon.my_sermons'))
    
    if request.method == 'POST':
        sermon.title = request.form.get('title')
        sermon.scripture_passage = request.form.get('scripture_passage')
        sermon.theme = request.form.get('theme')
        sermon.content = request.form.get('content')
        sermon.outline = request.form.get('outline')
        sermon.illustrations = request.form.get('illustrations')
        
        try:
            db.session.commit()
            flash('Sermon updated successfully!', 'success')
            return redirect(url_for('sermon.view_sermon', id=sermon.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating sermon: {str(e)}', 'danger')
    
    # Parse JSON fields for editing
    try:
        outline = json.loads(sermon.outline) if sermon.outline else []
    except:
        outline = []
    
    try:
        illustrations = json.loads(sermon.illustrations) if sermon.illustrations else []
    except:
        illustrations = []
    
    return render_template(
        'sermon/edit_sermon.html',
        sermon=sermon,
        outline=outline,
        illustrations=illustrations
    )


@sermon_bp.route('/sermon/<int:id>/delete', methods=['POST'])
@login_required
def delete_sermon(id):
    """Delete a sermon"""
    sermon = Sermon.query.get_or_404(id)
    
    # Check if the user is the owner of the sermon
    if sermon.user_id != current_user.id:
        flash('You do not have permission to delete this sermon.', 'danger')
        return redirect(url_for('sermon.my_sermons'))
    
    try:
        db.session.delete(sermon)
        db.session.commit()
        flash('Sermon deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sermon: {str(e)}', 'danger')
    
    return redirect(url_for('sermon.my_sermons'))


@sermon_bp.route('/api/generate_outline', methods=['POST'])
@login_required
def generate_outline():
    """API endpoint to generate a sermon outline"""
    data = request.get_json()
    scripture = data.get('scripture')
    theme = data.get('theme')
    
    if not scripture:
        return jsonify({'success': False, 'message': 'Scripture passage is required'})
    
    # In a real application, this would call an AI model or service
    # For now, we'll return a sample outline
    sample_outline = [
        {
            'title': 'Introduction',
            'points': ['Context of scripture', 'Relevance today', 'Main themes']
        },
        {
            'title': 'Main Point 1',
            'points': ['Explanation', 'Scripture reference', 'Application']
        },
        {
            'title': 'Main Point 2',
            'points': ['Explanation', 'Scripture reference', 'Application']
        },
        {
            'title': 'Main Point 3',
            'points': ['Explanation', 'Scripture reference', 'Application']
        },
        {
            'title': 'Conclusion',
            'points': ['Summary', 'Call to action', 'Final thought']
        }
    ]
    
    return jsonify({
        'success': True,
        'outline': sample_outline
    })


@sermon_bp.route('/api/suggest_illustrations', methods=['POST'])
@login_required
def suggest_illustrations():
    """API endpoint to suggest sermon illustrations"""
    data = request.get_json()
    theme = data.get('theme')
    
    if not theme:
        return jsonify({'success': False, 'message': 'Theme is required'})
    
    # In a real application, this would call an AI model or service
    # For now, we'll return sample illustrations
    sample_illustrations = [
        {
            'title': 'Personal Story',
            'description': 'Share a personal experience related to the theme'
        },
        {
            'title': 'Historical Example',
            'description': 'Reference a historical event that illustrates the theme'
        },
        {
            'title': 'Modern Analogy',
            'description': 'Use a modern situation or technology as an analogy'
        }
    ]
    
    return jsonify({
        'success': True,
        'illustrations': sample_illustrations
    })


# Sermon Series Planning Routes
@sermon_bp.route('/series')
@login_required
def series_list():
    """View all sermon series created by the current user"""
    series = SermonSeries.query.filter_by(user_id=current_user.id).order_by(SermonSeries.created_at.desc()).all()
    return render_template('sermon/series_list.html', series_list=series)


@sermon_bp.route('/series/new', methods=['GET', 'POST'])
@login_required
def new_series():
    """Create a new sermon series"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        theme = request.form.get('theme')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Simple validation
        if not title:
            flash('Title is required for a sermon series.', 'danger')
            return redirect(url_for('sermon.new_series'))
        
        # Create new sermon series
        new_series = SermonSeries(
            title=title,
            description=description,
            theme=theme,
            user_id=current_user.id
        )
        
        # Parse dates if provided
        if start_date:
            try:
                new_series.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid start date format. Please use YYYY-MM-DD.', 'warning')
        
        if end_date:
            try:
                new_series.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid end date format. Please use YYYY-MM-DD.', 'warning')
        
        try:
            db.session.add(new_series)
            db.session.commit()
            flash('Sermon series created successfully!', 'success')
            return redirect(url_for('sermon.view_series', id=new_series.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sermon series: {str(e)}', 'danger')
            return redirect(url_for('sermon.new_series'))
    
    return render_template('sermon/new_series.html')


@sermon_bp.route('/series/<int:id>')
@login_required
def view_series(id):
    """View a specific sermon series"""
    series = SermonSeries.query.get_or_404(id)
    
    # Check if the user is the owner of the series
    if series.user_id != current_user.id:
        flash('You do not have permission to view this sermon series.', 'danger')
        return redirect(url_for('sermon.series_list'))
    
    # Get all sermons in this series
    sermons = Sermon.query.filter_by(series_id=series.id).order_by(Sermon.series_position).all()
    
    return render_template('sermon/view_series.html', series=series, sermons=sermons)


@sermon_bp.route('/series/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_series(id):
    """Edit an existing sermon series"""
    series = SermonSeries.query.get_or_404(id)
    
    # Check if the user is the owner of the series
    if series.user_id != current_user.id:
        flash('You do not have permission to edit this sermon series.', 'danger')
        return redirect(url_for('sermon.series_list'))
    
    if request.method == 'POST':
        series.title = request.form.get('title')
        series.description = request.form.get('description')
        series.theme = request.form.get('theme')
        
        # Parse dates if provided
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if start_date:
            try:
                series.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid start date format. Please use YYYY-MM-DD.', 'warning')
        else:
            series.start_date = None
        
        if end_date:
            try:
                series.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid end date format. Please use YYYY-MM-DD.', 'warning')
        else:
            series.end_date = None
        
        try:
            db.session.commit()
            flash('Sermon series updated successfully!', 'success')
            return redirect(url_for('sermon.view_series', id=series.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating sermon series: {str(e)}', 'danger')
    
    return render_template('sermon/edit_series.html', series=series)


@sermon_bp.route('/series/<int:id>/delete', methods=['POST'])
@login_required
def delete_series(id):
    """Delete a sermon series"""
    series = SermonSeries.query.get_or_404(id)
    
    # Check if the user is the owner of the series
    if series.user_id != current_user.id:
        flash('You do not have permission to delete this sermon series.', 'danger')
        return redirect(url_for('sermon.series_list'))
    
    try:
        # First handle the sermons in this series (either delete or unlink)
        sermons = Sermon.query.filter_by(series_id=series.id).all()
        for sermon in sermons:
            sermon.series_id = None
            sermon.series_position = None
        
        db.session.delete(series)
        db.session.commit()
        flash('Sermon series deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sermon series: {str(e)}', 'danger')
    
    return redirect(url_for('sermon.series_list'))


@sermon_bp.route('/sermon/add_to_series/<int:sermon_id>', methods=['POST'])
@login_required
def add_sermon_to_series(sermon_id):
    """Add a sermon to a series"""
    sermon = Sermon.query.get_or_404(sermon_id)
    
    # Check if the user is the owner of the sermon
    if sermon.user_id != current_user.id:
        flash('You do not have permission to modify this sermon.', 'danger')
        return redirect(url_for('sermon.my_sermons'))
    
    series_id = request.form.get('series_id')
    position = request.form.get('position')
    
    if not series_id:
        flash('You must select a sermon series.', 'warning')
        return redirect(url_for('sermon.view_sermon', id=sermon_id))
    
    # Verify the series exists and belongs to the user
    series = SermonSeries.query.get(series_id)
    if not series or series.user_id != current_user.id:
        flash('Invalid sermon series selected.', 'danger')
        return redirect(url_for('sermon.view_sermon', id=sermon_id))
    
    try:
        sermon.series_id = series_id
        
        # Set position if provided
        if position and position.isdigit():
            sermon.series_position = int(position)
        
        # Set sermon date from series start date if possible
        if series.start_date and not sermon.sermon_date:
            sermon.sermon_date = series.start_date
        
        db.session.commit()
        flash(f'Sermon added to series "{series.title}" successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding sermon to series: {str(e)}', 'danger')
    
    return redirect(url_for('sermon.view_sermon', id=sermon_id))
