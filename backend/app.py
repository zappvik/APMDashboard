from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app) # Enables cross-origin requests

# --- Database Connection Details ---
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "MySecretPwd123!" # Use your actual password

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route('/api/cpu-data')
def get_cpu_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Query for the last 10 minutes of CPU data
    cur.execute("""
        SELECT time, usage_user
        FROM cpu
        WHERE time > NOW() - INTERVAL '10 minutes'
        ORDER BY time ASC;
    """)
    
    # Fetch all rows and format them as a list of dictionaries
    raw_data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    
    results = []
    for row in raw_data:
        results.append(dict(zip(column_names, row)))
        
    cur.close()
    conn.close()
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)