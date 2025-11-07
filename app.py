from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "ton_secret_key"  # nécessaire pour les sessions

# Page d'accueil
@app.route('/')
def home():
    articles = [
        {"title": "Build in Public: Day Zero", "desc": "A few weeks ago we built an agent called WYKRA for the Real-Time AI Agents challenge powered by...", "read": True},
        {"title": "AI Trends 2025", "desc": "Discover the latest in artificial intelligence and its real-world applications.", "read": False},
        {"title": "Web Development in 2025", "desc": "What’s new in frontend, backend, and frameworks this year.", "read": True},
    ]
    return render_template('index.html', active_page='home', articles=articles, user=session.get('user'))

# Page tags
@app.route('/tags')
def tags():
    return render_template('tags.html', active_page='tags', user=session.get('user'))

# Page article
@app.route('/article/<int:article_id>')
def article(article_id):
    articles = [
        {"title": "Build in Public: Day Zero", "desc": "Full article content here..."},
        {"title": "AI Trends 2025", "desc": "AI article content here..."},
        {"title": "Web Development in 2025", "desc": "WebDev article content here..."},
    ]
    if 0 <= article_id < len(articles):
        return render_template('article.html', article=articles[article_id], active_page='article', user=session.get('user'))
    return "Article non trouvé", 404

# Mentions légales
@app.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions_legales.html', active_page='mentions', user=session.get('user'))

# Cookies
@app.route('/cookies')
def cookies():
    return render_template('cookies.html', active_page='cookies', user=session.get('user'))

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact', user=session.get('user'))

# Page login / inscription
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Ici tu pourrais vérifier les identifiants dans une base
        session['user'] = email
        return redirect(url_for('home'))
    return render_template('login.html', active_page='login', user=session.get('user'))

# Page compte utilisateur
@app.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('account.html', active_page='account', user=session.get('user'))

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# Suppression compte
@app.route('/delete_account')
def delete_account():
    # Ici tu pourrais supprimer l'utilisateur de ta base
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
