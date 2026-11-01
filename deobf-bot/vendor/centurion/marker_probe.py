"""Offline: does the P2D ERROR marker fire for GetControlPoint({})?"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

harness.P2D_CACHE["GetControlPoint|table"] = "ERROR:Unable to cast Array to int"
SNIPPET = """
local p = Instance.new('Path2D')
local ok, r = pcall(function() return p:GetControlPoint({}) end)
print("MARKER-FIRE ok=" .. tostring(ok) .. " r=" .. tostring(r):sub(1, 80))
"""
cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "marker_probe.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:900])
