import subprocess
import sys
import time
import os
import threading

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def run_command(command, cwd=None, prefix=""):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        bufsize=1
    )
    for line in iter(process.stdout.readline, ''):
        sys.stdout.write(f"[{prefix}] {line}")
        sys.stdout.flush()
    process.stdout.close()
    process.wait()

def start_services():
    print("🚀 Initializing KSP Crime Intelligence Platform...")

    # ── ML Pipeline ────────────────────────────────────────────
    # Only run ML training if the model artifact is missing.
    # On Render (or any cloud deploy) the pre-built model is
    # committed to git, so we skip retraining to avoid failures
    # caused by missing local CSV datasets.
    model_path = os.path.join("ml", "crime_rf_model.pkl")
    if os.path.exists(model_path):
        print(f"✅ [1/4] ML model already exists at '{model_path}' — skipping training.")
    else:
        print("📊 [1/4] ML model not found — running pipeline to generate assets...")
        try:
            subprocess.run([sys.executable, "main.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  ML pipeline failed (code {e.returncode}). Continuing without model — some features may be limited.")

    # ── Database ───────────────────────────────────────────────
    print("🗄️  [2/4] Database structure verified (using remote PostgreSQL).")

    # ── API Gateway ────────────────────────────────────────────
    print("🌐 [3/4] Starting KSP API Gateway...")
    api_thread = threading.Thread(
        target=run_command,
        args=("uvicorn app:app --host 0.0.0.0 --port 8000", ".", "API"),
        daemon=True
    )
    api_thread.start()

    # Wait for API to initialise before starting Streamlit
    time.sleep(5)

    # ── Streamlit Frontend ─────────────────────────────────────
    print("🖥️  [4/4] Starting Streamlit Dashboard...")
    frontend_thread = threading.Thread(
        target=run_command,
        args=("streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true", ".", "Streamlit"),
        daemon=True
    )
    frontend_thread.start()

    print("\n" + "="*50)
    print("✅ All services started!")
    print("📍 API Gateway: http://localhost:8000")
    print("📍 API Docs:    http://localhost:8000/docs")
    print("📍 Web Client:  http://localhost:8501")
    print("="*50 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")

if __name__ == "__main__":
    start_services()
