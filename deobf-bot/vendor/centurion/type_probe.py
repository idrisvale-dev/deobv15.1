"""Offline check: type() of proxies under envlog (vs live: userdata/thread)."""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
print("TYPE game " .. type(game))
local s = game:GetService("TextService")
print("TYPE svc " .. type(s))
local th = task.spawn(function() end)
print("TYPE thread " .. type(th))
print("TYPE vec2 " .. type(Vector2.new(1, 2)))
print("TYPE enum " .. type(Enum.Font.SourceSans))
print("TYPE nilv " .. type(nil))
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "type_probe.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:1500])
