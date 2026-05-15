"""
run_app.py — One-command launcher.
Starts FastAPI backend (8000) + Streamlit frontend (8501).
"""

import subprocess, time, sys, os

def main():
    print("🚀 Starting On-Prem Summarizer System...")
    print("=" * 50)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("🔹 Starting Backend (FastAPI on port 8000)...")
    backend_process = subprocess.Popen(
        [sys.executable, os.path.join(script_dir, "backend.py")],
        env=os.environ.copy()
    )
    time.sleep(3)

    print("🔹 Starting Frontend (Streamlit on port 8501)...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            os.path.join(script_dir, "frontend.py"),
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
            "--server.maxUploadSize", "200",
            "--server.scriptHealthCheckEnabled", "false",
        ])
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        backend_process.terminate()
        print("👋 Goodbye!")

    print()
    print("=" * 50)
    print("✅ App running at → http://localhost:8501")
    print("🔧 API Docs       → http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    main()
