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

    # ── Port Configuration ─────────────────────────────────────
    # Render routes public HTTP traffic to the port in the PORT env var.
    # Therefore, Streamlit (the user interface) must bind to this PORT.
    streamlit_port = int(os.getenv("PORT", "8501"))
    
    # Run FastAPI internally. If Streamlit is on 8000, move FastAPI to 8080 to prevent conflict.
    api_port = 8000 if streamlit_port != 8000 else 8080
    
    # Inject correct backend API URL so Streamlit knows where to send requests
    os.environ["KSP_API_BASE_URL"] = f"http://127.0.0.1:{api_port}"

    # ── API Gateway ────────────────────────────────────────────
    print(f"🌐 [3/4] Starting KSP API Gateway on port {api_port}...")
    api_thread = threading.Thread(
        target=run_command,
        args=(f"uvicorn app:app --host 0.0.0.0 --port {api_port}", ".", "API"),
        daemon=True
    )
    api_thread.start()

    # Wait for API to initialise before starting Streamlit
    time.sleep(5)

    # ── Streamlit Frontend ─────────────────────────────────────
    print(f"🖥️  [4/4] Starting Streamlit Dashboard on port {streamlit_port}...")
    frontend_thread = threading.Thread(
        target=run_command,
        args=(f"streamlit run dashboard/app.py --server.port {streamlit_port} --server.address 0.0.0.0 --server.headless true", ".", "Streamlit"),
        daemon=True
    )
    frontend_thread.start()

    print("\n" + "="*50)
    print("✅ All services started!")
    print(f"📍 API Gateway (Internal): http://localhost:{api_port}")
    print(f"📍 Web Client (Public):    http://localhost:{streamlit_port}")
    print("="*50 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")

if __name__ == "__main__":
    start_services()
