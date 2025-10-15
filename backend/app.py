from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import socket

app = Flask(__name__)
CORS(app)

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "MySecretPwd123!"  # Use your actual password


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )
    return conn


@app.route("/api/cpu-data")
def get_cpu_data():
    conn = get_db_connection()
    cur = conn.cursor()
    # --- CORRECTED QUERY IS HERE ---
    cur.execute("""
        SELECT
            time_bucket_gapfill('5 seconds', time, now() - interval '10 minutes', now()) as time,
            COALESCE(AVG(usage_user), 0) as usage_user
        FROM cpu
        WHERE time > NOW() - INTERVAL '10 minutes'
        GROUP BY 1
        ORDER BY 1 ASC;
    """)
    raw_data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    results = [dict(zip(column_names, row)) for row in raw_data]
    cur.close()
    conn.close()
    return jsonify(results)


@app.route("/api/mem-data")
def get_mem_data():
    conn = get_db_connection()
    cur = conn.cursor()
    # --- CORRECTED QUERY IS HERE ---
    cur.execute("""
        SELECT
            time_bucket_gapfill('5 seconds', time, now() - interval '10 minutes', now()) as time,
            COALESCE(AVG(used_percent), 0) as used_percent
        FROM mem
        WHERE time > NOW() - INTERVAL '10 minutes'
        GROUP BY 1
        ORDER BY 1 ASC;
    """)
    raw_data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    results = [dict(zip(column_names, row)) for row in raw_data]
    cur.close()
    conn.close()
    return jsonify(results)


@app.route("/api/check-port/<int:port>")
def check_port_status(port):
    try:
        with socket.create_connection(("localhost", port), timeout=1):
            return jsonify({"status": 200, "port": port, "message": "OK"})
    except (ConnectionRefusedError, socket.timeout):
        return jsonify({"status": 503, "port": port, "message": "Service Unavailable"})
    except Exception as e:
        return jsonify({"status": 500, "port": port, "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)