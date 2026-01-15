from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import psycopg2, os, csv, io
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)
DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# --- FONCTION D'INITIALISATION AUTOMATIQUE ---
def initialisation_automatique():
    """Crée les tables si elles n'existent pas au démarrage du serveur"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gmao_users (
                id SERIAL PRIMARY KEY, 
                username TEXT UNIQUE, 
                password_hash TEXT, 
                role TEXT, 
                nom_complet TEXT
            );
            CREATE TABLE IF NOT EXISTS lignes_production (
                id SERIAL PRIMARY KEY, 
                nom_ligne TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS interventions (
                id SERIAL PRIMARY KEY, 
                date_saisie TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ligne_production TEXT, 
                machine_num TEXT, 
                nom_operateur_intervenant TEXT,
                description TEXT, 
                id_referent INTEGER, 
                statut TEXT DEFAULT 'en_attente', 
                valide_par_tech TEXT
            );
            INSERT INTO gmao_users (username, password_hash, role, nom_complet) 
            VALUES ('Admin','1234','admin','Admin') 
            ON CONFLICT DO NOTHING;
        """)
        conn.commit()
        cur.close()
        print("✅ Base de données initialisée avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
    finally:
        if conn:
            conn.close()

# --- ROUTES PAGES ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/login')
def page_login(): return render_template('login.html')

@app.route('/page_referent')
def page_referent(): return render_template('referent.html')

@app.route('/page_technicien')
def page_technicien(): return render_template('technicien.html')

@app.route('/admin')
def page_admin(): return render_template('admin.html')

# --- API AUTH ---
@app.route('/login_gmao', methods=['POST'])
def login_gmao():
    data = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, role, nom_complet FROM gmao_users WHERE username = %s AND password_hash = %s", 
               (data.get('username'), data.get('password')))
    user = cur.fetchone(); cur.close(); conn.close()
    if user: return jsonify({"status": "success", "id": user['id'], "role": user['role'], "nom": user['nom_complet']})
    return jsonify({"status": "error"}), 401

# NOUVELLE ROUTE : Login sans PIN (pour les référents)
@app.route('/api/login_sans_pin', methods=['POST'])
def login_sans_pin():
    data = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT id, role, nom_complet FROM gmao_users WHERE username = %s", (data.get('username'),))
    user = cur.fetchone(); cur.close(); conn.close()
    if user:
        return jsonify({"status": "success", "id": user['id'], "role": user['role'], "nom": user['nom_complet']})
    return jsonify({"status": "error"}), 404

# --- API LIGNES ---
@app.route('/api/lignes', methods=['GET', 'POST'])
def manage_lignes():
    conn = get_db_connection(); cur = conn.cursor()
    if request.method == 'POST':
        cur.execute("INSERT INTO lignes_production (nom_ligne) VALUES (%s) ON CONFLICT DO NOTHING", (request.json['nom'],))
        conn.commit()
    cur.execute("SELECT * FROM lignes_production ORDER BY nom_ligne ASC")
    lignes = cur.fetchall(); cur.close(); conn.close()
    return jsonify(lignes)

@app.route('/api/lignes/<int:id>', methods=['DELETE'])
def delete_ligne(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM lignes_production WHERE id = %s", (id,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"status": "deleted"})

# --- API INTERVENTIONS ---
@app.route('/api/save_intervention', methods=['POST'])
def save_intervention():
    data = request.json
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO interventions (ligne_production, machine_num, nom_operateur_intervenant, description, id_referent, statut)
        VALUES (%s, %s, %s, %s, %s, 'en_attente')
    """, (data['ligne'], data['machine'], data['nom_op'], data['description'], data['id_referent']))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"status": "success"})

@app.route('/api/historique_complet')
def get_historique_complet():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT i.*, u.nom_complet FROM interventions i
        LEFT JOIN gmao_users u ON i.id_referent = u.id
        ORDER BY i.date_saisie DESC
    """)
    rows = cur.fetchall(); cur.close(); conn.close()
    return jsonify(rows)

@app.route('/api/cloturer_gmao', methods=['POST'])
def cloturer_gmao():
    data = request.json
    nouveau_statut = data.get('statut', 'saisi_gmao')
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("UPDATE interventions SET statut = %s, valide_par_tech = %s WHERE id = %s", 
               (nouveau_statut, str(data['id_tech']), int(data['id_intervention'])))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"status": "success"})

@app.route('/api/admin/delete_inter/<int:id>', methods=['DELETE'])
def delete_inter(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM interventions WHERE id = %s", (id,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"status": "success"})

# --- API EQUIPE ---
@app.route('/api/admin/users', methods=['GET', 'POST'])
def manage_users():
    conn = get_db_connection(); cur = conn.cursor()
    if request.method == 'POST':
        d = request.json
        cur.execute("INSERT INTO gmao_users (username, password_hash, role, nom_complet) VALUES (%s,%s,%s,%s)",
                    (d['username'], d['password'], d['role'], d['nom']))
        conn.commit()
    cur.execute("SELECT id, username, role, nom_complet, password_hash FROM gmao_users ORDER BY role")
    users = cur.fetchall(); cur.close(); conn.close()
    return jsonify(users)

@app.route('/api/admin/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM gmao_users WHERE id = %s", (id,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({"status": "success"})

@app.route('/api/export_csv')
def export_csv():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("SELECT i.*, u.nom_complet as referent FROM interventions i LEFT JOIN gmao_users u ON i.id_referent = u.id")
    rows = cur.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Ligne', 'Machine', 'Referent', 'Desc', 'Statut', 'Validé par'])
    for r in rows:
        writer.writerow([r['date_saisie'], r['ligne_production'], r['machine_num'], r['referent'], r['description'], r['statut'], r['valide_par_tech']])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition":"attachment; filename=export.csv"})

@app.route('/setup_db')
def setup_db():
    initialisation_automatique()
    return "Base vérifiée et mise à jour."

if __name__ == "__main__":
    initialisation_automatique() 
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
