from flask import Flask
from models.base import db
from flask_migrate import Migrate
app = Flask(__name__)
app.secret_key = "SECRET"
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:password@localhost:3306/chat_db"
db.init_app(app)
migrate = Migrate(app, db)