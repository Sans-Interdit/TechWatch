from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from data.models import Account, Article, Tag, session as db_session
import requests
import os
import bcrypt
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import asyncio
from googletrans import Translator

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
CORS(app)

chatbot_key = os.getenv("KEY")

client = InferenceClient(
    provider="hf-inference",
    api_key=chatbot_key,
)

@app.route("/summary", methods=["POST"])
def summary():
    article = request.json.get("article")

    def chunk_text(text, max_words=500):
        words = text.split()
        for i in range(0, len(words), max_words):
            yield " ".join(words[i:i+max_words])

    summaries = []

    for chunk in chunk_text(article, max_words=500):
        summary = client.summarization(
            chunk,
            model="sshleifer/distilbart-cnn-12-6",
        )
        summaries.append(summary['summary_text'])

    # Résumé final : concatène les résumés puis éventuellement résume à nouveau
    final_summary_text = " ".join(summaries)
    final_summary = client.summarization(
        final_summary_text,
        model="sshleifer/distilbart-cnn-12-6",
    )

    translator = Translator()

    # Fonction pour traduire
    async def traduire_texte(texte):
        result = await translator.translate(texte, dest='fr')
        return result.text

    translated_summary = asyncio.run(traduire_texte(final_summary['summary_text']))

    return jsonify({'response': translated_summary}), 200

@app.route('/api/tags/search')
def search_tags():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        tags = db_session.query(Tag).filter(Tag.name.ilike(f"%{query}%")).limit(50).all()
        results = [tag.to_dict() for tag in tags]
    else:
        tags = db_session.query(Tag).limit(50).all()
        results = [tag.to_dict() for tag in tags]

    return jsonify(results)

# ===== PAGE D’ACCUEIL =====
@app.route('/')
def home():
    per_page = 30
    
    query = db_session.query(Article)
    
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

    return render_template('index.html', articles=article_list, tag_query=tag_query,  active_page='home', user=session.get('user'))

# ===== PAGE ARTICLE =====
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

    return render_template('article.html', article=article, active_page='article', user=session.get('user'))

# ===== PAGE TAGS =====
@app.route('/tags')
def tags():
    per_page = 100

    tags = db_session.query(Tag).limit(per_page).all()

    tags_list = [tag.to_dict() for tag in tags]

    return render_template('tags.html', tags=tags_list, active_page='tags', user=session.get('user'))

# ===== PAGE LOGIN =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        account = db_session.query(Account).filter_by(email=email).first()

        if not account or not bcrypt.checkpw(password.encode("utf-8"), account.password.encode("utf-8")):
            return render_template('login.html', active_page='login', user=session.get('user'), error="Identifiants invalides")
        
        session['user'] = email
        return redirect(url_for('home'))
    return render_template('login.html', active_page='login', user=session.get('user'))

# ===== PAGE INSCRIPTION =====
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password-confirm")

        if not email or not password:
            return render_template('register.html', active_page='register', user=session.get('user'), error="Identifiants invalides")
        print(password_confirm, password)

        if password != password_confirm:
            return render_template('register.html', active_page='register', user=session.get('user'), error="Les mots de passe ne correspondent pas")

        existing_user = db_session.query(Account).filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', active_page='register', user=session.get('user'), error="Cet email est déjà utilisé")

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        new_account = Account(
            email=email,
            password=hashed_password,
        )
        db_session.add(new_account)
        db_session.commit()

        session['user'] = email
        return redirect(url_for('home'))
    return render_template('register.html', active_page='register', user=session.get('user'))

# ===== MENTIONS LÉGALES =====
@app.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions_legales.html', active_page='mentions', user=session.get('user'))

# ===== COOKIES =====
@app.route('/cookies')
def cookies():
    return render_template('cookies.html', active_page='cookies', user=session.get('user'))

# ===== PAGE CONTACT =====
@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact', user=session.get('user'))


# ===== PAGE MON COMPTE =====
@app.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('account.html', active_page='account', user=session.get('user'))

# ===== DÉCONNEXION =====
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# ===== PAGE À PROPOS =====
@app.route('/about')
def about():
    return render_template('about.html', active_page='about', user=session.get('user'))

# ===== SUPPRESSION DE COMPTE =====
@app.route('/delete_account')
def delete_account():
    session_user = session.get('user')
    db_session.query(Account).filter_by(email=session_user).delete()
    db_session.commit()

    session.pop('user', None)
    return redirect(url_for('home'))

# ===== LANCEMENT DE L’APPLICATION =====
if __name__ == '__main__':
    app.run(debug=True)