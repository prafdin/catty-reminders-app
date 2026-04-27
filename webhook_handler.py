import os
import subprocess
import threading
import logging
from flask import Flask, request, jsonify

REPO_DIR = "/home/ubuntu/catty-reminders-app"
ENV_FILE = "/etc/catty-app-env"
SERVICE = "catty"

app = Flask(__name__)
logging.basicConfig(filename="/home/ubuntu/deploy.log", level=logging.INFO)

def deploy(sha):
    try:
        subprocess.run(["git", "-C", REPO_DIR, "fetch", "--all"], check=True)
        subprocess.run(["git", "-C", REPO_DIR, "reset", "--hard", sha], check=True)
        with open(ENV_FILE, "w") as f:
            f.write(f"DEPLOY_REF={sha}\n")
        subprocess.run(["sudo", "systemctl", "restart", SERVICE], check=True)
        logging.info(f"Deployed {sha}")
    except Exception as e:
        logging.error(f"Deploy error: {e}")

@app.route('/', methods=['POST'])
def handle():
    if request.headers.get('X-GitHub-Event') == 'push':
        payload = request.get_json()
        sha = payload.get('after')
        if sha and sha != "0000000000000000000000000000000000000000":
            threading.Thread(target=deploy, args=(sha,)).start()
            return "Deploy started", 202
    return "Ignored", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
