"""
This is the file for the database, using SQLite
"""
import click
import sqlite3
from flask import current_app, g
from flask.cli import with_appcontext
"""
g is a special object that is unique for each request - stores data that is accessed by multiple functions
connection is stored and re-used instead of creating a new connection if get_db is called a second time in
the same request.
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        """
        (1) --> current_app is another special obj that points to the Flask app running the request.
        (2) --> sqlite3.connect() establishes a connection to the file pointed at by the DATABASE config
                key. This file doesn't have to exist yet, and won't exist until you initialize it later
        """
        g.db.row_factory = sqlite3.Row
        """
        sqlite3.Row tells the connection to return rows that behave like dicts, which allows accessing
        the columns by name
        """

    return g.db


# checks for connection --> check if g.db set, if connection exists it will be closed
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()

    """
    opens a file relative to the Flaskr pkg, which is useful since you won't necessarily know where
    the location is when deploying the application later. get_db returns a database connection, 
    which is used to execute the commands read from the file.
    """
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


"""
click.command is a command that a command-line command that runs init-db which runs init_db 
and shows a success message to the user
"""


@click.command('init-db')
@with_appcontext
def init_db_command():
    """clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # tells Flask to call that function when cleaning up after returning the response
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with the flask command. Import and call this function from the factory
    # place new code at the end of the factory function before returning the app
    app.cli.add_command(init_db_command)