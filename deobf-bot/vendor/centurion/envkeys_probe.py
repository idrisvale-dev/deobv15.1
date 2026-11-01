"""Offline: what does the script's getfenv() contain under envlog?"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local e = getfenv()
local keys = {}
for k in pairs(e) do keys[#keys + 1] = tostring(k) end
table.sort(keys)
print("ENVKEYS " .. table.concat(keys, ","))
for _, k in ipairs({"game", "task", "buffer", "gethui", "hookfunction", "getgc", "getgenv", "script", "workspace", "math", "string", "table", "pcall", "select", "unpack", "Vector2", "Enum", "Instance", "typeof", "loadstring"}) do
  local v = e[k]
  print("ENVK " .. k .. " type=" .. type(v))
end
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "envkeys.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:4000])
