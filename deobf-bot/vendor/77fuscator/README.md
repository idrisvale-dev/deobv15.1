# 77fuscator 0.6.1 Early Build Leak Deobfuscator

A static deobfuscator for scripts obfuscated with **77fuscator** (a Lua 5.1 VM
obfuscator). It takes an obfuscated `.lua` script and reconstructs a **standard
Lua 5.1 binary chunk** (`.luac`) that loads and runs under a stock Lua 5.1
interpreter, with the original program's behavior.

## Usage

```
deobfuscator <input.lua> [-o output.luac] [--strings] [--dump-protos] [--dump-handlers] [--dump-lifted]
```

- `-o <file>` — write the recovered stock Lua 5.1 binary chunk.
- `--strings` — additionally recover string literals encrypted by the
  obfuscator's string encryption: decrypt them statically and rewrite the
  decryption call sites to direct `LOADK`s of the plaintext (opt-in; the
  bytecode is semantically identical without it, strings just stay
  runtime-decrypted).
- `--dump-protos` — dump the deserialized blob proto tree.
- `--dump-handlers` — dump the dispatch-tree analysis and per-enum handler
  classification.
- `--dump-lifted` — dump the lifted code (pre-linearization node graph and
  final stock disassembly).

Verification: `bash tests/run-e2e.sh` obfuscates every `tests/t*.lua` with the
original obfuscator CLI, deobfuscates (both modes), runs the results under the
bundled stock `lua5.1.exe`, and diffs stdout against the original script.

## Pipeline

- **Layer 1 — Peel (`src/Peel/Layers.cs`).** The outer script is either the VM
  script itself or its LZW+base36-compressed form (`ExtraCompression`); both are
  unwrapped and the hex bytecode blob (`77FUS|<HEX>`) is extracted.
- **Layer 2 — XOR key (`src/Lua/XorKey.cs`).** The per-build `PrimaryXorKey` is
  recovered by statically evaluating the `NumberObfuscation`-shaped IIFE that
  produces it (tree-walking evaluator over Loretta syntax), with brute force as
  fallback.
- **Layer 3 — Blob deserialization (`src/Chunk/IR.cs`,
  `src/Chunk/BlobReader.cs`).** Section order (4! permutations) and the
  constant-type tag mapping are per-build random; all combinations are tried and
  the one consuming the blob exactly wins. Produces `Proto` trees with
  instructions `{ PC, Type, Enum, A, B, C, E, F }` where `Enum` is a per-build
  virtual opcode id. A **format v2** variant seen in the wild (prefix-less
  LZW+base36 raw blob, watermark "77fuscator 0.6.1 EARLY BUILD") is supported
  too: its uniform instruction records (descriptor + ULEB enum + four i32 + one
  i16 payload fields under per-build numeric keys), fixed bool/number/string
  constant tags, and ULEB-length strings are derived from the sample's own
  embedded runtime deserializer; the on-disk field order (obscured by the
  flattener) is brute-forced and disambiguated semantically after handler
  classification (jump targets and constant references must be in range).
- **Layer 4 — Handler classification (`src/Vm/DispatchTree.cs`,
  `src/Vm/LuaIR.cs`, `src/Vm/HandlerDb.cs`).** The binary-search dispatch tree
  is extracted from the VM script and every handler body is matched against
  structural templates of the obfuscator's `Op*.cs` semantics, recovering the
  per-build instruction field keys, const/register variants, and operand
  permutations (shuffle clones). CFRewriter loop/expression mutations are
  canonicalized back first (`LuaIR`); ambiguous template matches are deferred
  until self-anchoring handlers (e.g. `NewStack`) bind the shared roles, so a
  wrong early guess can't poison the rest.
