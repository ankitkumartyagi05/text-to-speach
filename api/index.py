from app import app as flask_app

# Vercel loads this module as the serverless entrypoint.
app = flask_app
application = flask_app
