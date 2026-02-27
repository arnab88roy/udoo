import asyncio
import asyncpg
import urllib.parse

async def test_conn():
    try:
        conn = await asyncpg.connect(
            user="postgres.rsuebckrxfpnfbwxvqqp",
            password="Dubaramatpuchna@123",
            database="postgres",
            host="aws-0-ap-southeast-2.pooler.supabase.com",
            port=6543,
            timeout=10
        )
        print("Success AP-SE-2 6543! Version:", await conn.fetchval('SELECT version()'))
        await conn.close()
    except Exception as e:
        print(f"Failed AP-SE-2 6543: {type(e).__name__} - {e}")
        
    try:
        conn = await asyncpg.connect(
            user="postgres.rsuebckrxfpnfbwxvqqp",
            password="Dubaramatpuchna@123",
            database="postgres",
            host="aws-0-ap-southeast-1.pooler.supabase.com",
            port=6543,
            timeout=10
        )
        print("Success AP-SE-1 6543! Version:", await conn.fetchval('SELECT version()'))
        await conn.close()
    except Exception as e:
        print(f"Failed AP-SE-1 6543: {type(e).__name__} - {e}")

asyncio.run(test_conn())
