import os
import shutil
import time
import requests
import subprocess
from .util import run_command

def start_ngrok(port, logger):
    """
    Starts ngrok on the given port and returns the public URL.
    """
    if not shutil.which("ngrok"):
        logger.error("ngrok not found in PATH.")
        return None

    logger.step(f"Starting ngrok on port {port}...")
    
    # We need to run ngrok in background
    cmd = ["ngrok", "http", str(port)]
    
    # In a real CLI tool, we have to be careful not to zombie this process.
    # The main process will handle cleanup via try/finally or signal handlers.
    proc = subprocess.Popen(
        cmd, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    
    # Wait for startup
    time.sleep(2)
    
    # Query API
    try:
        res = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        data = res.json()
        public_url = data['tunnels'][0]['public_url']
        logger.success(f"Ngrok Tunnel active: {public_url}")
        return proc, public_url
    except Exception as e:
        logger.error(f"Failed to get ngrok URL: {e}")
        # Try to read stdout if we captured it? No we didn't.
        # Just return proc so we can kill it later.
        return proc, None
