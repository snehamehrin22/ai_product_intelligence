#!/usr/bin/env python3
"""Check table storage location."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from databricks import sql

load_dotenv()

connection = sql.connect(
    server_hostname=os.getenv("DATABRICKS_HOST").replace("https://", "").rstrip("/"),
    http_path=os.getenv("DATABRICKS_HTTP_PATH"),
    access_token=os.getenv("DATABRICKS_TOKEN")
)

cursor = connection.cursor()

print("Checking table storage...")
print()

# Check if tables exist
cursor.execute("SHOW TABLES IN signaltogrowth.bronze")
tables = cursor.fetchall()
print(f"Tables in signaltogrowth.bronze: {tables}")
print()

# Check table properties
for table_name in ['platform_events', 'agent_traces']:
    try:
        cursor.execute(f"DESCRIBE EXTENDED signaltogrowth.bronze.{table_name}")
        rows = cursor.fetchall()

        print(f"=== {table_name} ===")
        for row in rows:
            col_name = row[0]
            if col_name in ['Location', 'Type', 'Provider', 'Table Properties']:
                print(f"{col_name}: {row[1]}")
        print()
    except Exception as e:
        print(f"Error checking {table_name}: {e}")
        print()

cursor.close()
connection.close()
