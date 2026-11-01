import discord
from discord.ext import commands
import asyncio
import aiohttp
import os
import tempfile
import time
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime

from keep_alive import keep_alive
from detector import detect_obfuscator
from runner import run_engine, cancel_job, has_active_job

TOKEN        = os.environ.get("DISCORD_TOKEN")
PASTEBIN_KEY = os.environ.get("PASTEBIN_API_KEY")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# embed colors
YELLOW  = 0xFEE75C   # in process
GREEN   = 0x57F287   # success
RED     = 0xFF0000   # failed / error
GREY    = 0x99AAB5   # unsupported / not detected
BLURPLE = 0x5865F2   # info / help / engines / history

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=5))


# ─────────────────────────────────────────────
# embed builders
# ─────────────────────────────────────────────

def make_embed(description=None, title=None, color=RED, footer=None):
    e = discord.Embed(color=color, timestamp=datetime.utcnow())
    if title:       e.title       = title
    if description: e.description = description
    if footer:      e.set_footer(text=footer)
    return e


def processing_embed(msg="In Process....."):
    return make_embed(title=msg, color=YELLOW)


def success_embed(engine, elapsed, size_kb, extra=None):
    e = discord.Embed(title="Deobfuscated", color=GREEN, timestamp=datetime.utcnow())
    e.add_field(name="Engine", value=f"`{engine}`",         inline=True)
    e.add_field(name="Time",   value=f"`{elapsed:.1f}s`",   inline=True)
    e.add_field(name="Size",   value=f"`{size_kb:.1f} KB`", inline=True)
    if extra:
        e.description = extra
    return e


def failed_embed(msg):
    return make_embed(title="Failed", description=msg, color=RED)


def unsupported_embed(msg="could not detect a supported obfuscator.\nscript may be clean, unsupported, or the version is too new."):
    return make_embed(title="Unsupported", description=msg, color=GREY)


def info_embed(title, description=None, footer=None):
    return make_embed(title=title, description=description, color=RED, footer=footer)


# ─────────────────────────────────────────────
# upload helpers
# ─────────────────────────────────────────────

async def upload_github(content: str, filename: str) -> str:
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not set in environment.")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "description": "deobfuscated via Reverse.Luau",
        "public": False,
        "files": {filename: {"content": content}},
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.github.com/gists",
            json=payload, headers=headers,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as r:
            if r.status == 201:
                return (await r.json())["html_url"]
            raise RuntimeError(f"GitHub API returned {r.status}: {(await r.text())[:200]}")


