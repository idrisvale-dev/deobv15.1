# Reverse.Luau

Discord bot that auto-detects and deobfuscates Roblox Luau scripts.
Supports 14 obfuscators in a single bot.

---

## supported obfuscators

| engine name      | obfuscator                        | language of engine |
|------------------|-----------------------------------|--------------------|
| `luraph_v15`     | Luraph v15 / v15.1                | Node.js + Python   |
| `luraph_v14`     | Luraph v14.7 / v14.8 / v14.9     | Python             |
| `ironbrew2`      | Ironbrew 2                        | .NET               |
| `ironbrew1`      | Ironbrew 1                        | Python             |
| `moonsec`        | Moonsec v2 / v3                   | .NET               |
| `77fuscator`     | 77fuscator                        | .NET               |
| `prometheus`     | Prometheus                        | Node.js            |
| `clyde`          | Clyde                             | Node.js            |
| `luaobfuscator`  | LuaObfuscator.com                 | Node.js            |
| `ironveil`       | Ironveil                          | Node.js            |
| `hercules`       | Hercules (BE / VM)                | Python             |
| `centurion`      | Centurion 6.x                     | Python             |
| `luast`          | LUAST L3                          | Python             |
| `flowauth`       | FlowAuth                          | Python             |

---

## commands

| command                          | what it does                                    |
|----------------------------------|-------------------------------------------------|
| `.deobf <url>`                   | auto-detect and deobfuscate (attach file or URL) |
| `.deobf --engine <name> <url>`   | force a specific engine                         |
| `.detect <url>`                  | detect obfuscator without deobfuscating         |
| `.engines`                       | list all supported obfuscators                  |
| `.ping`                          | check bot latency                               |
| `.help`                          | show all commands                               |

---

## setup on Replit

### step 1 — upload files

upload all of these to your Replit project root alongside this bot:

```
LuaObfuscator-Deobfuscator-main.zip
Ironveil-Deobfuscator-V1-main.zip
hercules-deobfuscator-main.zip
MoonsecDeobfuscator-master.zip
77fuscatorDeobfuscator-main.zip
ClydeDeobfuscator-main.zip
luraph-v15-v14_x-deobfuscator-main.zip
Prometheus-Deobfuscator-main.zip
Luraph_v15_1_Deobfuscator_Fixed_All_Errors_1.rar
ib2-deobf.zip
FlowAuth-Deobfuscator-main.zip
centurion-deobfuscator.zip
Luast-main.zip
```

### step 2 — set your bot token

in the Replit Secrets tab (the lock icon), add:

```
key:   DISCORD_TOKEN
value: your Discord bot token
```

### step 3 — install dependencies

open the Replit Shell and run:

```bash
pip install -r requirements.txt
```

for Node.js engines (Luraph v15, Prometheus, Clyde, LuaObfuscator, Ironveil):

```bash
cd vendor/luraph_v151 && npm install
cd ../prometheus && npm install
cd ../clyde && npm install
cd ../luaobfuscator && npm install
cd ../ironveil/deobfuscator && npm install
```

for .NET engines (Ironbrew2, Moonsec, 77fuscator) — these are optional on Replit
since Replit does not ship .NET by default. skip them if you don't need those engines.
on a VPS you can install .NET 8 and then `dotnet build` inside each vendor directory.

### step 4 — extract vendor archives

```bash
python setup.py
```

this extracts all ZIPs and the RAR into the `vendor/` directory automatically.

### step 5 — run the bot

```bash
python main.py
```

the bot will print `bot online: BotName#0000` when it connects.

### keep-alive (Replit)

the bot runs a Flask server on port 8080 automatically.
use UptimeRobot (free) to ping your Replit URL every 5 minutes to keep it alive.

---

## moving to a VPS

when you move off Replit:

1. copy the whole project folder to your VPS
2. upload the archive ZIPs to the project root and run `python setup.py`
3. install Node.js 18+, Python 3.10+, and optionally .NET 8
4. set `DISCORD_TOKEN` in your environment or a `.env` file
5. run with `python main.py` or wrap it in a `systemd` service or `screen` session

---

## notes

- scripts are processed one at a time per user request
- large scripts (Luraph v15 especially) can take several minutes
- output larger than 8MB gets uploaded to hastebin automatically
- the bot deletes all temp files after each request

---

## engine runtime requirements

| engine runtime | engines that need it                              |
|----------------|---------------------------------------------------|
| Python 3.10+   | luraph_v14, ironbrew1, hercules, centurion, luast, flowauth |
| Node.js 18+    | luraph_v15, prometheus, clyde, luaobfuscator, ironveil |
| .NET 8         | ironbrew2, moonsec, 77fuscator                    |
