from app import app
from modules.apologetics import apologetics_bp

# Register the apologetics blueprint
app.register_blueprint(apologetics_bp, url_prefix='/apologetics')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
