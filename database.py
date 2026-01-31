import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def initialize_database(db_file):
    """Initialize the database with logs table and indexes"""
    sql_create_logs_table = """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        timestamp TEXT,
        method TEXT,
        endpoint TEXT,
        status INTEGER,
        size INTEGER
    );
    """

    sql_create_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_status ON logs(status);",
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp);",
        "CREATE INDEX IF NOT EXISTS idx_endpoint ON logs(endpoint);",
        "CREATE INDEX IF NOT EXISTS idx_ip ON logs(ip);"
    ]

    conn = create_connection(db_file)
    if conn is not None:
        create_table(conn, sql_create_logs_table)
        for index_sql in sql_create_indexes:
            create_table(conn, index_sql)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

def execute_query(conn, query, params=()):
    """Execute a query and return results"""
    try:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()
    except sqlite3.Error as e:
        print(e)
        return []

def insert_log(conn, log_data):
    """Insert a log entry into the logs table"""
    sql = ''' INSERT INTO logs(ip, timestamp, method, endpoint, status, size)
              VALUES(?,?,?,?,?,?) '''
    try:
        c = conn.cursor()
        c.execute(sql, log_data)
        conn.commit()
        return c.lastrowid
    except sqlite3.Error as e:
        print(e)
        return None
