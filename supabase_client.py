import os
import httpx
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Prevent [WinError 10054] / httpx.ReadError on Windows:
# Replace the default HTTP/2 persistent session with a resilient HTTP/1.1 transport
# that automatically retries and recycles idle connections before remote drop.
try:
    transport = httpx.HTTPTransport(
        retries=3,
        verify=True,
        http2=False,  # HTTP/1.1 prevents Windows socket connection reset drops
        limits=httpx.Limits(max_keepalive_connections=10, keepalive_expiry=5.0)
    )
    resilient_client = httpx.Client(
        base_url=f"{SUPABASE_URL}/rest/v1",
        headers=supabase.postgrest.session.headers,
        transport=transport,
        follow_redirects=True,
        timeout=httpx.Timeout(20.0, connect=10.0)
    )
    supabase.postgrest.session = resilient_client
except Exception:
    pass

print("Supabase connection created successfully with resilient transport!")