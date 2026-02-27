import socket

def test_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()
    return "Open" if result == 0 else f"Closed/Filtered (code: {result})"

print("Direct DB (5432):", test_port('49.44.79.236', 5432))
print("Pooler AP-SE-1 (6543):", test_port('aws-0-ap-southeast-1.pooler.supabase.com', 6543))
print("Pooler AP-SE-2 (6543):", test_port('aws-0-ap-southeast-2.pooler.supabase.com', 6543))
