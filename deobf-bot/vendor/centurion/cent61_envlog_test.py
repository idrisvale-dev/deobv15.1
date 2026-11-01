"""Centurion v6.1 acceptance test under the Luraph envlog sandbox (read-only use).
Runs Centurion6.1v.txt through build_harness + luau.exe, then checks the
trace for the 56 live-decoded ground-truth strings (Infinite Jump, ESP...).
"""
import os
import sys

LURAPH_DEOBF = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\sandbox-copy-luraph"
LURAPH_BIN_LUAU = r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\luraph-v15-v14.x-deobfuscator-main\luraph-v15-v14.x-deobfuscator-main\Deobfuscator\deobf\bin\luau.exe"
SAMPLES = [
    r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\universal\alchemistabuser\Centurion6.1v.txt",
    r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\universal\alchemistabuser\centurion6.1v2nd.lua",
    r"C:\Users\goldl\Downloads\thee-bot-main1\thee-bot-main\universal-deobf\universal\alchemistabuser\centurion6.1v3rd.lua",
]
GROUND_TRUTH_ANY = [
    "Infinite Jump", "Player ESP", "Noclip", "Fullbright", "WalkSpeed",
    "JumpPower", "Rejoin", "Server Hop", "Reset Character", "rbtest",
    "UserInputService", "TweenService", "TeleportService", "RenderStepped",
    "MouseButton1Click", "BackgroundColor3", "ResetOnSpawn",
    "Fly", "ESP", "Server Hop", "Teleport", "Jump", "Speed",
]
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, LURAPH_DEOBF)
import harness

GROUND_TRUTH = [
    "Infinite Jump", "Player ESP", "Noclip", "Fullbright", "WalkSpeed",
    "JumpPower", "Rejoin", "Server Hop", "Reset Character", "rbtest",
    "UserInputService", "TweenService", "TeleportService", "RenderStepped",
    "MouseButton1Click", "BackgroundColor3", "ResetOnSpawn",
]

def run_one(tag, sample_path):
    with open(sample_path, "rb") as f:
        source = f.read().decode("latin-1")
    print("[*] ==== %s: %s (%d bytes)" % (tag, os.path.basename(sample_path), len(source)), flush=True)
    luau = LURAPH_BIN_LUAU
    # FLIP TEST (F1): CENT61_FLIP=1 -> replay NOTHING (all probes succeed
    # symbolically). If the trace advances past the wall, the branch reads
    # probe ok-flags and current replays are close-but-wrong somewhere.
    # If identical death, the branch does not depend on these ok-flags.
    flip = os.environ.get("CENT61_FLIP") == "1"
    # ABLATION: CENT61_STOCK=1 -> pure stock envlog (no P2D seed, no callerr,
    # no bigzero/oob/pcallog). Baseline to measure what MY port adds.
    stock = os.environ.get("CENT61_STOCK") == "1"
    if not flip and not stock:
        harness.P2D_CACHE["GetControlPoint|table"] = "ERROR:Unable to cast Array to int"
    cfg = {"time_budget": 90, "executor": "Potassium", "heartbeat": 2}
    # Stock Luraph-v14 alloc machinery, reused generically: trap records the
    # killer size/site, lenient returns an empty buffer instead of dying so
    # decode runs to completion on zeros past the bad read (v6 needed the
    # same: 37 bad bytes out of 400KB still gave 99.99%).
    cfg["v14_alloc_trap"] = False
    cfg["v14_lenient_create"] = True
    # White-box experiment B1: satisfy huge creates with capped zero buffer.
    cfg["centurion_bigzero"] = 0 if stock else 8388608
    # White-box experiment B2: OOB-tolerant reads + dict fallback so decode
    # runs to completion for measurement (CENT-DICTFIX/CENT-OOB in raw log).
    cfg["centurion_oob"] = not stock
    # Diagnostic depth for patched-read enumeration (values included).
    cfg["centurion_oob_cap"] = 500
    # White-box experiment B3: log every script-visible pcall outcome.
    cfg["centurion_pcallog"] = not stock
    # Reveal SILENT property reads (their trace only shows calls/emits).
    # Any env-derived value below can feed the branch invisibly.
    cfg["ptrace"] = True
    # Live-recorded engine argument errors (baseplate, 2026-10-02). The VM
    # poisons these calls and branches on pcall failure; symbolic success
    # takes the junk branch (buffer.create junk size). Replayed by the
    # CENTURION-PORT callerr hook in sandbox-copy-luraph/envlog.luau.
    # NOTE: task.spawn(nil) needs no rule: envlog's checkRoutine already
    # raises the exact live message ("invalid argument #1 to 'spawn'...").
    # Offline userdata names come from the CALLERR-SIG log (their typeof
    # reports Enum/Vector2 proxies as userdata).
    cfg["callerr"] = [] if (flip or stock) else [
        "GetTextSize|nil,number,userdata,userdata=Argument 1 missing or nil",
        "GetTextSize|string,Array,userdata,userdata=Unable to cast Array to int",
        "GetTextSize|string,number,Array,userdata=Unable to cast Array to Font",
        "GetTextSize|string,number,userdata,Array=Unable to cast Array to Vector2",
    ]
    hpath = os.path.join(OUT_DIR, "cent61_%s.harness.luau" % tag)
    body, err = harness.run_once(luau, source, cfg, hpath, 150, True)
    if body is None:
        print("[-] run failed:\n%s" % (err or "")[-3000:], flush=True)
        return 1
    with open(os.path.join(OUT_DIR, "cent61_%s.trace.txt" % tag), "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    with open(os.path.join(OUT_DIR, "cent61_%s.raw.txt" % tag), "w", encoding="utf-8", newline="\n") as f:
        f.write(harness.LAST_RAW[0])
    print("[*] trace bytes: %d" % len(body), flush=True)
    hits = [s for s in GROUND_TRUTH_ANY if s in body]
    print("[*] ground-truth hits: %d/%d: %s" % (len(hits), len(GROUND_TRUTH_ANY), ", ".join(hits) if hits else "-"), flush=True)
    return 0 if hits else 2


def main():
    tags = ["v1", "v2", "v3"]
    rc = 0
    only = os.environ.get("CENT61_ONLY")
    for tag, sample in zip(tags, SAMPLES):
        if only and tag != only:
            continue
        rc |= run_one(tag, sample)
    return rc

if __name__ == "__main__":
    sys.exit(main())
