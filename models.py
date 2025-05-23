from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    """User model for authentication and profile information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default='user')  # 'user', 'admin', 'pastor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sermons = db.relationship('Sermon', backref='author', lazy='dynamic')
    counseling_sessions = db.relationship('CounselingSession', backref='counselor', lazy='dynamic')
    sermon_series = db.relationship('SermonSeries', backref='author', lazy='dynamic')
    apologetics_responses = db.relationship('ApologeticsResponse', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Denomination(db.Model):
    """Model for storing different religious denominations and their core beliefs"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    beliefs = db.relationship('Belief', backref='denomination', lazy='dynamic')
    
    def __repr__(self):
        return f'<Denomination {self.name}>'


class Belief(db.Model):
    """Model for individual beliefs or doctrines within a denomination"""
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    scripture_references = db.Column(db.Text)  # Stored as JSON or comma-separated values
    denomination_id = db.Column(db.Integer, db.ForeignKey('denomination.id'), nullable=False)
    
    def __repr__(self):
        return f'<Belief {self.topic}>'


class SermonSeries(db.Model):
    """Model for sermon series planning"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    theme = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to sermons
    sermons = db.relationship('Sermon', backref='series', lazy='dynamic')
    
    def __repr__(self):
        return f'<SermonSeries {self.title}>'


class Sermon(db.Model):
    """Model for sermon details and content"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    scripture_passage = db.Column(db.String(200))
    theme = db.Column(db.String(100))
    content = db.Column(db.Text)
    outline = db.Column(db.Text)  # JSON structure for sermon outline
    illustrations = db.Column(db.Text)  # JSON structure for illustrations
    sermon_date = db.Column(db.Date)
    series_position = db.Column(db.Integer)  # Position in sermon series
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('sermon_series.id'), nullable=True)
    
    def __repr__(self):
        return f'<Sermon {self.title}>'


class CounselingSession(db.Model):
    """Model for pastoral counseling sessions"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    topic = db.Column(db.String(100))  # e.g., marriage, grief, addiction
    notes = db.Column(db.Text)
    scripture_references = db.Column(db.Text)  # Stored as JSON or comma-separated values
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<CounselingSession {self.title}>'


class Resource(db.Model):
    """Model for theological resources and materials"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    resource_type = db.Column(db.String(50))  # book, article, video, etc.
    topic = db.Column(db.String(100))
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # For articles, excerpts, or summaries
    url = db.Column(db.String(500))  # For external resources
    tags = db.Column(db.String(200))  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_amillennial = db.Column(db.Boolean, default=False)  # Mark resources from amillennial authors
    
    def __repr__(self):
        return f'<Resource {self.title}>'


class DoctrineComparison(db.Model):
    """Model for saved doctrine comparisons"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    denominations = db.Column(db.String(200))  # Comma-separated denomination IDs
    topics = db.Column(db.String(200))  # Comma-separated belief topics
    results = db.Column(db.Text)  # JSON of comparison results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<DoctrineComparison {self.title}>'


class ApologeticsCategory(db.Model):
    """Model for categorizing apologetics objections and responses"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    objections = db.relationship('ApologeticsObjection', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<ApologeticsCategory {self.name}>'


class ApologeticsObjection(db.Model):
    """Model for common objections to amillennialism or related doctrines"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    objection_text = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(200))  # Source of the objection, e.g., "Dispensationalism"
    difficulty_level = db.Column(db.Integer)  # 1-5 scale of how difficult this objection is
    category_id = db.Column(db.Integer, db.ForeignKey('apologetics_category.id'), nullable=False)
    
    # Relationships
    responses = db.relationship('ApologeticsResponse', backref='objection', lazy='dynamic')
    
    def __repr__(self):
        return f'<ApologeticsObjection {self.title}>'


class ApologeticsResponse(db.Model):
    """Model for responses to apologetics objections"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    scripture_references = db.Column(db.Text)  # Key scriptures supporting this response
    additional_resources = db.Column(db.Text)  # JSON list of related resources
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    objection_id = db.Column(db.Integer, db.ForeignKey('apologetics_objection.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<ApologeticsResponse {self.title}>'


class TheologicalAuthor(db.Model):
    """Model for notable theological authors, particularly amillennial ones"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    timeperiod = db.Column(db.String(100))  # e.g., "4th Century" or "Contemporary"
    tradition = db.Column(db.String(100))  # e.g., "Reformed", "Lutheran", etc.
    bio = db.Column(db.Text)
    is_amillennial = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))
    
    # Relationships
    works = db.relationship('TheologicalWork', backref='author', lazy='dynamic')
    quotes = db.relationship('TheologicalQuote', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return f'<TheologicalAuthor {self.name}>'


class TheologicalWork(db.Model):
    """Model for works by theological authors"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.String(20))
    description = db.Column(db.Text)
    content_excerpt = db.Column(db.Text)
    url = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('theological_author.id'), nullable=False)
    
    def __repr__(self):
        return f'<TheologicalWork {self.title}>'


class TheologicalQuote(db.Model):
    """Model for quotes from theological authors, particularly on amillennialism"""
    id = db.Column(db.Integer, primary_key=True)
    quote_text = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(200))
    topic = db.Column(db.String(100))
    context = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('theological_author.id'), nullable=False)
    
    def __repr__(self):
        return f'<TheologicalQuote {self.id}>'