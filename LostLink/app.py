from flask import Flask, render_template
from config import Config
from database.mongo import init_db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        init_db(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.items import items_bp
    from routes.matches import matches_bp
    from routes.notifications import notif_bp
    from routes.claims import claims_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(claims_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
