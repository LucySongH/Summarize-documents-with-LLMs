#!/usr/bin/env python3
"""
Document Summarizer - Simple App Runner
"""

import subprocess
import sys
import os
import socket
import time

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "localhost"

def main():
    print("🚀 Document Summarizer - Starting Up!")
    print("="*50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is ready")
    except ImportError:
        print("❌ Installing Streamlit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    local_ip = get_local_ip()
    port = 8501
    
    print("")
    print("📱 Your app will be available at:")
    print(f"   • http://localhost:{port} (for you)")
    print(f"   • http://{local_ip}:{port} (for same network)")
    print("")
    
    print("🌐 To share with teammates anywhere in the world:")
    print("   1. Keep this running")
    print("   2. Open a NEW terminal")
    print("   3. Run: ngrok http 8501")
    print("   4. Share the ngrok URL!")
    print("")
    
    print("📦 Installing ngrok automatically...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
        print("✅ ngrok installed!")
    except:
        print("❌ Couldn't install ngrok automatically")
        print("   Download from: https://ngrok.com/download")
    
    print("")
    print("🎯 Starting your app now...")
    print("🛑 Press Ctrl+C to stop")
    print("="*50)
    
    # Start Streamlit with custom config to avoid showing 0.0.0.0
    try:
        # Set environment variables to control what Streamlit displays
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
