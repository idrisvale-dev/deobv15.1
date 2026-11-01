import os, shutil
from engines.base import popen_run

VENDOR = os.path.join(os.path.dirname(__file__), "..", "vendor", "centurion")
ENTRY  = os.path.join(VENDOR, "centurion.py")
PYTHON = shutil.which("python3") or shutil.which("python") or "python3"

def run(input_path, output_path, timeout, cancel_event=None, user_id=0):
    if not os.path.exists(ENTRY):
        raise RuntimeError("centurion vendor files not found. run python setup.py")
    popen_run([PYTHON, ENTRY, input_path, "-o", output_path], VENDOR, timeout, cancel_event, user_id)
