"""Check environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"SUPABASE_URL exists: {url is not None}")
print(f"SUPABASE_URL value (first 30 chars): {url[:30] if url else 'NOT SET'}")
print(f"SUPABASE_URL value (last 20 chars): {url[-20:] if url else 'NOT SET'}")
print(f"SUPABASE_KEY exists: {key is not None}")
print(f"SUPABASE_KEY value (first 20 chars): {key[:20] if key else 'NOT SET'}")

if url:
    print(f"\nURL breakdown:")
    print(f"  Starts with 'https://': {url.startswith('https://')}")
    print(f"  Contains '.supabase.co': {'.supabase.co' in url}")
    print(f"  Length: {len(url)}")
