"""Offline: enum-item values + AdUnitStatus.Active behavior under envlog."""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
sys.path.insert(0, LURAPH_DEOBF)
import harness

LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

SNIPPET = """
local function t(label, f)
  local ok, r = pcall(f)
  if ok then
    local tt = typeof(r)
    local extra = ""
    if tt == "EnumItem" then
      local okv, vv = pcall(function() return r.Value end)
      extra = " Value=" .. tostring(vv)
    end
    print(label .. " ok=true t=" .. tt .. extra)
  else print(label .. " ok=false e=" .. tostring(r):sub(1, 110)) end
end
t("TAPV", function() return Enum.AppShellActionType.TapGamePageTab.Value end)
t("ADU", function() return Enum.AdUnitStatus end)
t("ADU_ACTIVE", function() return Enum.AdUnitStatus.Active end)
t("SSCSA", function() return game:GetService("SoundService").CharacterSoundsUseNewApi end)
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "enumcheck.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:1800])
