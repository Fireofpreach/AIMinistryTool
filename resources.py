from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from models import Resource
from modules.integrations import import_external_resources

# Create blueprint
resources_bp = Blueprint('resources', __name__)


@resources_bp.route('/')
def index():
    """Resource library module home page"""
    return render_template('resources/index.html')


@resources_bp.route('/library')
def library():
    """View the resource library"""
    # Get optional filter parameters
    resource_type = request.args.get('type')
    topic = request.args.get('topic')
    search = request.args.get('search')
    
    # Start with all resources
    query = Resource.query
    
    # Apply filters if provided
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    
    if topic:
        query = query.filter_by(topic=topic)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Resource.title.ilike(search_term)) |
            (Resource.author.ilike(search_term)) |
            (Resource.description.ilike(search_term)) |
            (Resource.tags.ilike(search_term))
        )
    
    # Get the resources
    resources = query.order_by(Resource.title).all()
    
    # Get distinct resource types and topics for filters
    resource_types = db.session.query(Resource.resource_type).distinct().all()
    resource_types = [r[0] for r in resource_types if r[0]]
    
    topics = db.session.query(Resource.topic).distinct().all()
    topics = [t[0] for t in topics if t[0]]
    
    return render_template(
        'resources/library.html',
        resources=resources,
        resource_types=resource_types,
        topics=topics,
        current_type=resource_type,
        current_topic=topic,
        search_term=search
    )


@resources_bp.route('/resource/<int:id>')
def view_resource(id):
    """View a specific resource"""
    resource = Resource.query.get_or_404(id)
    
    # Parse tags if they're stored as comma-separated values
    tags = resource.tags.split(',') if resource.tags else []
    
    return render_template(
        'resources/view_resource.html',
        resource=resource,
        tags=tags
    )


@resources_bp.route('/resource/new', methods=['GET', 'POST'])
@login_required
def new_resource():
    """Add a new resource to the library"""
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        resource_type = request.form.get('resource_type')
        topic = request.form.get('topic')
        description = request.form.get('description')
        content = request.form.get('content')
        url = request.form.get('url')
        tags = request.form.get('tags')
        
        # Simple validation
        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('resources.new_resource'))
        
        # Create new resource
        new_resource = Resource(
            title=title,
            author=author,
            resource_type=resource_type,
            topic=topic,
            description=description,
            content=content,
            url=url,
            tags=tags
        )
        
        try:
            db.session.add(new_resource)
            db.session.commit()
            flash('Resource added successfully!', 'success')
            return redirect(url_for('resources.view_resource', id=new_resource.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding resource: {str(e)}', 'danger')
            return redirect(url_for('resources.new_resource'))
    
    # Common resource types and topics
    resource_types = ['Book', 'Article', 'Video', 'Sermon', 'Course', 'Website', 'Podcast', 'Study Guide']
    topics = [
        'Biblical Studies', 'Theology', 'Church History', 'Apologetics', 
        'Pastoral Ministry', 'Christian Living', 'Evangelism', 'Discipleship',
        'Marriage and Family', 'Leadership', 'Ethics', 'Missions'
    ]
    
    return render_template(
        'resources/new_resource.html',
        resource_types=resource_types,
        topics=topics
    )


@resources_bp.route('/resource/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resource(id):
    """Edit an existing resource"""
    resource = Resource.query.get_or_404(id)
    
    if request.method == 'POST':
        resource.title = request.form.get('title')
        resource.author = request.form.get('author')
        resource.resource_type = request.form.get('resource_type')
        resource.topic = request.form.get('topic')
        resource.description = request.form.get('description')
        resource.content = request.form.get('content')
        resource.url = request.form.get('url')
        resource.tags = request.form.get('tags')
        
        try:
            db.session.commit()
            flash('Resource updated successfully!', 'success')
            return redirect(url_for('resources.view_resource', id=resource.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating resource: {str(e)}', 'danger')
    
    # Common resource types and topics
    resource_types = ['Book', 'Article', 'Video', 'Sermon', 'Course', 'Website', 'Podcast', 'Study Guide']
    topics = [
        'Biblical Studies', 'Theology', 'Church History', 'Apologetics', 
        'Pastoral Ministry', 'Christian Living', 'Evangelism', 'Discipleship',
        'Marriage and Family', 'Leadership', 'Ethics', 'Missions'
    ]
    
    return render_template(
        'resources/edit_resource.html',
        resource=resource,
        resource_types=resource_types,
        topics=topics
    )


@resources_bp.route('/resource/<int:id>/delete', methods=['POST'])
@login_required
def delete_resource(id):
    """Delete a resource"""
    resource = Resource.query.get_or_404(id)
    
    try:
        db.session.delete(resource)
        db.session.commit()
        flash('Resource deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting resource: {str(e)}', 'danger')
    
    return redirect(url_for('resources.library'))


@resources_bp.route('/api/search', methods=['GET'])
def search_resources():
    """API endpoint to search resources"""
    search_term = request.args.get('q', '')
    
    if not search_term:
        return jsonify({'success': False, 'message': 'Search term is required'})
    
    # Search resources
    search_pattern = f"%{search_term}%"
    resources = Resource.query.filter(
        (Resource.title.ilike(search_pattern)) |
        (Resource.author.ilike(search_pattern)) |
        (Resource.description.ilike(search_pattern)) |
        (Resource.tags.ilike(search_pattern))
    ).limit(10).all()
    
    # Format results
    results = []
    for resource in resources:
        results.append({
            'id': resource.id,
            'title': resource.title,
            'author': resource.author,
            'resource_type': resource.resource_type,
            'topic': resource.topic,
            'url': url_for('resources.view_resource', id=resource.id)
        })
    
    return jsonify({
        'success': True,
        'results': results
    })


@resources_bp.route('/api/recommend', methods=['GET'])
def recommend_resources():
    """API endpoint to recommend resources based on topic"""
    topic = request.args.get('topic', '')
    
    if not topic:
        return jsonify({'success': False, 'message': 'Topic is required'})
    
    # Find resources on the topic
    resources = Resource.query.filter_by(topic=topic).limit(5).all()
    
    # Format results
    results = []
    for resource in resources:
        results.append({
            'id': resource.id,
            'title': resource.title,
            'author': resource.author,
            'resource_type': resource.resource_type,
            'url': url_for('resources.view_resource', id=resource.id)
        })
    
    return jsonify({
        'success': True,
        'results': results
    })


@resources_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_resources():
    """Import resources from external sources like e-Sword and Logos"""
    
    if request.method == 'POST':
        source = request.form.get('source', 'all')
        resource_type = request.form.get('resource_type', None)
        topic = request.form.get('topic', None)
        
        success, message = import_external_resources(source, resource_type, topic)
        
        if success:
            flash('Resources imported successfully!', 'success')
        else:
            flash(f'Error importing resources: {message}', 'danger')
        
        return redirect(url_for('resources.library'))
    
    # Common resource types and topics for the form
    resource_types = ['Book', 'Article', 'Commentary', 'Dictionary', 'Study Bible', 'Magazine']
    topics = [
        'Biblical Studies', 'Theology', 'Eschatology', 'Church History', 'Apologetics', 
        'Pastoral Ministry', 'Christian Living', 'Biblical Languages', 'Amillennialism'
    ]
    
    return render_template(
        'resources/import.html',
        resource_types=resource_types,
        topics=topics
    )
