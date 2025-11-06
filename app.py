from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from data.models import Account, Article, Tag, session
import requests
import jwt
import os
from functools import wraps
import bcrypt
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

def token_required(f):
    """
    Decorator that requires JWT authentication.
    Validates the token and checks for expiration.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, os.getenv("HASH_KEY"), algorithms=["HS256"])
            request.user_id = data["id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated

@app.route('/')
def home():
    per_page = 30
    
    query = session.query(Article)
    
    tag_query = request.args.get('q', '').strip()  # récupération du tag recherché

    if tag_query:
        # Jointure avec Tag via la table d’association 'possess'
        query = query.join(Article.tags).filter(Tag.name.ilike(f"%{tag_query}%"))
    
    articles = query.limit(per_page).all()

    article_list = []
    for article in articles:
        # TODO : implémenter un truc du genre quand les comptes utilisateurs seront gérés

        # # Vérifie si l'article est marqué par l'utilisateur courant
        # read = False
        # if current_user.is_authenticated:
        #     read = article in current_user.marked_articles
        
        article_dict = article.to_dict()
        article_dict['read'] = False
        article_list.append(article_dict)

    return render_template('index.html', articles=article_list, tag_query=tag_query)

@app.route('/article/<int:article_id>')
def article(article_id):

    response = requests.get(f"https://dev.to/api/articles/{article_id}?per_page=1")
    response.raise_for_status()
    api_tags = response.json()

    article = {
        "title": api_tags['title'],
        # "cover_image": api_tags.get('cover_image', ''), si on veut rajouter des images à un moment
        "body_html": api_tags.get('body_html', ''),
    }

    return render_template('article.html', article=article)

@app.route('/tags')
def tags():
    per_page = 100

    tags = session.query(Tag).limit(per_page).all()

    tags_list = [tag.to_dict() for tag in tags]

    return render_template('tags.html', tags=tags_list)

@app.route('/api/tags/search')
def search_tags():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        tags = session.query(Tag).filter(Tag.name.ilike(f"%{query}%")).limit(50).all()
        results = [tag.to_dict() for tag in tags]
    else:
        tags = session.query(Tag).limit(50).all()
        results = [tag.to_dict() for tag in tags]

    return jsonify(results)

@app.route('/log', methods=['POST'])
def log():
    email = request.form['email']
    password = request.form['password']

    account = session.query(Account).filter_by(email=email).first()

    if not account or not bcrypt.checkpw(password.encode("utf-8"), account.password.encode("utf-8")):
        return jsonify({"error": "Identifiants invalides"}), 401

    return get_token(account)

def get_token(account):
    """
    Generates a JWT token for an authenticated user account.
    """
    payload = {
        "id": account.id_account,
        "email": account.email,
        "exp": datetime.datetime.now() + datetime.timedelta(hours=1),
    }

    token = jwt.encode(payload, os.getenv("HASH_KEY"), algorithm="HS256")
    return jsonify({"token": token}), 200

@app.route("/create_account", methods=["POST"])
def create_account():
    """
    Registers a new user with an email and a hashed password.
    Returns a JWT token upon successful registration.
    """
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return jsonify({"error": "Identifiants invalides"}), 400

    existing_user = session.query(Account).filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Cet email est déjà utilisé"}), 409

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    new_account = Account(
        email=email,
        password=hashed_password,
    )
    session.add(new_account)
    session.commit()

    return get_token(new_account)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

if __name__ == "__main__":
    app.run(debug=True)
