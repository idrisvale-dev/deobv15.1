import re

# Each entry: (engine_name, [(pattern, weight), ...], min_score_to_match)
# Patterns are checked against raw script text. Weights sum to a confidence score.

FINGERPRINTS = [
    (
        "luraph_v15",
        [
            (r"LPH_ENCSTR",         40),
            (r"LPH_ENCFUNC",        40),
            (r"LPH_CRASH",          30),
            (r"lph_enc",            20),
            (r"lura\.ph",           15),
            (r"luraph",             10),
            (r"v15\b",               5),
        ],
        40,
    ),
    (
        "luraph_v14",
        [
            (r"luraph",             30),
            (r"lura\.ph",           20),
            (r"v14\b",              15),
            (r"LPH_ENCSTR",         10),
        ],
        30,
    ),
    (
        "ironbrew2",
        [
            (r"IronBrew",           50),
            (r"Synapse",            10),
            (r'local\s+\w+\s*=\s*\{[^}]{2000,}\}',  25),
            (r"VM\s*\[",            10),
            (r"Deserialize",        15),
        ],
        40,
    ),
    (
        "ironbrew1",
        [
            (r"IronBrew",           40),
            (r"Ironbrew",           40),
            (r"iron\s*brew",        30),
            (r'local\s+\w+\s*=\s*\{[^}]{500,}\}',   15),
        ],
        30,
    ),
    (
        "moonsec",
        [
            (r"Moonsec",            60),
            (r"moonsec",            60),
            (r"MOONSEC",            60),
            (r"moon\s*sec",         30),
            (r"ByteCode",           10),
            (r"Luraph|lura",         5),
        ],
        50,
    ),
    (
        "77fuscator",
        [
            (r"77fuscator",         70),
            (r"77Fuscator",         70),
            (r"77FUSCATOR",         70),
            (r"BlobReader",         20),
            (r"XorKey",             15),
            (r"HandlerDb",          20),
        ],
        50,
    ),
    (
        "prometheus",
        [
            (r"Prometheus",         50),
            (r"prometheus",         40),
            (r"PROMETHEUS",         50),
            (r"PrometheusObfuscator",60),
            (r"__PROMETHEUS_",      40),
            (r"vm_execute",         15),
            (r"vm_opcode",          15),
        ],
        40,
    ),
    (
        "clyde",
        [
            (r"Clyde",              50),
            (r"CLYDE",              50),
            (r"clyde",              40),
            (r"ClydeObf",           60),
        ],
        40,
    ),
    (
        "luaobfuscator",
        [
            (r"luaobfuscator",      50),
            (r"LuaObfuscator",      50),
            (r"lua-obfuscator",     40),
            (r"luaobfuscator\.com", 70),
        ],
        40,
    ),
    (
        "ironveil",
        [
            (r"IronVeil",           60),
            (r"ironveil",           60),
            (r"Ironveil",           60),
            (r"IRONVEIL",           60),
        ],
        50,
    ),
    (
        "hercules",
        [
            (r"Hercules",           50),
            (r"hercules",           40),
            (r"HERCULES",           50),
            (r"HerculesObf",        60),
            (r"payload\.decode",    15),
            (r"vm_decompile",       10),
        ],
        40,
    ),
    (
        "centurion",
        [
            (r"Centurion",          50),
            (r"centurion",          40),
            (r"CENTURION",          50),
            (r"CenturionObf",       60),
            (r"cent6[0-9]",         30),
        ],
        40,
    ),
    (
        "luast",
        [
            (r"LUAST",              60),
            (r"luast",              50),
            (r"Luast",              50),
            (r"l3_deobf",           40),
            (r"luau_recover",       30),
        ],
        40,
    ),
    (
        "flowauth",
        [
            (r"FlowAuth",           60),
            (r"flowauth",           50),
            (r"FLOWAUTH",           60),
            (r"hop_challenge",      40),
            (r"hop_payload",        40),
            (r"LPH_ENCSTR.*FlowAuth|FlowAuth.*LPH_ENCSTR", 30),
        ],
        50,
    ),
]


def detect_obfuscator(script_path: str):
    """
    Returns (engine_name, confidence_percent) or (None, 0) if undetected.
    Reads up to 256KB to keep detection fast on huge files.
    """
    try:
        with open(script_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(262144)
    except Exception:
        return None, 0

    best_engine = None
    best_score = 0
    best_raw = 0

    for engine_name, patterns, min_score in FINGERPRINTS:
        score = 0
        max_possible = sum(w for _, w in patterns)
        for pattern, weight in patterns:
            try:
                if re.search(pattern, content, re.IGNORECASE):
                    score += weight
            except re.error:
                pass

        if score >= min_score and score > best_raw:
            best_raw = score
            best_engine = engine_name
            best_score = min(int((score / max_possible) * 100), 99)

    return best_engine, best_score
