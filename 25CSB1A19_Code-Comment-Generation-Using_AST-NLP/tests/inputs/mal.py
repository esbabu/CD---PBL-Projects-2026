
import os
import subprocess
import base64
import socket
import platform

# Suspicious system information collection
def collect_system_info():
    username = os.getenv("USERNAME")
    hostname = socket.gethostname()
    system = platform.system()
    return username, hostname, system

# Encoded command-like data
encoded_command = base64.b64encode(
    b"echo Security_Test"
).decode()

# Suspicious process execution pattern (not executed)
def suspicious_execution():
    command = base64.b64decode(encoded_command).decode()
    print("Decoded test command:", command)
    print("Subprocess execution pattern detected:", subprocess.__name__)

# Network connection pattern (not executed)
def network_activity():
    target = "127.0.0.1"
    port = 4444
    print(f"Simulated connection target: {target}:{port}")

if __name__ == "__main__":
    print("Security testing sample")
    print("System information:", collect_system_info())
    suspicious_execution()
    network_activity()
