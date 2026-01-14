from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)

# Récupération de la variable d'environnement sur Render
DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# --- ROUTES NAVIGATION (HTML) ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/page_operateur')
def page_operateur():
    return render_template('operateur.html')

@app.route('/page_login')
def page_login():
    return render_template('login.html')

@app.route('/page_referent')
def page_referent():
    return render_template('referent.html')

# --- ROUTES API (DATA) ---

@app.route('/login_gmao', methods=['POST'])
def login_gmao():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, role, nom_complet FROM gmao_users WHERE username = %s AND password_hash = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return jsonify({"status": "success", "id": user['id'], "role": user['role'], "nom": user['nom_complet']})
        return jsonify({"status": "error", "message": "Identifiants incorrects"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 1. Remontée simple Opérateur
@app.route('/api/remarque_op', methods=['POST'])
def save_remarque():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO remarques_operateurs (commentaire) VALUES (%s)", (data['commentaire'],))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 2. Enregistrement intervention Référent
@app.route('/api/save_intervention', methods=['POST'])
def save_intervention():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO interventions (ligne_production, machine_num, nom_operateur_intervenant, description, id_referent)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['ligne'], data['machine'], data['nom_op'], data['description'], data['id_referent']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. Historique 30 jours pour le Référent
@app.route('/api/historique/<int:referent_id>', methods=['GET'])
def get_historique(referent_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM interventions 
            WHERE id_referent = %s AND date_saisie > NOW() - INTERVAL '30 days'
            ORDER BY date_saisie DESC
        """, (referent_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. Validation Technicien (Mise à jour immédiate)
@app.route('/api/valider_intervention', methods=['POST'])
def valider_intervention():
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE interventions 
            SET statut = 'valide', valide_par_tech = %s 
            WHERE id = %s
        """, (data['id_tech'], data['id_intervention']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
