from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Récupération de la variable d'environnement sur Render
DB_URL = os.environ.get("DATABASE_URL")

@app.route('/')
def home():
    return "Serveur GMAO Actif avec Variables d'Environnement"

@app.route('/login_gmao', methods=['POST'])
def login_gmao():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not DB_URL:
        return jsonify({"status": "error", "message": "Base de données non configurée sur Render"}), 500

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        # Vérification des identifiants dans la table
        cur.execute("SELECT id, role, nom_complet FROM gmao_users WHERE username = %s AND password_hash = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return jsonify({"status": "success", "role": user[1], "nom": user[2]})
        return jsonify({"status": "error", "message": "Identifiants incorrects"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/debug_users')
def debug_users():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT username, password_hash, nom_complet FROM gmao_users")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(users)
    except Exception as e:
        return str(e)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
