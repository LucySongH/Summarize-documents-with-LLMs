
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           DocSum — On-Premise Document Summarizer            ║
║                                                              ║
║     AI-powered summarization that runs fully on your PC.     ║
║     No internet required. Your documents stay private.       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BEFORE YOU START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  You only need ONE thing installed:

    Docker Desktop
    → Download: https://www.docker.com/products/docker-desktop/

  That's it. No Python. No Ollama. No other installs.

  Minimum requirements:
    • 8 GB RAM  (16 GB recommended)
    • 10 GB free disk space  (for AI models)
    • Windows 10/11  or  macOS


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Windows
  ───────
  1. Make sure Docker Desktop is running
  2. Double-click  start.bat
  3. Wait for setup to finish (first run takes 5–15 minutes)
  4. Open your browser and go to:

       http://localhost:8501

  Mac / Linux
  ───────────
  1. Make sure Docker Desktop is running
  2. Open Terminal in this folder and run:

       chmod +x start.sh
       ./start.sh

  3. Wait for setup to finish (first run takes 5–15 minutes)
  4. Open your browser and go to:

       http://localhost:8501


  ⚠️  First run only:
      The app will automatically download 3 AI models (~5 GB total).
      This requires an internet connection just this one time.
      After that, everything runs completely offline.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO USE THE APP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  The app has 3 tabs:

  📄 Summarize
  ─────────────
  → Upload one or more documents
  → Select a summary type:
       • Comprehensive  — full detailed summary
       • Executive      — short, decision-focused summary
       • Bullet Points  — key points in list format
  → Choose a model (llama3.2 recommended)
  → Click "Run All" and wait for results
  → Download the summary as a text file

  📊 Model Matrix
  ────────────────
  → Upload one document
  → Select which models and summary types to compare
  → Click "Run Matrix Experiment"
  → See all results side by side
  → Export results to Excel (.xlsx)

  📜 History
  ───────────
  → View all summaries generated in this session
  → Expand any entry to read the full summary


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SUPPORTED FILE FORMATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅  PDF          (.pdf)
  ✅  Word         (.docx)
  ✅  PowerPoint   (.pptx)
  ✅  Excel        (.xlsx, .xls)
  ✅  CSV          (.csv)
  ✅  Text         (.txt)
  ✅  Markdown     (.md)
  ✅  HTML         (.html)
  ✅  Python       (.py)

  Note: Scanned PDFs (image-only) are not supported.
        Only text-layer PDFs can be processed.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AI MODELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Model          Size    Best for
  ─────────────────────────────────────────────────────────────
  llama3.2       ~2 GB   Best overall quality (recommended)
  phi3           ~2.3 GB Fast, good for most documents
  gemma2:2b      ~1.7 GB Fastest, best for short documents


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO STOP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Windows        Double-click  stop.bat
  Mac / Linux    Run  ./stop.sh  in Terminal


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Problem                    Solution
  ─────────────────────────────────────────────────────────────
  Docker not running          Open Docker Desktop, wait for it
                              to fully start, then try again

  App won't open              Wait 30 seconds after start.bat
                              finishes, then refresh the browser

  Port already in use         Run: docker compose down
                              Then try start.bat again

  Models not downloading      Check your internet connection
                              (only needed for first run)

  Out of memory error         Close other applications
                              In Docker Desktop → Settings →
                              Resources → increase Memory to 8GB+

  Summarization taking long   This is normal on CPU - each
                              document takes 1-5 minutes
                              Use phi3 or gemma2 for faster results

  Backend not running         Restart the app with start.bat

  "Ollama timed out" error    The document is too large or complex.
                              Try one of the following:
                                • Use a shorter document
                                • Switch to phi3 or gemma2:2b
                                • Split the document into sections

  No response after upload    This is normal - the AI model is
                              loading for the first time.
                              First summarization takes 3–5 min.
                              Wait and do not close the browser.
                              Subsequent runs will be faster.



━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DocSum/
  ├── start.bat            ← Windows: run to start
  ├── start.sh             ← Mac/Linux: run to start
  ├── stop.bat             ← Windows: run to stop
  ├── stop.sh              ← Mac/Linux: run to stop
  ├── README.txt           ← This file
  ├── docker-compose.yml   ← Docker configuration
  ├── Dockerfile           ← App build instructions
  ├── backend.py           ← API server
  ├── frontend.py          ← Web interface
  ├── job_queue.py         ← Job queue
  ├── evaluation.py        ← Quality metrics
  ├── run_app.py           ← App launcher
  ├── requirements.txt     ← Python packages
  └── ollama_data/         ← AI models (auto-created on first run)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRIVACY & SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅  All processing happens on your computer
  ✅  No document data is sent to external servers
  ✅  No API keys required
  ✅  Works fully offline after first setup
  ✅  AI models are stored locally in the ollama_data/ folder


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DocSum  |  AUT R&D Project  |  Client: Pingar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
