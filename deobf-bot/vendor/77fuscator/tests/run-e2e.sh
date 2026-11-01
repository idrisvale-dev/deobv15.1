#!/usr/bin/env bash
# End-to-end: for each tests/t*.lua (+ hello/benchmark fixtures):
#   1. run original with stock lua5.1.exe            -> expected stdout
#   2. obfuscate with geniussolution CLI.exe         -> out.lua
#   3. deobfuscate (plain and --strings)             -> out.luac / out.strings.luac
#   4. run both with lua5.1.exe                      -> actual stdout
#   5. diff against oracle (benchmark timing lines are normalized)
#   6. for t12_strings_enc: the recovered literal must be visible in the binary
set -u
DEOB_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLI_DIR="C:/Users/corne/Downloads/source/source/77main CLI/bin/Debug/net8.0"
LUA="$CLI_DIR/lua5.1.exe"
CLI="$CLI_DIR/geniussolution CLI.exe"
WORK="$DEOB_DIR/tests/_e2e"
mkdir -p "$WORK"

cd "$DEOB_DIR" && dotnet build -v q --nologo >/dev/null 2>&1

pass=0; fail=0
norm() { sed 's/^Time:.*/Time:/' "$1"; }
check() { # name mode
    if diff <(norm "$WORK/$1.expected") <(norm "$WORK/$1.$2.actual") > "$WORK/$1.$2.diff" 2>&1; then
        echo "$1 [$2]: PASS"; pass=$((pass+1))
    else
        echo "$1 [$2]: FAIL (first diff lines:)"
        head -6 "$WORK/$1.$2.diff" | sed 's/^/    /'
        fail=$((fail+1))
    fi
}

for src in "$DEOB_DIR"/tests/t*.lua "$DEOB_DIR/tests/hello.lua" "$DEOB_DIR/tests/benchmark.lua"; do
    name="$(basename "$src" .lua)"
    # 1. oracle
    "$LUA" "$src" > "$WORK/$name.expected" 2>&1
    if [ $? -ne 0 ]; then echo "$name: SKIP (original does not run on 5.1)"; continue; fi
    # 2. obfuscate (CLI overwrites/restores input; writes out.lua in its cwd)
    cp "$src" "$CLI_DIR/_e2e_in.lua"
    (cd "$CLI_DIR" && rm -f out.lua && "$CLI" "_e2e_in.lua" >/dev/null 2>&1)
    if [ ! -f "$CLI_DIR/out.lua" ]; then echo "$name: FAIL (obfuscator produced no out.lua)"; fail=$((fail+1)); continue; fi
    cp "$CLI_DIR/out.lua" "$WORK/$name-obfuscated.lua"
    # 3+4. deobfuscate in both modes and run
    (cd "$DEOB_DIR" && dotnet run --no-build -- "$WORK/$name-obfuscated.lua" -o "$WORK/$name.luac" > "$WORK/$name.deob.log" 2>&1)
    "$LUA" "$WORK/$name.luac" > "$WORK/$name.plain.actual" 2>&1
    check "$name" plain
    (cd "$DEOB_DIR" && dotnet run --no-build -- "$WORK/$name-obfuscated.lua" --strings -o "$WORK/$name.strings.luac" > "$WORK/$name.deob-strings.log" 2>&1)
    "$LUA" "$WORK/$name.strings.luac" > "$WORK/$name.strings.actual" 2>&1
    check "$name" strings
    # 6. recovery proof: the canary literal must be a plaintext constant in the binary
    if [ "$name" = "t12_strings_enc" ]; then
        if grep -q "CANARY-literal-7f3a9b-wee" "$WORK/$name.strings.luac"; then
            echo "$name [canary-in-binary]: PASS"; pass=$((pass+1))
        else
            echo "$name [canary-in-binary]: FAIL"; fail=$((fail+1))
        fi
        nrec=$(grep -oE "recovered [0-9]+ encrypted string" "$WORK/$name.deob-strings.log" | grep -oE "[0-9]+" | head -1)
        echo "$name [info]: $nrec literals recovered"
    fi
done
echo "== $pass passed, $fail failed =="
