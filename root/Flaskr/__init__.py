"""
__init__ (usage) --> contains application factory
                 --> tells Python that the project directory (Flaskr) should
                     be treated as a package
"""
import os
from flask import Flask
from flask import render_template


# create_app is the application factory function
def create_app(test_config=None):
    # create and configure the app - creates flask instance
    app: Flask = Flask(__name__, instance_relative_config=True)
    """
    (1) --> __name__ is the name of the current Python module, this app needs to know where the file is
            located to set up paths, and __name__ is a convenient way to tell it that
            
    (2) --> instance_relative_config=True tells app that config files are relative to the instance folder
            the instance folder isn't in the project package, and can hold local data not needed in the 
            version control such as configuration secrets and the database file
    """
    # sets some default configurations that the app will use
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )
    """
    (1) --> SECRET_KEY is used by Flask and extensions to keep data safe. It's set to 'dev' during development
            but it should be overridden with a random value when deploying
    (2) --> DATABASE is the path where the SQLite database file will be saved. It's under app.instance_path,
            which is the path that Flask has chosen for the instance folder. You'll learn more about the database
            in the next section
    """

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # loads configurations from a python file in the project directory
        app.config.from_pyfile('config.py', silent=True)
        """
        (1) --> overrides default config with values taken from the config.py file in the instance folder 
                if it exists. For example, it can be used to make a real SECRET_KEY
        """
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
        """
        (1) --> test_config can also be passed to the factory instead of the instance config. the tests can be
                configured independently from any dev values
        """

    # ensure that the instance folder exists
    # if it doesn't exist, it will make it, if it does, an error will occur and pass
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page saying hello
    @app.route('/hello')
    def hello():
        return 'Hello, World'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
