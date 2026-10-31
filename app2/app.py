from pathlib import Path

from flask import Flask

from config import Config
from data.database import db
from presentation.routes import web


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    Path(app.config["STORAGE_DIR"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(web)
    with app.app_context():
        db.create_all()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
