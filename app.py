from flask import Flask, render_template
from flask_cors import CORS
from data.models import Account, Article, Tag, session

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

@app.route('/')
def home():
    per_page = 30
    
    articles = session.query(Article).limit(per_page).all()
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
    return render_template('article.html', article_id=article_id)

@app.route('/tags')
def tags():
    per_page = 100

    tags = session.query(Tag).limit(per_page).all()

    tags_list = [tag.to_dict() for tag in tags]

    return render_template('tags.html', tags=tags_list)

@app.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

if __name__ == "__main__":
    app.run(debug=True)
