import os
import pickle
import hashlib
import requests

def run_command(user_param):
    # Command injection (CWE-78)
    os.system("ping -c 1 " + user_param)

def load_payload(raw_bytes):
    # Insecure Deserialization (CWE-502)
    return pickle.loads(raw_bytes)

def hash_password(password):
    # Insecure MD5 Hash (CWE-328)
    return hashlib.md5(password.encode()).hexdigest()

def execute_dynamic(user_code):
    # Dynamic Code Execution (CWE-94)
    return eval(user_code)

def fetch_data(api_url):
    # Disabled TLS Verification (CWE-295)
    return requests.get(api_url, verify=False)
