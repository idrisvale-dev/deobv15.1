import os, shutil, threading
from engines.base import popen_run

VENDOR = os.path.join(os.path.dirname(__file__), "..", "vendor", "luraph_v151")
ENTRY  = os.path.join(VENDOR, "deob.js")
NODE   = shutil.which("node") or "node"
PYTHON = shutil.which("python3") or shutil.which("python") or "python3"

def run(input_path, output_path, timeout, cancel_event=None, user_id=0):
    if not os.path.exists(ENTRY):
        raise RuntimeError("luraph_v151 vendor files not found. run python setup.py")
    env = os.environ.copy()
    env["PYTHON_BIN"] = PYTHON
    popen_run([NODE, ENTRY, input_path, "-o", output_path], VENDOR, timeout, cancel_event, user_id, env)
