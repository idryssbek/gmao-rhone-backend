from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

DB_URL = "postgresql://mademoiselle_rhone_db_user:MgE4EgSZrKTahlaJ13uGpGNDsRFG6Qq4@dpg-d53fbif5r7bs73dq0jug-a.frankfurt-postgres.render.com/mademoiselle_rhone_db"

@app.route('/')
def home():
    return "Serveur GMAO Actif"

@app.route('/login_gmao', methods=['POST'])
def login_gmao():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, role, nom_complet FROM gmao_users WHERE username = %s AND password_hash = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return jsonify({"status": "success", "role": user[1], "nom": user[2]})
        return jsonify({"status": "error", "message": "Identifiants incorrects"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
