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
    process.stdout.close()
    process.wait()

def start_services():
    print("🚀 Initializing KSP Crime Intelligence Platform...")

    print("📊 [1/4] Running ML Pipeline to generate assets...")
    subprocess.run([sys.executable, "main.py"], check=True)

    print("🗄️ [2/4] Database structure verified.")
    # subprocess.run([sys.executable, "backend/database/load_data.py"], check=True)

    print("🌐 [3/4] Starting KSP API Gateway...")

    # 1. Start the main API Gateway (which now includes backend routes and network analysis)
    # We will use uvicorn to run app:app
    api_thread = threading.Thread(
        target=run_command,
        args=("uvicorn app:app --host 0.0.0.0 --port 8000", ".", "API"),
        daemon=True
    )
    api_thread.start()
    
    # 2. Wait for API to initialize
    time.sleep(3)

    # 3. Start the Streamlit Frontend Application
    frontend_thread = threading.Thread(
        target=run_command,
        args=("streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0", ".", "Streamlit"),
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
