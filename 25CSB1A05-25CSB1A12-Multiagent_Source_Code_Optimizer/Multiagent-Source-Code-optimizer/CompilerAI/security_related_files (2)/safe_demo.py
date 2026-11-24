import subprocess
import hashlib
import json

def run_command(user_param):
    subprocess.run(["ping", "-c", "1", user_param], shell=False)

def load_payload(raw_bytes):
    return json.loads(raw_bytes.decode())

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
