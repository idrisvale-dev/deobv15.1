import os, shutil, threading
from engines.base import popen_run

VENDOR = os.path.join(os.path.dirname(__file__), "..", "vendor", "luraph_v15zip", "Deobfuscator", "deobf")
ENTRY  = os.path.join(VENDOR, "deob.py")
PYTHON = shutil.which("python3") or shutil.which("python") or "python3"

def run(input_path, output_path, timeout, cancel_event=None, user_id=0):
    if not os.path.exists(ENTRY):
        raise RuntimeError("luraph_v14 vendor files not found. run python setup.py")
    popen_run([PYTHON, ENTRY, input_path, "-o", output_path], VENDOR, timeout, cancel_event, user_id)
