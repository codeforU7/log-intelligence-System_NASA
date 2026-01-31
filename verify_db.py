import sqlite3

conn = sqlite3.connect('data/logs.db')
cursor = conn.cursor()

# Columns
cursor.execute("PRAGMA table_info(logs);")
cols = [row[1] for row in cursor.fetchall()]
print("✅ COLUMNS:", cols)

# Indexes
cursor.execute("PRAGMA index_list(logs);")
idxs = [row[1] for row in cursor.fetchall()]
print("✅ INDEXES:", idxs)

# Count
cursor.execute("SELECT COUNT(*) FROM logs")
cnt = cursor.fetchone()[0]
print(f"✅ TOTAL LOGS: {cnt:,}")

# Sample row
cursor.execute("SELECT * FROM logs LIMIT 1")
sample = cursor.fetchone()
print(f"✅ SAMPLE ROW: ip={sample[1]}, timestamp={sample[2]}, method={sample[3]}, endpoint={sample[4]}, status={sample[5]}, size={sample[6]}")

conn.close()
