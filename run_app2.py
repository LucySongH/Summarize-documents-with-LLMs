import subprocess
import time
import sys
import os

def main():
    print("🚀 Starting On-Prem Summarizer System...")
    print("="*50)

    # Ensure paths are resolved relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # run backend.
    print("🔹 Starting Backend (FastAPI)...")
    backend_path = os.path.join(script_dir, "backend.py")
    backend_process = subprocess.Popen(
        [sys.executable, backend_path],
        env=os.environ.copy()
    )
    
    # wait a few seconds to ensure the backend is up before starting the frontend
    time.sleep(3) 

    # run frontend.
    print("🔹 Starting Frontend (Streamlit)...")
    try:
        frontend_path = os.path.join(script_dir, "frontend.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", frontend_path])
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
        backend_process.terminate()

if __name__ == "__main__":
    main()
