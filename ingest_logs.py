import sqlite3
import csv
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import initialize_database


def ingest_tsv_logs(data_dir='data', db_file='data/logs.db', limit=1000000):
    """
    Ingest NASA logs from TSV format (Kaggle dataset).
    Expects: log_1.tsv, log_2.tsv with columns: ip, timestamp, request, status, size
    """
    initialize_database(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    batch = []
    batch_size = 10000
    processed = 0

    insert_sql = "INSERT INTO logs (ip, timestamp, method, endpoint, status, size) VALUES (?,?,?,?,?,?)"

    # Find all TSV files
    tsv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.tsv')])
    
    if not tsv_files:
        print(f"❌ No .tsv files found in {data_dir}")
        return

    print(f"🚀 Found {len(tsv_files)} TSV file(s): {tsv_files}")
    print(f"🚀 Starting ingestion (limit={limit:,})...\n")

    for tsv_file in tsv_files:
        file_path = os.path.join(data_dir, tsv_file)
        print(f"📄 Processing: {tsv_file}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as fh:
                reader = csv.DictReader(fh, delimiter='\t')
                
                if reader.fieldnames is None:
                    print(f"⚠️  Skipping {tsv_file}: No headers found\n")
                    continue
                
                print(f"   Columns: {list(reader.fieldnames)}\n")

                for row in reader:
                    try:
                        # Kaggle format: 'host', 'logname', 'time', 'method', 'url', 'response', 'bytes', 'referer', 'useragent'
                        ip = row.get('host', '').strip()
                        timestamp = row.get('time', '').strip()
                        method = row.get('method', 'GET').strip()
                        endpoint = row.get('url', '/').strip()
                        status_str = row.get('response', '200')
                        size_str = row.get('bytes', '0')

                        # Convert types
                        try:
                            status = int(status_str)
                        except:
                            status = 200

                        try:
                            size = int(size_str) if size_str and size_str != '-' else 0
                        except:
                            size = 0

                        # Only insert if we have required fields
                        if ip and timestamp:
                            batch.append((ip, timestamp, method, endpoint, status, size))
                            processed += 1

                            if len(batch) >= batch_size:
                                cursor.executemany(insert_sql, batch)
                                conn.commit()
                                batch = []
                                print(f"   ✓ {processed:,} logs inserted...")

                            if processed >= limit:
                                print()
                                break

                    except Exception as e:
                        # Skip malformed rows silently
                        continue

                if processed >= limit:
                    break

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}\n")
            continue

    # Final batch
    if batch:
        cursor.executemany(insert_sql, batch)
        conn.commit()

    conn.close()

    print(f"✅ Ingestion complete: Processed {processed:,} logs")


if __name__ == '__main__':
    ingest_tsv_logs()

