from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import User


@app.route('/')
def index():
    """Home page of the eAI Ministry Tool"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Form validation
        if not username or not email or not password or not password_confirm:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists.', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')
    
    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('auth/login.html')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard for logged-in users"""
    # Direct template rendering without passing model objects
    # This avoids SQLAlchemy queries that might fail if schema changed
    return render_template('dashboard.html')


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 error page"""
    return render_template('500.html'), 500


@app.route('/user_guide')
def user_guide():
    """User guide and documentation"""
    return render_template('user_guide.html')