async def upload_pastebin(content: str, filename: str) -> str:
    if not PASTEBIN_KEY:
        raise RuntimeError("PASTEBIN_API_KEY not set in environment.")
    payload = {
        "api_dev_key":           PASTEBIN_KEY,
        "api_option":            "paste",
        "api_paste_code":        content,
        "api_paste_name":        filename,
        "api_paste_format":      "lua",
        "api_paste_private":     "1",
        "api_paste_expire_date": "N",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://pastebin.com/api/api_post.php",
            data=payload,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as r:
            text = await r.text()
            if r.status == 200 and text.startswith("https://"):
                return text.strip()
            raise RuntimeError(f"Pastebin error: {text[:200]}")


async def upload_hastebin(content: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://hastebin.com/documents",
            data=content.encode(),
            timeout=aiohttp.ClientTimeout(total=20),
        ) as r:
            if r.status == 200:
                key = (await r.json())["key"]
                return f"https://hastebin.com/{key}.lua"
            raise RuntimeError(f"Hastebin returned HTTP {r.status}")


# ─────────────────────────────────────────────
# paste view
# ─────────────────────────────────────────────

class PasteView(discord.ui.View):
    def __init__(self, content: str, filename: str, emb: discord.Embed):
        super().__init__(timeout=600)
        self.content  = content
        self.filename = filename
        self.emb      = emb
        self._cache   = {}

    async def _handle(self, interaction, service, upload_fn, button, field_label):
        await interaction.response.defer()
        if service in self._cache:
            url = self._cache[service]
        else:
            try:
                url = await upload_fn(self.content, self.filename)
                self._cache[service] = url
            except Exception as e:
                await interaction.followup.send(
                    embed=failed_embed(f"upload to {service} failed: {e}"),
                    ephemeral=True
                )
                return

        existing = next(
            (i for i, f in enumerate(self.emb.fields) if f.name == field_label), None
        )
        if existing is not None:
            self.emb.set_field_at(existing, name=field_label, value=url, inline=False)
        else:
            self.emb.add_field(name=field_label, value=url, inline=False)

        button.disabled = True
        button.style    = discord.ButtonStyle.secondary
        await interaction.message.edit(embed=self.emb, view=self)

    @discord.ui.button(label="\u200b", emoji=discord.PartialEmoji(name="github",   id=1565700356267188264), style=discord.ButtonStyle.secondary)
    async def github_btn(self, interaction, button):
        await self._handle(interaction, "github",   lambda c, f: upload_github(c, f),   button, "GitHub Gist")

    @discord.ui.button(label="\u200b", emoji=discord.PartialEmoji(name="pastebin", id=1565700440585273344), style=discord.ButtonStyle.secondary)
    async def pastebin_btn(self, interaction, button):
        await self._handle(interaction, "pastebin", lambda c, f: upload_pastebin(c, f), button, "Pastebin")

    @discord.ui.button(label="\u200b", emoji=discord.PartialEmoji(name="hastebin", id=1565701270348628058), style=discord.ButtonStyle.secondary)
    async def hastebin_btn(self, interaction, button):
        await self._handle(interaction, "hastebin", lambda c, f: upload_hastebin(c),    button, "Hastebin")

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


def build_paste_embed(engine, elapsed, size_kb):
    e = discord.Embed(title="Deobfuscated", color=GREEN, timestamp=datetime.utcnow())
    e.description = "click a service below to get a share link."
    e.add_field(name="Engine", value=f"`{engine}`",         inline=True)
    e.add_field(name="Time",   value=f"`{elapsed:.1f}s`",   inline=True)
    e.add_field(name="Size",   value=f"`{size_kb:.1f} KB`", inline=True)
    e.set_footer(text="buttons expire after 10 minutes")
    return e


# ─────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────

def record_history(user_id, engine, elapsed, size_kb, status):
    _history[user_id].appendleft({
        "engine":  engine,
        "elapsed": elapsed,
        "size_kb": size_kb,
        "status":  status,
        "at":      datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    })


async def fetch_script(ctx, url_or_attach):
    if url_or_attach:
        url = url_or_attach.strip()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise ValueError(f"failed to fetch URL (HTTP {resp.status})")
                data     = await resp.read()
                filename = url.split("/")[-1].split("?")[0] or "script.lua"
                return data, filename
    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(att.url) as resp:
                return await resp.read(), att.filename
    raise ValueError("no file attached and no URL provided")


async def _run_deobf_core(ctx, url, force_engine=None):
    user_id = ctx.author.id

    if has_active_job(user_id):
        await ctx.send(embed=make_embed(
            title="Already Running",
            description="you already have a job running. use `.cancel` to stop it first.",
            color=YELLOW
        ))
        return None

    status = await ctx.send(embed=processing_embed("Fetching Script....."))

    try:
        data, filename = await fetch_script(ctx, url)
    except Exception as e:
        await status.edit(embed=failed_embed(f"error fetching script: {e}"))
        return None

    suffix = Path(filename).suffix or ".lua"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        input_path = tmp.name

    engine_name = force_engine
    start       = None

    try:
        if not engine_name:
            await status.edit(embed=processing_embed("Detecting Obfuscator....."))
            engine_name, confidence = detect_obfuscator(input_path)
            if not engine_name:
                await status.edit(embed=unsupported_embed())
                return None
            await status.edit(embed=make_embed(
                title="In Process.....",
                description=f"detected: `{engine_name}` (confidence: `{confidence}%`)\nrunning deobfuscator... use `.cancel` to stop.",
                color=YELLOW
            ))
        else:
            await status.edit(embed=make_embed(
                title="In Process.....",
                description=f"forcing engine: `{engine_name}`\nrunning... use `.cancel` to stop.",
                color=YELLOW
            ))

        start       = time.time()
        output_path = await asyncio.get_event_loop().run_in_executor(
            None, run_engine, engine_name, input_path, user_id
        )
        elapsed = time.time() - start
        size_kb = os.path.getsize(output_path) / 1024

        await status.delete()
        return output_path, engine_name, elapsed, size_kb

    except Exception as e:
        elapsed   = time.time() - start if start else 0
        cancelled = "cancelled" in str(e).lower()
        if cancelled:
            await status.edit(embed=make_embed(title="Cancelled", description="job was cancelled.", color=GREY))
        else:
            await status.edit(embed=failed_embed(str(e)))
        record_history(user_id, engine_name or "unknown", elapsed, 0, "cancelled" if cancelled else "failed")
        return None

    finally:
        try:
            os.unlink(input_path)
        except Exception:
            pass


# ─────────────────────────────────────────────
# commands
# ─────────────────────────────────────────────

@bot.command(name="deobf")
async def deobf(ctx, url: str = None):
    parts = ctx.message.content.split()
    if "--engine" in parts:
        try:
            idx         = parts.index("--engine")
            engine_name = parts[idx + 1]
            remaining   = [p for i, p in enumerate(parts) if i not in (0, idx, idx + 1)]
            url         = remaining[0] if remaining else None
        except (IndexError, ValueError):
            await ctx.send(embed=failed_embed("usage: `.deobf --engine <name> <url>`"))
            return
        result = await _run_deobf_core(ctx, url, force_engine=engine_name)
    else:
        result = await _run_deobf_core(ctx, url)

    if not result:
        return

    output_path, engine_name, elapsed, size_kb = result
    user_id = ctx.author.id

    if size_kb > 8000:
        content_str = open(output_path, "r", encoding="utf-8", errors="replace").read()
        try:
            paste_url = await upload_hastebin(content_str)
            await ctx.send(embed=success_embed(engine_name, elapsed, size_kb, extra=f"output too large — {paste_url}"))
        except Exception as e:
            await ctx.send(embed=failed_embed(f"paste upload failed: {e}"))
    else:
        await ctx.send(
            embed=success_embed(engine_name, elapsed, size_kb),
            file=discord.File(output_path, filename="deobfuscated.lua")
        )

    record_history(user_id, engine_name, elapsed, size_kb, "success")
    try:
        os.unlink(output_path)
    except Exception:
        pass


@bot.command(name="paste")
async def paste_cmd(ctx, url: str = None):
    parts = ctx.message.content.split()
    force_engine = None
    if "--engine" in parts:
        try:
            idx          = parts.index("--engine")
            force_engine = parts[idx + 1]
            remaining    = [p for i, p in enumerate(parts) if i not in (0, idx, idx + 1)]
            url          = remaining[0] if remaining else None
        except (IndexError, ValueError):
            await ctx.send(embed=failed_embed("usage: `.paste --engine <name> <url>`"))
            return

    result = await _run_deobf_core(ctx, url, force_engine=force_engine)
    if not result:
        return

    output_path, engine_name, elapsed, size_kb = result
    user_id  = ctx.author.id
    filename = "deobfuscated.lua"

    with open(output_path, "r", encoding="utf-8", errors="replace") as f:
        script_content = f.read()

    emb  = build_paste_embed(engine_name, elapsed, size_kb)
    view = PasteView(script_content, filename, emb)

    await ctx.send(
        embed=emb,
        file=discord.File(output_path, filename=filename),
        view=view,
    )

    record_history(user_id, engine_name, elapsed, size_kb, "success")
    try:
        os.unlink(output_path)
    except Exception:
        pass


@bot.command(name="cancel")
async def cancel(ctx):
    user_id = ctx.author.id
    if not has_active_job(user_id):
        await ctx.send(embed=make_embed(title="No Active Job", description="you have no active job running.", color=GREY))
        return
    if cancel_job(user_id):
        await ctx.send(embed=make_embed(title="Cancelling.....", color=YELLOW))
    else:
        await ctx.send(embed=make_embed(title="No Active Job", description="no active job found.", color=GREY))


@bot.command(name="queue")
async def queue(ctx):
    from runner import _active_jobs, _lock
    with _lock:
        count = len(_active_jobs)
    if count == 0:
        msg = "no jobs currently running."
    else:
        msg = f"`{count}` job(s) currently running."
    await ctx.send(embed=make_embed(title="Queue", description=msg, color=YELLOW if count > 0 else GREEN))


@bot.command(name="history")
async def history(ctx):
    user_id = ctx.author.id
    jobs    = list(_history.get(user_id, []))

    if not jobs:
        await ctx.send(embed=make_embed(title="History", description="no job history yet. run `.deobf` first.", color=GREY))
        return

    e = discord.Embed(title="Your Last Jobs", color=BLURPLE, timestamp=datetime.utcnow())
    for i, job in enumerate(jobs, 1):
        color_icon = "+" if job["status"] == "success" else "x" if job["status"] == "cancelled" else "-"
        e.add_field(
            name=f"`{i}.` [{color_icon}] `{job['engine']}`",
            value=f"`{job['elapsed']:.1f}s` | `{job['size_kb']:.1f} KB` | {job['at']}",
            inline=False,
        )
    await ctx.send(embed=e)


@bot.command(name="detect")
async def detect(ctx, url: str = None):
    status = await ctx.send(embed=processing_embed("Detecting Obfuscator....."))

    try:
        data, filename = await fetch_script(ctx, url)
    except Exception as e:
        await status.edit(embed=failed_embed(f"error fetching script: {e}"))
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".lua") as tmp:
        tmp.write(data)
        input_path = tmp.name

    try:
        engine_name, confidence = detect_obfuscator(input_path)
        if engine_name:
            e = discord.Embed(title="Detected", color=GREEN, timestamp=datetime.utcnow())
            e.add_field(name="Obfuscator", value=f"`{engine_name}`", inline=True)
            e.add_field(name="Confidence", value=f"`{confidence}%`", inline=True)
            e.set_footer(text="use .deobf to deobfuscate")
            await status.edit(embed=e)
        else:
            await status.edit(embed=unsupported_embed())
    finally:
        try:
            os.unlink(input_path)
        except Exception:
            pass


