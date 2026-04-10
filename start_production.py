# start_production.py
import os
import sys
import logging
from waitress import serve

# Add the current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web.app import app

if __name__ == "__main__":
    # Get local IP for convenience
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    port = 5000
    
    print("="*60)
    print("        🛡️ SMART GUARDIAN - PRODUCTION MODE 🛡️")
    print("="*60)
    print(f" [+] Server is running on: http://localhost:{port}")
    print(f" [+] Network access:       http://{local_ip}:{port}")
    print(" [+] Press Ctrl+C to stop the server.")
    print("="*60)
    
    # Run the production server
    serve(app, host='0.0.0.0', port=port, threads=8)
