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

  You need TWO things installed:

  1. Python (3.10 or newer)
     → Download: https://www.python.org/downloads/
     → IMPORTANT: Check "Add Python to PATH" during installation

  2. Ollama (AI model server)
     → Download: https://ollama.com/download


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FIRST TIME SETUP  (run once only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Windows
  ───────
  Double-click  install.bat

  Mac / Linux
  ───────────
  Open Terminal in this folder and run:

    chmod +x install.sh start.sh
    ./install.sh

  ⚠️  First time setup downloads 3 AI models (~6 GB total).
      This requires an internet connection just this one time.
      After that, everything runs completely offline.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO START  (every time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Windows        Double-click  start.bat
  Mac / Linux    Run  ./start.sh  in Terminal

  Then open your browser and go to:

    http://localhost:8501


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

  ⏱️  Expected processing times:
      First run   : 3–5 min (model loading + inference)
      After that  : 1–3 min (model already in memory)
      Short docs  : 30–60 seconds


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO STOP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Press Ctrl+C in the terminal window where start.bat is running.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Problem                    Solution
  ─────────────────────────────────────────────────────────────
  'python' not recognised     Reinstall Python and check
                              "Add Python to PATH"

  'ollama' not recognised     Restart your computer after
                              installing Ollama

  App won't open              Wait 10 seconds after start.bat
                              finishes, then refresh the browser

  Models not downloading      Check your internet connection
                              (only needed for first run)

  No response after upload    First summarization takes 3–5 min.
                              Wait and do not close the browser.

  "Ollama timed out" error    Try a shorter document or switch
                              to phi3 or gemma2:2b model

  Backend not running         Run start.bat again


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DocSum/
  ├── install.bat        ← Windows: run ONCE to set up
  ├── install.sh         ← Mac/Linux: run ONCE to set up
  ├── start.bat          ← Windows: run to start app
  ├── start.sh           ← Mac/Linux: run to start app
  ├── README.txt         ← This file
  ├── backend.py         ← API server
  ├── frontend.py        ← Web interface
  ├── job_queue.py       ← Job queue
  ├── evaluation.py      ← Quality metrics
  ├── run_app.py         ← App launcher
  └── requirements.txt   ← Python packages


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRIVACY & SECURITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅  All processing happens on your computer
  ✅  No document data is sent to external servers
  ✅  No API keys required
  ✅  Works fully offline after first setup
  ✅  AI models are stored locally by Ollama


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DocSum  |  AUT R&D Project  |  Client: Pingar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
