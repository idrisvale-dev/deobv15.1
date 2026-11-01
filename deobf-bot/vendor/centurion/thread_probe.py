"""Offline check: spawned-thread status semantics under envlog."""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local th = task.spawn(function() end)
print("SPAWN-TTYPE " .. typeof(th))
local ok, st = pcall(function() return coroutine.status(th) end)
print("STATUS ok=" .. tostring(ok) .. " v=" .. tostring(st))
local th2 = task.defer(function() end)
local ok2, st2 = pcall(function() return coroutine.status(th2) end)
print("DEFER-STATUS ok=" .. tostring(ok2) .. " v=" .. tostring(st2))
print("EQ-THREAD " .. tostring(th == th))
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "thread_probe.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:1500])
print("=== raw tail ===")
print(harness.LAST_RAW[0][-1200:])
