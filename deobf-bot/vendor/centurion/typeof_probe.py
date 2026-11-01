"""Offline check: what does typeof(Instance.new(...)) return under envlog?"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local c = Instance.new("Camera")
local t1 = typeof(c)
local g = game:GetService("TextService")
local t2 = typeof(g)
local e = Enum.Font.SourceSans
local t3 = typeof(e)
local v = Vector2.new(100, 100)
local t4 = typeof(v)
print("TYPEOF-CAMERA " .. t1)
print("TYPEOF-SERVICE " .. t2)
print("TYPEOF-ENUM " .. t3)
print("TYPEOF-VEC2 " .. t4)
print("EQ-ENUM " .. tostring(e == Enum.Font.SourceSans))
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "typeof_probe.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:2000])
print("=== raw tail ===")
print(harness.LAST_RAW[0][-1500:])