- **Layer 5 — Lifting (`src/Lift/Lifter.cs`).** Per proto: polymorphic-enum
  resolution (field offsets undone), `GetInstruction` fixup-pattern repair
  (Redirect / RegisterReload / ResetOpcodeData), fake-global name recovery
  (EnhancedSecurity renames the 10 library globals; the anti-tamper block's
  `{[fake]=_G[real]}` constructor gives the mapping back), prologue stripping
  (Prep* + anti-tamper block, delimited by the `LoadNil A=0` / `PrepStackArgs`
  marker), operand decode (every `Serializer.Mutate` inverted to stock Lua 5.1
  operand meaning), then CFG recovery: junk JMP-connector threading,
  reachability, trace-scheduling linearization with cond-flag flipping, and sBx
  recomputation. Unreferenced child protos (anti-tamper callbacks) are pruned
  and CLOSURE Bx remapped.
- **Layer 6 — Emission (`src/Emit/LuacWriter.cs`).** Standard Lua 5.1 binary
  chunk (ESC"Lua" 0x51, LE, int=4, size_t=8, Instruction=4, number=f64).
  Tampered decoy constants are emitted as nil; debug sections are empty.
- **String recovery (`src/Lift/StringRecovery.cs`, `--strings`).** StringToLocal
  + ConstantEncryption moved every literal into `(Strings_Table[i])` backed by
  `(DecryptStringForm(key, enc, L))` calls in the main chunk with
  `plain[j] = enc[j] ^ key[j % L]`. The pass recognizes the lifted 5-instruction
  call-site shape (`MOVE`; `LOADK` key; `LOADK` enc; `LOADK` L; `CALL f,4,2`
  with `L == #key`, single shared key constant), emulates the XOR, and rewrites
  each site to a direct `LOADK` of the recovered literal.

## Verification

`tests/run-e2e.sh`: 13 test programs (arithmetic/RK, control flow, numeric +
generic for, closures/shared upvalues, varargs, table constructors incl.
SETLIST batches, method calls, multiple returns/tailcalls, string ops, all
comparisons, a mixed stress test, a string-encryption canary test) plus the
`hello`/`benchmark` fixtures — each obfuscated fresh (new randomness every run),
deobfuscated in both modes, run under the bundled stock `lua5.1.exe`, and
diffed against the original's stdout. The `--strings` mode is additionally
verified by checking the canary literal appears as a plaintext constant inside
the `.luac` binary. Current status: **all green in both modes** (repeated
rounds; zero unliftable instructions in every sample).

The target Lua build's loader contains a bytecode verifier; the emitted chunks
satisfy it (cond ops followed by JMP, FORLOOP jumps backward, CLOSURE pseudo
instructions, dead `RETURN 0 0` after TAILCALL, proto ends with RETURN,
`is_vararg` ∈ {0,2,3}).

## Known limitations

- Obfuscator-side information loss is unrecoverable: `const % register` computes
  `Const % Const[reg]` (its `OpModB` body is copy-pasted from `OpModBC`), and
  its constant folder mis-folds `%` with negative operands (C semantics). Where
  the obfuscator breaks behavior, output matches the *obfuscated* program.
- `error("msg")` position prefixes (`file:line:`) and all debug info are absent
  (the blob carries none).
- `NEWTABLE` size hints are lost (emitted as 0,0 — semantically inert).
- `SETLIST` with C=0 (table constructors over 25550 elements) is unliftable —
  the Data-slot payload is never serialized into the blob.
- Nested vararg protos get `is_vararg=2`; the legacy `arg` table (NEEDSARG) is
  not reconstructed (never produced by the obfuscator's minify pipeline).
- Genuinely unliftable instructions (none encountered in any test) are
  substituted with verifier-safe NOPs and counted in the lift report.
- `--strings` only rewrites call sites matching the exact obfuscator scheme;
  anything unrecognized is left untouched (runtime decryption still works).

## Leaked 77fuscator 0.6.1 Early Build Source
[Leaked source](https://github.com/dunnerulz/77fuscator-fork)

# Made by @bytecode1337 | @bytecoded1337 on discord
