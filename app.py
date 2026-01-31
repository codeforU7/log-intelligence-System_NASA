from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_connection, execute_query
from .analysis import simulate_security_analysis

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stats")
def get_stats():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}

    # Total logs
    total_logs = execute_query(conn, "SELECT COUNT(*) FROM logs")[0][0]

    # 4xx error percentage
    total_4xx = execute_query(conn, "SELECT COUNT(*) FROM logs WHERE status >= 400 AND status < 500")[0][0]
    error_4xx_pct = (total_4xx / total_logs * 100) if total_logs > 0 else 0

    # 5xx error percentage
    total_5xx = execute_query(conn, "SELECT COUNT(*) FROM logs WHERE status >= 500")[0][0]
    error_5xx_pct = (total_5xx / total_logs * 100) if total_logs > 0 else 0

    conn.close()
    return {
        "total_logs": total_logs,
        "error_4xx_percentage": round(error_4xx_pct, 2),
        "error_5xx_percentage": round(error_5xx_pct, 2)
    }

@app.get("/top-endpoints")
def get_top_endpoints():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}

    results = execute_query(conn, """
        SELECT endpoint, COUNT(*) as count
        FROM logs
        GROUP BY endpoint
        ORDER BY count DESC
        LIMIT 10
    """)

    conn.close()
    return [{"endpoint": row[0], "count": row[1]} for row in results]

@app.get("/top-ips")
def get_top_ips():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}

    results = execute_query(conn, """
        SELECT ip, COUNT(*) as count
        FROM logs
        GROUP BY ip
        ORDER BY count DESC
        LIMIT 10
    """)

    conn.close()
    return [{"ip": row[0], "count": row[1]} for row in results]

@app.get("/requests-over-time")
def get_requests_over_time():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}
    # For NASA logs timestamp like: 01/Aug/1995:00:00:17 -0400
    # Use SUBSTR to extract DD/Mon/YYYY:HH as a time bucket
    results = execute_query(conn, """
        SELECT SUBSTR(timestamp, 1, 14) as time_bucket, COUNT(*) as count
        FROM logs
        GROUP BY time_bucket
        ORDER BY time_bucket ASC
    """)

    conn.close()
    return {
        "labels": [row[0] for row in results],
        "data": [row[1] for row in results]
    }

@app.get("/search")
def search_logs(q: str):
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}
    
    if "500" in q or "error" in q.lower():
        results = execute_query(conn, "SELECT * FROM logs WHERE status >= 500 ORDER BY id DESC LIMIT 50")
        conn.close()
        return {"type": "logs", "data": [dict(zip(["id", "ip", "timestamp", "method", "endpoint", "status", "size"], row)) for row in results]}
    
    if "suspicious" in q.lower() or "security" in q.lower():
        # Call the intelligence module
        analysis = simulate_security_analysis()
        conn.close()
        return {"type": "analysis", "data": analysis}

    # Default: search by IP or Endpoint
    results = execute_query(conn, "SELECT * FROM logs WHERE ip LIKE ? OR endpoint LIKE ? LIMIT 50", (f"%{q}%", f"%{q}%"))
    conn.close()
    return {"type": "logs", "data": [dict(zip(["id", "ip", "timestamp", "method", "endpoint", "status", "size"], row)) for row in results]}