@bot.command(name="engines")
async def engines(ctx):
    e = discord.Embed(title="Supported Obfuscators", color=BLURPLE, timestamp=datetime.utcnow())
    engines_list = [
        ("luraph_v15",    "Luraph v15 / v15.1 (full devirt)"),
        ("luraph_v14",    "Luraph v14.7 / v14.8 / v14.9"),
        ("ironbrew2",     "Ironbrew 2"),
        ("ironbrew1",     "Ironbrew 1"),
        ("moonsec",       "Moonsec v2 / v3"),
        ("77fuscator",    "77fuscator (bytecode VM)"),
        ("prometheus",    "Prometheus"),
        ("clyde",         "Clyde"),
        ("luaobfuscator", "LuaObfuscator.com"),
        ("ironveil",      "Ironveil"),
        ("hercules",      "Hercules (BE / VM modes)"),
        ("centurion",     "Centurion 6.x"),
        ("luast",         "LUAST L3"),
        ("flowauth",      "FlowAuth"),
    ]
    for name, desc in engines_list:
        e.add_field(name=f"`{name}`", value=desc, inline=True)
    e.set_footer(text="use .deobf --engine <name> to force a specific one")
    await ctx.send(embed=e)


@bot.command(name="fetch")
async def fetch_cmd(ctx, url: str = None):
    if not url:
        await ctx.send(embed=failed_embed("usage: `.fetch <url>`"))
        return

    status = await ctx.send(embed=processing_embed("Fetching....."))

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url.strip(),
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"User-Agent": "Mozilla/5.0"}
            ) as resp:
                if resp.status != 200:
                    await status.edit(embed=failed_embed(f"failed to fetch URL (HTTP {resp.status})"))
                    return

                content_type = resp.headers.get("Content-Type", "")
                raw          = await resp.read()
                size_kb      = len(raw) / 1024

                # guess filename from URL
                from urllib.parse import urlparse
                parsed   = urlparse(url.strip())
                filename = parsed.path.split("/")[-1].split("?")[0]
                if not filename or "." not in filename:
                    # guess extension from content type
                    if "javascript" in content_type:
                        filename = "file.js"
                    elif "lua" in content_type or url.endswith(".lua"):
                        filename = "file.lua"
                    elif "html" in content_type:
                        filename = "file.html"
                    elif "json" in content_type:
                        filename = "file.json"
                    elif "python" in content_type or url.endswith(".py"):
                        filename = "file.py"
                    else:
                        filename = "file.txt"

        if size_kb > 8000:
            await status.edit(embed=failed_embed(
                f"file is too large to send (`{size_kb:.1f} KB`). Discord limit is 8 MB."
            ))
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name

        e = discord.Embed(title="Fetched", color=GREEN, timestamp=datetime.utcnow())
        e.add_field(name="File",   value=f"`{filename}`",       inline=True)
        e.add_field(name="Size",   value=f"`{size_kb:.1f} KB`", inline=True)
        e.add_field(name="Source", value=url.strip(),           inline=False)

        await status.edit(embed=e)
        await ctx.send(file=discord.File(tmp_path, filename=filename))

        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    except asyncio.TimeoutError:
        await status.edit(embed=failed_embed("request timed out. URL took too long to respond."))
    except Exception as e:
        await status.edit(embed=failed_embed(f"fetch failed: {e}"))


