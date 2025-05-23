import json
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from models import Denomination, Belief, DoctrineComparison

# Create blueprint
doctrine_bp = Blueprint('doctrine', __name__)


@doctrine_bp.route('/')
def index():
    """Doctrine comparison module home page"""
    denominations = Denomination.query.all()
    return render_template('doctrine/index.html', denominations=denominations)


@doctrine_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():
    """Compare doctrines between denominations"""
    denominations = Denomination.query.all()
    
    if request.method == 'POST':
        # Get selected denominations and topics from form
        denom_ids = request.form.getlist('denominations')
        topics = request.form.getlist('topics')
        
        if not denom_ids or len(denom_ids) < 2:
            flash('Please select at least two denominations to compare.', 'warning')
            return redirect(url_for('doctrine.compare'))
        
        if not topics:
            flash('Please select at least one topic to compare.', 'warning')
            return redirect(url_for('doctrine.compare'))
        
        # Get the actual denominations
        selected_denoms = Denomination.query.filter(Denomination.id.in_(denom_ids)).all()
        
        # Gather beliefs for each denomination on the selected topics
        comparison_results = {}
        for topic in topics:
            comparison_results[topic] = {}
            for denom in selected_denoms:
                belief = Belief.query.filter_by(denomination_id=denom.id, topic=topic).first()
                if belief:
                    comparison_results[topic][denom.name] = {
                        'summary': belief.summary,
                        'scripture_references': belief.scripture_references
                    }
                else:
                    comparison_results[topic][denom.name] = {
                        'summary': 'No information available',
                        'scripture_references': ''
                    }
        
        # Render the comparison results
        return render_template(
            'doctrine/compare.html',
            denominations=denominations,
            selected_denoms=selected_denoms,
            topics=topics,
            results=comparison_results
        )
    
    # GET request - show the comparison form
    topics = db.session.query(Belief.topic).distinct().all()
    topics = [topic[0] for topic in topics]
    
    return render_template(
        'doctrine/compare.html',
        denominations=denominations,
        topics=topics
    )


@doctrine_bp.route('/save_comparison', methods=['POST'])
@login_required
def save_comparison():
    """Save a doctrine comparison result"""
    title = request.form.get('title')
    description = request.form.get('description')
    denom_ids = request.form.getlist('denominations')
    topics = request.form.getlist('topics')
    results = request.form.get('results')
    
    if not title or not denom_ids or not topics or not results:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Create new comparison record
    new_comparison = DoctrineComparison(
        title=title,
        description=description,
        denominations=','.join(denom_ids),
        topics=','.join(topics),
        results=results,
        user_id=current_user.id
    )
    
    try:
        db.session.add(new_comparison)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comparison saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@doctrine_bp.route('/my_comparisons')
@login_required
def my_comparisons():
    """View saved comparisons"""
    comparisons = DoctrineComparison.query.filter_by(user_id=current_user.id).all()
    return render_template('doctrine/my_comparisons.html', comparisons=comparisons)


@doctrine_bp.route('/comparison/<int:id>')
@login_required
def view_comparison(id):
    """View a specific saved comparison"""
    comparison = DoctrineComparison.query.get_or_404(id)
    
    # Check if the user is the owner
    if comparison.user_id != current_user.id:
        flash('You do not have permission to view this comparison.', 'danger')
        return redirect(url_for('doctrine.my_comparisons'))
    
    # Parse the denominations and topics
    denom_ids = comparison.denominations.split(',')
    topics = comparison.topics.split(',')
    
    # Get the denomination objects
    denominations = Denomination.query.filter(Denomination.id.in_(denom_ids)).all()
    
    # Parse the results
    results = json.loads(comparison.results)
    
    return render_template(
        'doctrine/view_comparison.html',
        comparison=comparison,
        denominations=denominations,
        topics=topics,
        results=results
    )


@doctrine_bp.route('/api/topics/<int:denomination_id>')
def get_denomination_topics(denomination_id):
    """API endpoint to get topics for a specific denomination"""
    beliefs = Belief.query.filter_by(denomination_id=denomination_id).all()
    topics = [belief.topic for belief in beliefs]
    return jsonify(topics)


@doctrine_bp.route('/amillennial_comparison')
@login_required
def amillennial_comparison():
    """Special comparison view with amillennial theology as the foundation"""
    # Get the Amillennial denomination
    amillennial = Denomination.query.filter_by(name="Amillennial").first()
    
    if not amillennial:
        flash('Amillennial theological foundation not found.', 'warning')
        return redirect(url_for('doctrine.index'))
    
    # Get all other denominations
    other_denominations = Denomination.query.filter(Denomination.id != amillennial.id).all()
    
    # Get amillennial beliefs/topics
    amillennial_beliefs = Belief.query.filter_by(denomination_id=amillennial.id).all()
    topics = [belief.topic for belief in amillennial_beliefs]
    
    # If we're submitting the form with selected denominations
    if request.method == 'GET' and request.args.get('compare') == 'true':
        selected_denomination_ids = request.args.getlist('denominations')
        
        if not selected_denomination_ids:
            flash('Please select at least one denomination to compare with amillennial theology.', 'warning')
            return render_template(
                'doctrine/amillennial_comparison.html',
                amillennial=amillennial,
                other_denominations=other_denominations,
                topics=topics
            )
        
        # Get the actual denominations
        selected_denoms = Denomination.query.filter(Denomination.id.in_(selected_denomination_ids)).all()
        selected_denoms.insert(0, amillennial)  # Ensure amillennial is first
        
        # Gather comparison results
        comparison_results = {}
        for topic in topics:
            comparison_results[topic] = {}
            
            # Get the amillennial belief for this topic
            amillennial_belief = Belief.query.filter_by(
                denomination_id=amillennial.id, 
                topic=topic
            ).first()
            
            if amillennial_belief:
                comparison_results[topic][amillennial.name] = {
                    'summary': amillennial_belief.summary,
                    'scripture_references': amillennial_belief.scripture_references
                }
            else:
                comparison_results[topic][amillennial.name] = {
                    'summary': 'No information available',
                    'scripture_references': ''
                }
            
            # Get the beliefs for other denominations
            for denom in selected_denoms[1:]:  # Skip amillennial since we've already added it
                belief = Belief.query.filter_by(denomination_id=denom.id, topic=topic).first()
                if belief:
                    comparison_results[topic][denom.name] = {
                        'summary': belief.summary,
                        'scripture_references': belief.scripture_references
                    }
                else:
                    comparison_results[topic][denom.name] = {
                        'summary': 'No information available',
                        'scripture_references': ''
                    }
        
        # Render the comparison results
        return render_template(
            'doctrine/amillennial_comparison.html',
            amillennial=amillennial,
            other_denominations=other_denominations,
            selected_denoms=selected_denoms,
            topics=topics,
            results=comparison_results
        )
    
    # Initial form view
    return render_template(
        'doctrine/amillennial_comparison.html',
        amillennial=amillennial,
        other_denominations=other_denominations,
        topics=topics
    )
