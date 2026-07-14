#!/usr/bin/env python3
"""Check catalog storage configuration."""

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

print("Checking catalog and schema storage...\n")

# Check catalog properties
cursor.execute("DESCRIBE CATALOG EXTENDED signaltogrowth")
rows = cursor.fetchall()
print("=== CATALOG: signaltogrowth ===")
for row in rows:
    if row[0] in ['Location', 'Catalog Type', 'Storage Type', 'Owner']:
        print(f"{row[0]}: {row[1]}")
print()

# Check schema properties
cursor.execute("DESCRIBE SCHEMA EXTENDED signaltogrowth.bronze")
rows = cursor.fetchall()
print("=== SCHEMA: signaltogrowth.bronze ===")
for row in rows:
    if row[0] in ['Location', 'Managed Location', 'Owner']:
        print(f"{row[0]}: {row[1]}")
print()

cursor.close()
connection.close()
