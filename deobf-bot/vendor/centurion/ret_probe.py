"""Offline: what does workspace.Retargeting resolve to under envlog?"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local ok, r = pcall(function() return workspace.Retargeting end)
print("RET ok=" .. tostring(ok))
if ok then
  print("RET typeof=" .. typeof(r))
  print("RET type=" .. type(r))
  local ok2, v = pcall(function() return tostring(r) end)
  print("RET tostring ok=" .. tostring(ok2) .. " v=" .. tostring(v):sub(1,60))
else
  print("RET err=" .. tostring(r):sub(1,120))
end
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "ret_probe.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:1200])
