"""Offline: does pairs()/# order differ between their patched luau and stock?"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

THEIRS = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
MINE = r"C:\Users\goldl\AppData\Local\Temp\opencode\luau\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local t = {}
local keys = {"Alpha","Beta","Gamma","Delta","Epsilon","Zeta","Eta","Theta","Code","Fire","Pity","Boss","Mob","Fish","Quest","Island","Bounty","Skill","Prestige","Dungeon"}
for _, k in ipairs(keys) do t[k] = true end
local o = {}
for k in pairs(t) do o[#o + 1] = k end
print("PAIRS " .. table.concat(o, ","))
local h = {a = 1}
for i = 1, 10 do h["k" .. i] = i end
h["a"] = nil
local o2 = {}
for k in pairs(h) do o2[#o2 + 1] = k end
print("HOLEY " .. table.concat(o2, ",") .. " len=" .. #h)
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
for tag, exe in (("theirs", THEIRS), ("mine", MINE)):
    hpath = os.path.join(OUT_DIR, "order_probe_%s.harness.luau" % tag)
    body, err = harness.run_once(exe, SNIPPET, cfg, hpath, 60, True)
    print("===== %s =====" % tag)
    print((body or "")[:900])
    print("--- raw tail ---")
    print(harness.LAST_RAW[0][-700:])