@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    e = discord.Embed(title="Pong", description=f"`{latency}ms`", color=GREEN, timestamp=datetime.utcnow())
    await ctx.send(embed=e)


@bot.command(name="help")
async def help_cmd(ctx):
    e = discord.Embed(title="Reverse.Luau", color=BLURPLE, timestamp=datetime.utcnow())
    cmds = [
        (".deobf <url>",                  "auto-detect and deobfuscate"),
        (".deobf --engine <name> <url>",  "force a specific engine"),
        (".paste <url>",                  "deobf + embed with share buttons"),
        (".paste --engine <name> <url>",  "force engine on paste mode"),
        (".detect <url>",                 "detect obfuscator only"),
        (".fetch <url>",                  "download a file from a URL and send it here"),
        (".cancel",                       "cancel your running job"),
        (".queue",                        "jobs running right now"),
        (".history",                      "your last 5 jobs"),
        (".engines",                      "list all 14 supported obfuscators"),
        (".ping",                         "bot latency"),
        (".help",                         "this message"),
    ]
    for name, desc in cmds:
        e.add_field(name=f"`{name}`", value=desc, inline=False)
    await ctx.send(embed=e)


@bot.event
async def on_ready():
    print(f"bot online: {bot.user} ({bot.user.id})")
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="discord.gg/2ttp6y8bk3"
        )
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(embed=failed_embed(f"error: {error}"))


if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
