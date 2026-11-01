"""6th typeof targets offline."""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local L = game:GetService("Lighting")
print("OA t=" .. typeof(L.OutdoorAmbient))
local w = game:GetService("Workspace")
print("NAP t=" .. typeof(w:GetNumAwakeParts()))
print("FPS t=" .. typeof(w:GetRealPhysicsFPS()))
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "t6.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:800])
