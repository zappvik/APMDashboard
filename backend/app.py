from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

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
    cur.execute("""
        SELECT time, usage_user
        FROM cpu
        WHERE time > NOW() - INTERVAL '10 minutes'
        ORDER BY time ASC;
    """)
    raw_data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    results = [dict(zip(column_names, row)) for row in raw_data]
    cur.close()
    conn.close()
    return jsonify(results)

# --- NEW ENDPOINT FOR MEMORY DATA ---
@app.route('/api/mem-data')
def get_mem_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT time, used_percent
        FROM mem
        WHERE time > NOW() - INTERVAL '10 minutes'
        ORDER BY time ASC;
    """)
    raw_data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    results = [dict(zip(column_names, row)) for row in raw_data]
    cur.close()
    conn.close()
    return jsonify(results)

# --- NEW ENDPOINT FOR APPLICATION STATUS ---
@app.route('/api/status-data')
def get_status_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT result_code 
        FROM http_response
        ORDER BY time DESC
        LIMIT 1;
    """)
    # Fetch one result, default to 0 if no data
    status = cur.fetchone()
    result_code = status[0] if status else 0
    cur.close()
    conn.close()
    return jsonify({'status': result_code})


if __name__ == '__main__':
    app.run(debug=True, port=5000)