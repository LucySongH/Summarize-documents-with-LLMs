# Deployment Method Change: Docker → Local Execution

## Summary

The deployment method for DocSum has been changed from **Docker containerisation** to **local execution**. This document explains why this change was made and how the new approach works.

---

## Why Docker Was Chosen Initially

Docker was originally selected so that end users would only need to install Docker Desktop, no Python or Ollama installation required. However, testing revealed critical performance and stability issues that made Docker unsuitable for this project.

---

## Problems Found During Docker Testing

| # | Problem | Detail |
|---|---------|--------|
| 1 | **Extremely slow** | Docker's virtualisation layer severely limits CPU performance. phi3 took **944 seconds (15+ min)** on a single document. The same document ran in ~120 seconds locally. |
| 2 | **Memory constraints** | Docker Desktop allocated only 7.43 GB RAM. Running 3 models simultaneously required ~6 GB for models alone, causing swap and extreme slowdowns. |
| 3 | **Ollama container failures** | The Ollama container repeatedly failed health checks because it took too long to start inside Docker, preventing the app from launching. |
| 4 | **Port conflicts** | If Ollama was already installed on the user's PC, it occupied port 11434 and conflicted with the Docker Ollama container. |
| 5 | **Complex troubleshooting** | Docker added an extra layer of complexity requiring container logs, Docker networking, and WSL2 memory configuration, unfamiliar to non-technical users. |

---

## Performance Comparison

| Scenario | Docker | Local Execution |
|----------|--------|-----------------|
| llama3.2 (single doc) | 294s (4.9 min) | ~113s (1.9 min) |
| phi3 (single doc) | 944s (15.7 min) | ~120s (2 min) |
| Model Matrix (3 models) | 30+ minutes | 6–10 minutes |
| Memory usage | 5.44 GB / 7.43 GB (73%) | Uses all available RAM |

---

## New Local Execution Approach

Users install two lightweight tools (Python and Ollama) once, then use two scripts:

**First time only:**
```
install.bat   (Windows)
./install.sh  (Mac/Linux)
```
→ Installs Python packages and downloads all 3 AI models (~6 GB)

**Every time:**
```
start.bat     (Windows)
./start.sh    (Mac/Linux)
```
→ Starts Ollama + launches the app at http://localhost:8501

---

## Impact on Files

| File | Status | Change |
|------|--------|--------|
| `Dockerfile` | Removed | No longer needed |
| `docker-compose.yml` | Removed | No longer needed |
| `stop.bat` / `stop.sh` | Removed | Use Ctrl+C to stop |
| `start.bat` | Replaced | New local execution version |
| `start.sh` | Replaced | New local execution version |
| `install.bat` | New | One-time setup for Windows |
| `install.sh` | New | One-time setup for Mac/Linux |
| `README.txt` | Updated | New installation instructions |
| `backend.py` | Unchanged | No changes required |
| `frontend.py` | Unchanged | No changes required |

---

## Privacy & Security

The core privacy guarantees remain unchanged:

- All processing happens locally on the user's machine
- No document data is transmitted to external servers
- No API keys required
- Works fully offline after initial model download

---

*DocSum | AUT R&D Project | Client: Pingar | 2026*
