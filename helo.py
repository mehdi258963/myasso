from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
import os
import shutil

app = Flask(__name__)
app.secret_key = "secret_key"

# Initialisation de la base de données
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                denomination TEXT NOT NULL,
                status TEXT NOT NULL,
                ville TEXT NOT NULL,
                quartier TEXT NOT NULL,
                secteur TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        conn.commit()

init_db()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                flash("✅ Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for('login'))
            except:
                flash("❌ Email déjà utilisé. Veuillez essayer un autre.", "danger")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                return redirect(url_for('dashboard'))
            else:
                flash("❌ Identifiants incorrects. Veuillez réessayer.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("✅ Déconnexion réussie.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM associations")
        associations = cursor.fetchall()
    return render_template('dashboard.html', associations=associations)

@app.route('/create_association', methods=['POST'])
def create_association():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    denomination = request.form['denomination']
    status = request.form['status']
    ville = request.form['ville']
    quartier = request.form['quartier']
    secteur = request.form['secteur']
    user_id = session['user_id']
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM associations WHERE secteur = ?", (secteur,))
        existing_association = cursor.fetchone()
        if existing_association:
            flash("❌ Une autre association dans le même secteur existe déjà.", "danger")
        else:
            cursor.execute("INSERT INTO associations (denomination, status, ville, quartier, secteur, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                           (denomination, status, ville, quartier, secteur, user_id))
            conn.commit()
            flash("✅ Association créée avec succès !", "success")
    return redirect(url_for('dashboard'))

@app.route('/association/<int:association_id>')
def view_association(association_id):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM associations WHERE id = ?", (association_id,))
        association = cursor.fetchone()
    return render_template('association.html', association=association)

if __name__ == '__main__':
    app.run(debug=True)

# Génération automatique des fichiers HTML améliorés
html_templates = {
    "dashboard.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tableau de bord</title>
        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'>
    </head>
    <body class='container mt-5'>
        <h2 class='text-center'>📊 Tableau de bord</h2>
        <form method='POST' action='/create_association' class='mb-4 p-3 bg-light rounded shadow'>
            <input type='text' name='denomination' placeholder='Dénomination' class='form-control mb-2' required>
            <input type='text' name='status' placeholder='Statut' class='form-control mb-2' required>
            <input type='text' name='ville' placeholder='Ville' class='form-control mb-2' required>
            <input type='text' name='quartier' placeholder='Quartier' class='form-control mb-2' required>
            <input type='text' name='secteur' placeholder='Secteur d\'activité' class='form-control mb-2' required>
            <button type='submit' class='btn btn-primary w-100'>Créer</button>
        </form>
        <h3>📌 Liste des associations</h3>
        <ul class='list-group'>{% for association in associations %}<li class='list-group-item'><a href='/association/{{ association[0] }}'>{{ association[1] }}</a></li>{% endfor %}</ul>
        <a href='/logout' class='btn btn-danger mt-3'>🚪 Déconnexion</a>
    </body>
    </html>
    """,
    "association.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profil Association</title>
        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'>
    </head>
    <body class='container mt-5 text-center'>
        <h2>🏛️ Détails de l'Association</h2>
        <div class='card p-3 shadow'>{% if association %}<h3>{{ association[1] }}</h3><p><strong>Statut :</strong> {{ association[2] }}</p><p><strong>Ville :</strong> {{ association[3] }}</p><p><strong>Quartier :</strong> {{ association[4] }}</p><p><strong>Secteur :</strong> {{ association[5] }}</p>{% else %}<p>❌ Association non trouvée.</p>{% endif %}</div>
        <a href='/dashboard' class='btn btn-secondary mt-3'>⬅️ Retour</a>
    </body>
    </html>
    """
}

# Création des fichiers HTML améliorés
