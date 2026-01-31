from backend.database import create_connection, execute_query

def detect_sql_injection():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}

    # Simple rule-based detection for SQL injection patterns
    results = execute_query(conn, """
        SELECT COUNT(*) as count, ip
        FROM logs
        WHERE endpoint LIKE '%SELECT%' OR endpoint LIKE '%UNION%' OR endpoint LIKE '%DROP%'
        GROUP BY ip
    """)

    total_attempts = sum(row[0] for row in results)
    unique_ips = len(results)
    sample_request = "Sample malicious request: /api/search?query=SELECT * FROM users"
    risk_level = "High" if total_attempts > 100 else "Medium"

    conn.close()
    return {
        "request_count": total_attempts,
        "sample_malicious_request": sample_request,
        "unique_ip_count": unique_ips,
        "risk_level": risk_level
    }

def detect_bot_scraping():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}

    # Detect high-frequency requests from same IP
    results = execute_query(conn, """
        SELECT ip, COUNT(*) as count
        FROM logs
        GROUP BY ip
        HAVING count > 1000
        ORDER BY count DESC
        LIMIT 5
    """)

    request_count = sum(row[1] for row in results)
    suspected_user_agents = ["Bot/1.0", "Scrapy/1.0"]  # Mocked
    recommendation = "Implement rate limiting and CAPTCHA"

    conn.close()
    return {
        "request_count": request_count,
        "suspected_user_agents": suspected_user_agents,
        "recommendation": recommendation
    }

def detect_failed_login_burst():
    conn = create_connection('data/logs.db')
    if conn is None:
        return {"error": "Database connection failed"}

    # Detect bursts of 401/403 errors
    results = execute_query(conn, """
        SELECT ip, COUNT(*) as count, MIN(timestamp) as start_time, MAX(timestamp) as end_time
        FROM logs
        WHERE status IN (401, 403)
        GROUP BY ip
        HAVING count > 10
        ORDER BY count DESC
        LIMIT 1
    """)

    if results:
        ip, count, start_time, end_time = results[0]
        alert_message = f"Failed login burst detected from IP {ip} with {count} attempts between {start_time} and {end_time}"
    else:
        ip, count, start_time, end_time = None, 0, None, None
        alert_message = "No significant failed login bursts detected"

    conn.close()
    return {
        "attempt_count": count,
        "source_ip": ip,
        "time_window": f"{start_time} to {end_time}" if start_time else "N/A",
        "alert_message": alert_message
    }

def get_security_insights():
    return {
        "sql_injection": detect_sql_injection(),
        "bot_scraping": detect_bot_scraping(),
        "failed_login_burst": detect_failed_login_burst()
    }
