from flask import Flask, jsonify, request
import threading
import subprocess
import os

app = Flask(__name__)

@app.route("/run")
def run_agent():
    # Roda o agente como subprocesso
    try:
        result = subprocess.run(
            ["python", "moda_agent/main.py"],
            capture_output=True,
            text=True,
            timeout=120,  # segundos
            cwd="/render/project"
        )
        return jsonify({
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout"}), 504

@app.route("/")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(port=10000)  # Render usa portas altas (10000+)
