from flask import Flask, request, render_template, redirect, session, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models.base import db
from models.user import User
from models.chat import Chat
from utils import encrypt_aes, decrypt_aes, generate_key_iv
from flask_migrate import Migrate
import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
import uuid
import os

user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
port = os.environ.get("DB_PORT")
database = os.environ.get("DB_NAME")

app = Flask(__name__)
app.secret_key = "SECRET"
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

# initialize the app with the extension
db.init_app(app)
migrate = Migrate(app, db)

key, iv = generate_key_iv()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('jwt_token')

        if not token:
            # return jsonify({'message': 'Token is missing!'}), 401
            return render_template('login.html', message="Expired Token")

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except:
            # return jsonify({'message': 'Token is invalid!'}), 401
            return render_template('login.html', message="Token is Invalid!")

        return f(current_user, *args, **kwargs)

    return decorated

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        # Validate form data
        password = request.form.get("password")
        email = request.form.get("email")

        if not (password and email):
            return render_template("register.html", message="All fields are required.")
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template("register.html", message="User with Email exists")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Store user data in the database
        user = User(
            user_id=str(uuid.uuid4()),
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Retrieve user data from the database
        user = User.query.filter_by(email=email).first()
        print(user)
        # Check if username exists and password is correct
        if user and check_password_hash(user.password, password):
            user.status = True
            token = jwt.encode({'user_id': user.user_id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)}, app.config['SECRET_KEY'],algorithm = "HS256")
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('jwt_token', token)
            # print(session)
            db.session.commit() # update the status
            return response
        else:
            return render_template("login.html", message="Invalid email or password.")

    return render_template("login.html")


@app.route('/dashboard', methods=["GET"])
@app.route('/dashboard/<email>', methods=["GET", "POST"])
@token_required
def dashboard(user, email=None, to_email=None):
    if not email:
        users = User.query.all()
        return render_template("dashboard.html", users=users, my_email=user.email, to_email=user.email)
        # return f"Welcome {user.email}! You are logged in."
    else:
        if request.method == "GET":
            users = User.query.filter_by(email=email.strip()).all()
            to_user = User.query.filter_by(email=email.strip()).first()
            to_email = to_user.email
            chats = Chat.query.filter(
            ((Chat.message_from == user.email) & (Chat.message_to == email)) |
            ((Chat.message_from == email) & (Chat.message_to == user.email))
        ).order_by(Chat.created_at.asc()).all()
            length = len(chats)
            for chat in chats:
                chat.message = decrypt_aes(chat.message, key, iv)
            print(chats)
            return render_template("dashboard.html", users=users, my_email= user.email, to_email=to_email, chats=chats, length=length)
        if request.method == "POST":
            # to_user = User.query.filter_by(email=email.strip()).first()
            message_text = request.form.get("message")
            new_chat = Chat(
                chat_id=str(uuid.uuid4()),
                message_from=user.email,
                message_to=email,
                message=str(encrypt_aes(message_text, key, iv)),
            )
            db.session.add(new_chat)
            db.session.commit()
        
        return redirect(url_for("dashboard", email=email))
    
@app.route('/logout')
@token_required
def logout(user):
    user.status = False
    db.session.commit()
    response = make_response(redirect('/'))
    response.delete_cookie('jwt_token')
    return response

        


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
