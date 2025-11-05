from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from data.models import Account, Article, Tag, session
import requests

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

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

    return render_template('index.html', articles=article_list)

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

@app.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

if __name__ == "__main__":
    app.run(debug=True)
