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
                name TEXT NOT NULL,
                registration_receipt TEXT NOT NULL,
                committee_file TEXT NOT NULL,
                main_activity TEXT NOT NULL,
                objectives TEXT NOT NULL,
                domain TEXT NOT NULL,
                target_population TEXT NOT NULL,
                workforce TEXT NOT NULL,
                geographic_area TEXT NOT NULL,
                annual_budget TEXT NOT NULL,
                partnership TEXT NOT NULL,
                strengths TEXT NOT NULL,
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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM associations")
        associations = cursor.fetchall()
    return render_template('dashboard.html', associations=associations)

# Génération automatique du fichier dashboard.html
html_templates = {
    "dashboard.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tableau de bord</title>
        <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'>
        <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'>
        <script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js'></script>
    </head>
    <body class='container mt-5'>
        <h2 class='text-center animate__animated animate__fadeInDown'>📊 Tableau de bord</h2>
        <form method='POST' action='/create_association' enctype='multipart/form-data' class='mb-4 p-4 bg-light rounded shadow animate__animated animate__fadeInUp'>
            <div class='row'>
                <div class='col-md-6'>
                    <input type='text' name='name' placeholder='Nom de l\'association' class='form-control mb-3' required>
                    <label class='form-label'>Reçu définitif (PDF/JPG) :</label>
                    <input type='file' name='registration_receipt' class='form-control mb-3' accept='application/pdf, image/jpeg' required>
                    <label class='form-label'>Fiche du comité (PDF/JPG) :</label>
                    <input type='file' name='committee_file' class='form-control mb-3' accept='application/pdf, image/jpeg' required>
                    <input type='text' name='main_activity' placeholder='Activité principale' class='form-control mb-3' required>
                    <input type='text' name='objectives' placeholder='Objectifs et missions' class='form-control mb-3' required>
                </div>
                <div class='col-md-6'>
                    <input type='text' name='domain' placeholder='Domaine d\'intervention' class='form-control mb-3' required>
                    <input type='text' name='target_population' placeholder='Population cible' class='form-control mb-3' required>
                    <input type='number' name='workforce' placeholder='Effectif' class='form-control mb-3' required>
                    <input type='text' name='geographic_area' placeholder='Zone géographique' class='form-control mb-3' required>
                    <input type='text' name='annual_budget' placeholder='Budget annuel' class='form-control mb-3' required>
                    <input type='text' name='partnership' placeholder='Partenariat et sponsoring' class='form-control mb-3' required>
                    <input type='text' name='strengths' placeholder='Points forts / Bonnes pratiques' class='form-control mb-3' required>
                </div>
            </div>
            <button type='submit' class='btn btn-primary w-100 animate__animated animate__pulse animate__infinite'>Créer</button>
        </form>
        <h3 class='animate__animated animate__fadeIn'>📌 Liste des associations</h3>
        <ul class='list-group animate__animated animate__fadeInUp'>{% for association in associations %}<li class='list-group-item'><a href='/association/{{ association[0] }}'>{{ association[1] }}</a></li>{% endfor %}</ul>
        <a href='/logout' class='btn btn-danger mt-3 animate__animated animate__bounce'>🚪 Déconnexion</a>
    </body>
    </html>
    """
}

# Création automatique du fichier HTML
os.makedirs("templates", exist_ok=True)
for filename, content in html_templates.items():
    with open(f"templates/{filename}", "w") as f:
        f.write(content)

if __name__ == '__main__':
    app.run(debug=True)
