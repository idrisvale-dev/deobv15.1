import os, shutil
from engines.base import popen_run

VENDOR = os.path.join(os.path.dirname(__file__), "..", "vendor", "77fuscator")
DOTNET = shutil.which("dotnet")

def _find_dll():
    for sub in ["bin/Debug/net8.0", "bin/Release/net8.0", ""]:
        c = os.path.join(VENDOR, sub, "deobfuscator.dll")
        if os.path.exists(c):
            return c
    return None

def run(input_path, output_path, timeout, cancel_event=None, user_id=0):
    dll = _find_dll()
    if not dll:
        raise RuntimeError("77fuscator vendor not compiled. run python setup.py then dotnet build inside vendor/77fuscator/")
    if not DOTNET:
        raise RuntimeError("dotnet runtime not found. install .NET 8 to use 77fuscator.")
    popen_run([DOTNET, dll, input_path, output_path], VENDOR, timeout, cancel_event, user_id)
