"""Offline: exact behavior of v5's edge calls under envlog (no live)."""
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
  if ok then print(label .. " ok=true t=" .. typeof(r) .. " v=" .. tostring(r):sub(1, 60))
  else print(label .. " ok=false e=" .. tostring(r):sub(1, 100)) end
end
do local o = Instance.new('IntValue') t("SET", function() o.Value = 307961 return o.Value end) pcall(function() o:Destroy() end) end
local p = Instance.new('Path2D')
t("GCP0", function() return p:GetControlPoint(0) end)
t("GCP1", function() return p:GetControlPoint(1) end)
t("RCP1", function() return p:RemoveControlPoint(1) end)
t("SCP", function() return p:SetControlPoints({1, 2}) end)
"""

cfg = {"time_budget": 30, "executor": "Potassium", "heartbeat": 2}
hpath = os.path.join(OUT_DIR, "edge_probe.harness.luau")
body, err = harness.run_once(LUAU, SNIPPET, cfg, hpath, 60, True)
print("=== body ===")
print((body or "")[:1600])
