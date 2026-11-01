import os, shutil
from engines.base import popen_run

VENDOR = os.path.join(os.path.dirname(__file__), "..", "vendor", "ib2bot")
EXE    = os.path.join(VENDOR, "ib2deobf", "LuaAnalysis.Ironbrew2.exe")
DOTNET = shutil.which("dotnet")

def run(input_path, output_path, timeout, cancel_event=None, user_id=0):
    if not os.path.exists(EXE):
        raise RuntimeError("ironbrew2 vendor files not found. run python setup.py")
    if not DOTNET:
        raise RuntimeError("dotnet runtime not found. install .NET 8 to use ironbrew2.")
    popen_run([DOTNET, EXE, input_path, output_path], VENDOR, timeout, cancel_event, user_id)
