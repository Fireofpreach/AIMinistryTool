import json
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from models import (
    ApologeticsCategory, ApologeticsObjection, ApologeticsResponse,
    TheologicalAuthor, TheologicalWork, TheologicalQuote, Resource
)

# Create blueprint
apologetics_bp = Blueprint('apologetics', __name__)


@apologetics_bp.route('/')
def index():
    """Apologetics module home page"""
    categories = ApologeticsCategory.query.all()
    return render_template('apologetics/index.html', categories=categories)


@apologetics_bp.route('/objections')
def objections_list():
    """List all objections with their categories"""
    category_id = request.args.get('category', type=int)
    
    if category_id:
        objections = ApologeticsObjection.query.filter_by(category_id=category_id).all()
        category = ApologeticsCategory.query.get_or_404(category_id)
        return render_template('apologetics/objections.html', 
                              objections=objections, 
                              category=category,
                              all_categories=ApologeticsCategory.query.all())
    else:
        objections = ApologeticsObjection.query.all()
        return render_template('apologetics/objections.html', 
                              objections=objections,
                              all_categories=ApologeticsCategory.query.all())


@apologetics_bp.route('/objection/<int:id>')
def view_objection(id):
    """View a specific objection and its responses"""
    objection = ApologeticsObjection.query.get_or_404(id)
    responses = ApologeticsResponse.query.filter_by(objection_id=id).all()
    
    # Get related resources
    related_resources = []
    for response in responses:
        if response.additional_resources:
            try:
                resource_ids = json.loads(response.additional_resources)
                for res_id in resource_ids:
                    resource = Resource.query.get(res_id)
                    if resource and resource not in related_resources:
                        related_resources.append(resource)
            except:
                pass
    
    return render_template('apologetics/view_objection.html', 
                          objection=objection, 
                          responses=responses,
                          related_resources=related_resources)


