import os, shutil
from engines.base import popen_run

VENDOR = os.path.join(os.path.dirname(__file__), "..", "vendor", "ironveil", "deobfuscator")
ENTRY  = os.path.join(VENDOR, "index.js")
NODE   = shutil.which("node") or "node"

def run(input_path, output_path, timeout, cancel_event=None, user_id=0):
    if not os.path.exists(ENTRY):
        raise RuntimeError("ironveil vendor files not found. run python setup.py")
    popen_run([NODE, ENTRY, input_path, output_path], VENDOR, timeout, cancel_event, user_id)
