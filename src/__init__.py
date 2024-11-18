from flask import Flask
from config import Config
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db = SQLAlchemy()
mail = Mail()

def create_app():
  import src.routes as routes
  app = Flask(__name__)
  app.config.from_object(Config)
  
  db.init_app(app)
  migrate = Migrate(app , db)

  app.register_blueprint(routes.simple_page)
  mail.init_app(app)
  return app


def setup_mail(app):
  return Mail(app)

