import webview
import threading
import time
import os
import sys
from web.app import app
from init_db import init_db

def start_flask():
    """Run the Flask server in a background thread."""
    init_db()
    # We use a standard flask run here for the desktop wrapper
    app.run(host='127.0.0.1', port=5000, threaded=True, use_reloader=False)

if __name__ == "__main__":
    # 1. Start Flask in the background
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()

    # 2. Wait a moment for the server to warm up
    time.sleep(2)

    # 3. Create the Desktop Window
    print("Launching Smart Guardian Desktop...")
    webview.create_window(
        'Smart Guardian Security System', 
        'http://127.0.0.1:5000',
        width=1280,
        height=800,
        resizable=True,
        confirm_close=True
    )
    
    # 4. Start the GUI loop
    webview.start()
