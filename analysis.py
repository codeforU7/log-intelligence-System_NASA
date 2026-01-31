"""
Mock LLM-powered security analysis for the Log Intelligence System.
Provides rule-based insights for SQL injection, bot scraping, and failed login attempts.
"""

from backend.database import create_connection


def simulate_security_analysis():
    """
    Simulate LLM-powered security pattern detection.
    Returns structured insights for SQL injection, bot scraping, and failed login bursts.
    """
    conn = create_connection('data/logs.db')
    if conn is None:
        return []
    
    cursor = conn.cursor()
    
    # 1. SQL Injection Detection (Pattern matching logs)
    sqli_samples = cursor.execute(
        "SELECT ip, endpoint FROM logs WHERE endpoint LIKE '%select%' OR endpoint LIKE '%union%' OR endpoint LIKE '%--%' LIMIT 3"
    ).fetchall()
    
    # 2. Bot/Scraping Detection (High frequency IPs)
    heavy_hitters = cursor.execute(
        "SELECT ip, COUNT(*) as count FROM logs GROUP BY ip HAVING count > 1000 ORDER BY count DESC LIMIT 1"
    ).fetchone()
    
    # 3. Failed Login Burst (403/401 errors)
    failed_logins = cursor.execute(
        "SELECT COUNT(*) as count FROM logs WHERE status IN (401, 403)"
    ).fetchone()
    
    conn.close()

    return [
        {
            "category": "SQL Injection Attempt",
            "count": len(sqli_samples) * 42 if sqli_samples else 126,  # Simulated amplification
            "sample": sqli_samples[0][1] if sqli_samples else "/cgi-bin/query?id=1' OR '1'='1",
            "risk_level": "CRITICAL",
            "insight": "Pattern detected: Heuristic analysis identified unauthorized SQL keyword injection in URL parameters."
        },
        {
            "category": "Bot Aggregator / Scraping",
            "count": heavy_hitters[1] if heavy_hitters else 1502,
            "source_ip": heavy_hitters[0] if heavy_hitters else "129.94.144.152",
            "risk_level": "MEDIUM",
            "insight": "High-frequency request burst from single IP. User-agent spoofing suspected."
        },
        {
            "category": "Failed Login Burst",
            "count": failed_logins[0] if failed_logins else 89,
            "source_ip": "199.174.141.2",
            "risk_level": "HIGH",
            "insight": "Brute force signature detected on /login or /admin endpoints within a 60-second window."
        }
    ]
