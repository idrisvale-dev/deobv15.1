"""Offline: what does fallthrough return for GetControlPoint on empty path?"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local p = Instance.new('Path2D')
local ok, r = pcall(function() return p:GetControlPoint(0) end)
print("ok=" .. tostring(ok))
if ok then
  print("t=" .. typeof(r) .. " type=" .. type(r))
  print("tostr=" .. tostring(r):sub(1, 60))
  local ok2, v = pcall(function() return r.Position end)
  print("pos-ok=" .. tostring(ok2) .. " pos=" .. tostring(v):sub(1, 60))
end
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "gcpfall.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:1200])
