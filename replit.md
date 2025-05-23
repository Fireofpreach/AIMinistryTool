# eAI Ministry Tool

## Overview
The eAI Ministry Tool is a web application designed to assist ministry leaders with various aspects of their work. The application includes modules for doctrine comparison, sermon building, pastoral counseling, and theological resources. It's built with Flask and uses SQLAlchemy for database operations.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
The application follows a modular architecture using Flask blueprints to organize functionality into distinct components:

1. **Core Application Structure**:
   - Flask web framework as the foundation
   - SQLAlchemy ORM for database interactions
   - Flask-Login for user authentication and session management
   - Blueprints for modular organization

2. **Frontend**:
   - HTML templates with Jinja2 templating
   - Bootstrap CSS framework (via CDN) for responsive design
   - Custom CSS for styling enhancements
   - JavaScript for interactive features

3. **Backend**:
   - Python 3.11
   - Flask routes handling HTTP requests
   - SQLAlchemy models for data persistence
   - Blueprint-based module organization

4. **Database**:
   - SQLAlchemy with SQLite (development/default)
   - Configurable to use PostgreSQL in production

## Key Components

### Core Application
- `app.py`: Core application setup, initializes Flask, SQLAlchemy, and registers blueprints
- `main.py`: Entry point for running the application
- `models.py`: Database models for the application
- `routes.py`: Main application routes

### Module System
The application is organized into feature-specific modules:
- **Doctrine Module**: Compare theological positions between denominations
- **Sermon Module**: Tools for creating and managing sermon content
- **Counseling Module**: Resources for pastoral counseling sessions
- **Resources Module**: Library of theological materials

### Authentication System
- User registration and login functionality
- Role-based access control (user, admin, pastor roles)
- Session management with Flask-Login

### Database Models
- `User`: User account information and authentication
- `Denomination`: Religious denominations and their core beliefs
- `Belief`: Theological positions for different denominations
- `Sermon`: Sermon content and metadata
- `CounselingSession`: Pastoral counseling session records
- (Additional models for resources and other features)

## Data Flow

### Authentication Flow
1. User registers or logs in via web interface
2. Credentials are validated against the database
3. Flask-Login manages user sessions
4. Role-based permissions control access to features

### Doctrine Comparison Flow
1. User selects denominations and topics to compare
2. Application queries database for relevant beliefs
3. Comparison results are rendered in the template
4. Users can save comparisons for future reference

### Sermon Builder Flow
1. User enters sermon details (title, scripture, theme)
2. Optional AI assistance for outlines and illustrations
3. Content is saved to the database
4. Users can edit, view, and manage sermon content

### Counseling Session Flow
1. User creates a new counseling session
2. System provides relevant scripture and guidance
3. Session notes and details are saved
4. Follow-up sessions can reference previous content

## External Dependencies
- Flask: Web framework
- Flask-SQLAlchemy: ORM for database operations
- Flask-Login: User authentication and sessions
- Gunicorn: WSGI HTTP server for production
- Bootstrap (via CDN): Frontend framework
- Font Awesome (via CDN): Icon library
- PostgreSQL (optional): Production database
- Email Validator: Validate email addresses
- Flask-Dance: OAuth integration (prepared but may not be fully implemented)
- PyJWT: JSON Web Tokens for authentication

## Deployment Strategy
The application is configured for deployment on Replit:

1. **Development Environment**:
   - Running with Flask's built-in server (`app.run()`)
   - SQLite database for simplicity

2. **Production Environment**:
   - Gunicorn as the WSGI server
   - Configured for autoscaling deployment
   - Environment variables for configuration (DATABASE_URL, SESSION_SECRET)
   - PostgreSQL database (referenced in dependencies)

3. **Configuration**:
   - `.replit` file defines deployment settings
   - Gunicorn configured to bind to 0.0.0.0:5000
   - Port reuse enabled for development convenience

4. **Workflow**:
   - Custom workflow for starting the application
   - Uses gunicorn with automatic reloading for development