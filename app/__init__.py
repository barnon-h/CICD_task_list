from flask import Flask
from .model import init_db

# Create flask app and initialize db
def create_app( config = None ):
    app = Flask( __name__ )
    app.config[ "DATABASE" ] = "todolist.db"

    if config:
        app.config.update( config )

    init_db( app )

    from .logic import logic_bp
    app.register_blueprint( logic_bp )

    return app