@apologetics_bp.route('/response/new/<int:objection_id>', methods=['GET', 'POST'])
@login_required
def new_response(objection_id):
    """Create a new response to an objection"""
    objection = ApologeticsObjection.query.get_or_404(objection_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        response_text = request.form.get('response_text')
        scripture_references = request.form.get('scripture_references')
        resource_ids = request.form.getlist('resources')
        
        if not title or not response_text:
            flash('Title and response text are required', 'danger')
            return redirect(url_for('apologetics.new_response', objection_id=objection_id))
        
        # Create new response
        response = ApologeticsResponse(
            title=title,
            response_text=response_text,
            scripture_references=scripture_references,
            additional_resources=json.dumps(resource_ids) if resource_ids else None,
            objection_id=objection_id,
            user_id=current_user.id
        )
        
        try:
            db.session.add(response)
            db.session.commit()
            flash('Response added successfully!', 'success')
            return redirect(url_for('apologetics.view_objection', id=objection_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding response: {str(e)}', 'danger')
    
    # Get resources for the dropdown
    amillennial_resources = Resource.query.filter_by(is_amillennial=True).all()
    other_resources = Resource.query.filter_by(is_amillennial=False).all()
    
    return render_template('apologetics/new_response.html', 
                           objection=objection,
                           amillennial_resources=amillennial_resources,
                           other_resources=other_resources)


@apologetics_bp.route('/response/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_response(id):
    """Edit a response"""
    response = ApologeticsResponse.query.get_or_404(id)
    
    # Check if the user is the owner of the response
    if response.user_id != current_user.id:
        flash('You do not have permission to edit this response.', 'danger')
        return redirect(url_for('apologetics.view_objection', id=response.objection_id))
    
    if request.method == 'POST':
        response.title = request.form.get('title')
        response.response_text = request.form.get('response_text')
        response.scripture_references = request.form.get('scripture_references')
        
        resource_ids = request.form.getlist('resources')
        response.additional_resources = json.dumps(resource_ids) if resource_ids else None
        
        try:
            db.session.commit()
            flash('Response updated successfully!', 'success')
            return redirect(url_for('apologetics.view_objection', id=response.objection_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating response: {str(e)}', 'danger')
    
    # Get selected resources
    selected_resources = []
    if response.additional_resources:
        try:
            selected_resources = json.loads(response.additional_resources)
        except:
            selected_resources = []
    
    # Get resources for the dropdown
    amillennial_resources = Resource.query.filter_by(is_amillennial=True).all()
    other_resources = Resource.query.filter_by(is_amillennial=False).all()
    
    return render_template('apologetics/edit_response.html', 
                           response=response,
                           objection=response.objection,
                           amillennial_resources=amillennial_resources,
                           other_resources=other_resources,
                           selected_resources=selected_resources)


@apologetics_bp.route('/response/<int:id>/delete', methods=['POST'])
@login_required
def delete_response(id):
    """Delete a response"""
    response = ApologeticsResponse.query.get_or_404(id)
    
    # Check if the user is the owner of the response
    if response.user_id != current_user.id:
        flash('You do not have permission to delete this response.', 'danger')
        return redirect(url_for('apologetics.view_objection', id=response.objection_id))
    
    objection_id = response.objection_id
    
    try:
        db.session.delete(response)
        db.session.commit()
        flash('Response deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting response: {str(e)}', 'danger')
    
    return redirect(url_for('apologetics.view_objection', id=objection_id))


@apologetics_bp.route('/authors')
def theological_authors():
    """View theological authors, especially amillennial ones"""
    # Filter by amillennial if specified
    amillennial_only = request.args.get('amillennial', type=int)
    
    if amillennial_only:
        authors = TheologicalAuthor.query.filter_by(is_amillennial=True).all()
    else:
        authors = TheologicalAuthor.query.all()
    
    return render_template('apologetics/authors.html', authors=authors, amillennial_only=amillennial_only)


@apologetics_bp.route('/author/<int:id>')
def view_author(id):
    """View a specific theological author and their works"""
    author = TheologicalAuthor.query.get_or_404(id)
    works = TheologicalWork.query.filter_by(author_id=id).all()
    quotes = TheologicalQuote.query.filter_by(author_id=id).all()
    
    return render_template('apologetics/view_author.html', 
                           author=author, 
                           works=works,
                           quotes=quotes)


@apologetics_bp.route('/debate-preparation')
@login_required
def debate_preparation():
    """Prepare for theological debates with common objections and responses"""
    categories = ApologeticsCategory.query.all()
    
    # If a specific category is selected
    category_id = request.args.get('category', type=int)
    if category_id:
        selected_category = ApologeticsCategory.query.get_or_404(category_id)
        objections = ApologeticsObjection.query.filter_by(category_id=category_id).all()
    else:
        selected_category = None
        objections = []
    
    return render_template('apologetics/debate_preparation.html', 
                          categories=categories,
                          selected_category=selected_category,
                          objections=objections)


@apologetics_bp.route('/api/generate_response', methods=['POST'])
@login_required
def generate_response():
    """API endpoint to generate a response to an objection"""
    data = request.get_json()
    objection_id = data.get('objection_id')
    
    if not objection_id:
        return jsonify({'success': False, 'message': 'Objection ID is required'})
    
    objection = ApologeticsObjection.query.get(objection_id)
    if not objection:
        return jsonify({'success': False, 'message': 'Objection not found'})
    
    # In a real application, this would call an AI model or service
    # For now, we'll return a sample response based on the objection category
    
    category_name = objection.category.name.lower()
    
    sample_response = {
        'title': f'Response to: {objection.title}',
        'response_text': '',
        'scripture_references': ''
    }
    
    if 'eschatology' in category_name:
        sample_response['response_text'] = (
            "The amillennial view interprets Revelation 20:1-6 symbolically rather than literally. "
            "The 'thousand years' represents Christ's current reign in the hearts of believers and in heaven. "
            "This interpretation is consistent with the highly symbolic nature of apocalyptic literature. "
            "Consider how Jesus himself frequently used parables and figurative language to describe the Kingdom of God. "
            "The amillennial view has strong historical support, being held by Augustine, Luther, Calvin, and many church fathers."
        )
        sample_response['scripture_references'] = "John 5:28-29, 2 Peter 3:10-13, Matthew 12:28"
    
    elif 'israel' in category_name:
        sample_response['response_text'] = (
            "The amillennial view understands the church as the spiritual Israel, the fulfillment of God's promises to Abraham. "
            "This is not replacement theology but fulfillment theology. Paul explicitly states in Galatians 3:29, 'If you belong to Christ, "
            "then you are Abraham's seed, and heirs according to the promise.' The promises to ethnic Israel are ultimately fulfilled in Christ "
            "and the Church. Romans 9:6 clarifies, 'Not all who are descended from Israel are Israel.'"
        )
        sample_response['scripture_references'] = "Romans 9:6-8, Galatians 3:7-9, Galatians 3:29, Romans 2:28-29"
    
    else:
        sample_response['response_text'] = (
            "The amillennial interpretation offers a cohesive framework that harmonizes Scripture's teaching on Christ's kingdom. "
            "Rather than dividing God's redemptive plan into dispensations, amillennialism sees the unity of God's people across history. "
            "The apparent contradictions in premillennial and dispensational views are resolved when we understand apocalyptic literature "
            "in its proper context and recognize the already-not yet nature of God's kingdom."
        )
        sample_response['scripture_references'] = "Luke 17:20-21, Colossians 1:13-14, Hebrews 12:22-24"
    
    return jsonify({
        'success': True,
        'response': sample_response
    })