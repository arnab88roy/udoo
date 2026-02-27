import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    print("Testing pooler with psycopg2...")
    conn = psycopg2.connect("postgresql://postgres.rsuebckrxfpnfbwxvqqp:Dubaramatpuchna%40123@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres", connect_timeout=5)
    print("Success! Postgres Version:", conn.server_version)
    conn.close()
except Exception as e:
    print(f"Failed pooler connection: {type(e).__name__} - {e}")
