"""SEC002 whose command uses a pipe: no argument list, so the agent falls back to shlex.quote."""
import subprocess

from flask import request


def grep_processes():
    name = request.args["name"]
    return subprocess.check_output("ps aux | grep " + name, shell=True)
