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

TOKEN           = os.environ.get("DISCORD_TOKEN")
PASTEBIN_KEY    = os.environ.get("PASTEBIN_API_KEY")
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN")

EMBED_COLOR     = 0x5865F2   # discord blurple
EMBED_COLOR_OK  = 0x57F287   # discord green

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=5))


# ─────────────────────────────────────────────
# upload helpers
# ─────────────────────────────────────────────

async def upload_github(content: str, filename: str) -> str:
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN not set in Replit Secrets.")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "description": "deobfuscated via Reverse.Luau",
        "public": False,
        "files": {
            filename: {"content": content}
        },
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.github.com/gists",
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as r:
            if r.status == 201:
                data = await r.json()
                return data["html_url"]
            text = await r.text()
            raise RuntimeError(f"GitHub API returned {r.status}: {text[:200]}")


async def upload_pastebin(content: str, filename: str) -> str:
    if not PASTEBIN_KEY:
        raise RuntimeError("PASTEBIN_API_KEY not set in Replit Secrets.")
    payload = {
        "api_dev_key":       PASTEBIN_KEY,
        "api_option":        "paste",
        "api_paste_code":    content,
        "api_paste_name":    filename,
        "api_paste_format":  "lua",
        "api_paste_private": "1",   # unlisted
        "api_paste_expire_date": "N",  # never expire
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
# paste embed + button view
# ─────────────────────────────────────────────

class PasteView(discord.ui.View):
    def __init__(self, content: str, filename: str, embed: discord.Embed):
        super().__init__(timeout=600)   # buttons live for 10 min
        self.content  = content
        self.filename = filename
        self.embed    = embed
        self._cache   = {}              # service name -> url (avoid re-uploading)

    async def _handle(self, interaction: discord.Interaction, service: str,
                      upload_fn, button: discord.ui.Button, field_label: str):
        await interaction.response.defer()

        # reuse cached url if already uploaded to this service
        if service in self._cache:
            url = self._cache[service]
        else:
            try:
                url = await upload_fn(self.content, self.filename)
                self._cache[service] = url
            except Exception as e:
                await interaction.followup.send(
                    f"upload to {service} failed: {e}", ephemeral=True
                )
                return

        # add or update the field in the embed
        existing = next(
            (i for i, f in enumerate(self.embed.fields) if f.name == field_label),
            None
        )
        if existing is not None:
            self.embed.set_field_at(existing, name=field_label, value=url, inline=False)
        else:
            self.embed.add_field(name=field_label, value=url, inline=False)

        # mark the clicked button as done
        button.disabled = True
        button.style    = discord.ButtonStyle.secondary

        await interaction.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="\u200b", emoji=discord.PartialEmoji(name="github",  id=1565700356267188264), style=discord.ButtonStyle.secondary)
    async def github_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle(
            interaction, "github",
            lambda c, f: upload_github(c, f),
            button, "GitHub Gist"
        )

    @discord.ui.button(label="\u200b", emoji=discord.PartialEmoji(name="pastebin", id=1565700440585273344), style=discord.ButtonStyle.secondary)
    async def pastebin_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle(
            interaction, "pastebin",
            lambda c, f: upload_pastebin(c, f),
            button, "Pastebin"
        )

    @discord.ui.button(label="\u200b", emoji=discord.PartialEmoji(name="hastebin", id=1565701270348628058), style=discord.ButtonStyle.secondary)
    async def hastebin_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle(
            interaction, "hastebin",
            lambda c, f: upload_hastebin(c),
            button, "Hastebin"
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


def build_paste_embed(engine: str, elapsed: float, size_kb: float, filename: str) -> discord.Embed:
    embed = discord.Embed(
        title="Reverse.Luau",
        description="click a service below to get a share link.",
        color=EMBED_COLOR_OK,
        timestamp=datetime.utcnow(),
    )
    embed.add_field(name="Engine",   value=f"`{engine}`",          inline=True)
    embed.add_field(name="Time",     value=f"`{elapsed:.1f}s`",    inline=True)
    embed.add_field(name="Size",     value=f"`{size_kb:.1f} KB`",  inline=True)
    embed.set_footer(text="buttons expire after 10 minutes")
    return embed


# ─────────────────────────────────────────────
# shared fetch / history helpers
# ─────────────────────────────────────────────

def record_history(user_id: int, engine: str, elapsed: float, size_kb: float, status: str):
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
                data = await resp.read()
                filename = url.split("/")[-1].split("?")[0] or "script.lua"
                return data, filename

    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(att.url) as resp:
                data = await resp.read()
                return data, att.filename

    raise ValueError("no file attached and no URL provided")


async def _run_deobf_core(ctx, url, force_engine=None):
    """
    Runs the full deobf pipeline.
    Returns (output_path, engine_name, elapsed, size_kb) on success.
    Returns None on failure (error already sent to ctx).
    Cleans up input_path automatically.
    """
    user_id = ctx.author.id

    if has_active_job(user_id):
        await ctx.send("you already have a job running. use `.cancel` to stop it first.")
        return None

    status = await ctx.send("fetching script...")

    try:
        data, filename = await fetch_script(ctx, url)
    except Exception as e:
        await status.edit(content=f"error fetching script: {e}")
        return None

    suffix = Path(filename).suffix or ".lua"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        input_path = tmp.name

    engine_name = force_engine

    try:
        if not engine_name:
            await status.edit(content="detecting obfuscator...")
            engine_name, confidence = detect_obfuscator(input_path)
            if not engine_name:
                await status.edit(content="could not detect a supported obfuscator in this script.")
                return None
            await status.edit(
                content=f"detected: `{engine_name}` (confidence: `{confidence}%`)\n"
                        f"running deobfuscator... this may take a few minutes.\n"
                        f"use `.cancel` to stop."
            )
        else:
            await status.edit(
                content=f"forcing engine: `{engine_name}`\nrunning... use `.cancel` to stop."
            )

        start       = time.time()
        output_path = await asyncio.get_event_loop().run_in_executor(
            None, run_engine, engine_name, input_path, user_id
        )
        elapsed = time.time() - start
        size_kb = os.path.getsize(output_path) / 1024

        await status.delete()
        return output_path, engine_name, elapsed, size_kb

    except Exception as e:
        elapsed  = time.time() - start if "start" in dir() else 0
        err_str  = str(e)
        cancelled = "cancelled" in err_str.lower()
        await status.edit(content="job cancelled." if cancelled else f"deobfuscation failed: {e}")
        record_history(user_id, engine_name or "unknown", elapsed, 0,
                       "cancelled" if cancelled else "failed")
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
    """
    .deobf <url>                   auto-detect and deobfuscate
    .deobf --engine <name> <url>   force a specific engine
    """
    parts = ctx.message.content.split()
    if "--engine" in parts:
        try:
            idx         = parts.index("--engine")
            engine_name = parts[idx + 1]
            remaining   = [p for i, p in enumerate(parts) if i not in (0, idx, idx + 1)]
            url         = remaining[0] if remaining else None
        except (IndexError, ValueError):
            await ctx.send("usage: `.deobf --engine <name> <url>`")
            return
        result = await _run_deobf_core(ctx, url, force_engine=engine_name)
    else:
        result = await _run_deobf_core(ctx, url)

    if not result:
        return

    output_path, engine_name, elapsed, size_kb = result
    user_id = ctx.author.id

    header = f"engine: `{engine_name}` | time: `{elapsed:.1f}s` | size: `{size_kb:.1f} KB`"

    if size_kb > 8000:
        content_str = open(output_path, "r", encoding="utf-8", errors="replace").read()
        try:
            url = await upload_hastebin(content_str)
            await ctx.send(f"done. {header}\noutput too large for Discord — {url}")
        except Exception as e:
            await ctx.send(f"done. {header}\npaste upload failed: {e}")
    else:
        await ctx.send(
            content=f"done. {header}",
            file=discord.File(output_path, filename="deobfuscated.lua")
        )

    record_history(user_id, engine_name, elapsed, size_kb, "success")
    try:
        os.unlink(output_path)
    except Exception:
        pass


@bot.command(name="paste")
async def paste_cmd(ctx, url: str = None):
    """
    .paste <url>
    Deobfuscates and sends an embed with the file attached.
    Three buttons below let you upload to GitHub Gist, Pastebin, or Hastebin.
    """
    # --engine flag support on .paste too
    parts = ctx.message.content.split()
    force_engine = None
    if "--engine" in parts:
        try:
            idx          = parts.index("--engine")
            force_engine = parts[idx + 1]
            remaining    = [p for i, p in enumerate(parts) if i not in (0, idx, idx + 1)]
            url          = remaining[0] if remaining else None
        except (IndexError, ValueError):
            await ctx.send("usage: `.paste --engine <name> <url>`")
            return

    result = await _run_deobf_core(ctx, url, force_engine=force_engine)
    if not result:
        return

    output_path, engine_name, elapsed, size_kb = result
    user_id  = ctx.author.id
    filename = "deobfuscated.lua"

    with open(output_path, "r", encoding="utf-8", errors="replace") as f:
        script_content = f.read()

    embed = build_paste_embed(engine_name, elapsed, size_kb, filename)
    view  = PasteView(script_content, filename, embed)

    await ctx.send(
        embed=embed,
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
    """
    .cancel  —  cancel your running deobf job.
    """
    user_id = ctx.author.id
    if not has_active_job(user_id):
        await ctx.send("you have no active job running.")
        return
    if cancel_job(user_id):
        await ctx.send("cancelling job...")
    else:
        await ctx.send("no active job found.")


@bot.command(name="queue")
async def queue(ctx):
    """
    .queue  —  how many jobs are running right now.
    """
    from runner import _active_jobs, _lock
    with _lock:
        count = len(_active_jobs)
    if count == 0:
        await ctx.send("no jobs currently running.")
    elif count == 1:
        await ctx.send("1 job currently running.")
    else:
        await ctx.send(f"{count} jobs currently running.")


@bot.command(name="history")
async def history(ctx):
    """
    .history  —  your last 5 deobf jobs.
    """
    user_id = ctx.author.id
    jobs    = list(_history.get(user_id, []))

    if not jobs:
        await ctx.send("no job history yet. run `.deobf` first.")
        return

    lines = ["**your last deobf jobs**", ""]
    for i, job in enumerate(jobs, 1):
        icon = "+" if job["status"] == "success" else "x" if job["status"] == "cancelled" else "-"
        lines.append(
            f"`{i}.` [{icon}] `{job['engine']}` | "
            f"`{job['elapsed']:.1f}s` | "
            f"`{job['size_kb']:.1f} KB` | "
            f"{job['at']}"
        )

    await ctx.send("\n".join(lines))


@bot.command(name="detect")
async def detect(ctx, url: str = None):
    """
    .detect <url>  —  identify obfuscator without deobfuscating.
    """
    status = await ctx.send("fetching script...")

    try:
        data, filename = await fetch_script(ctx, url)
    except Exception as e:
        await status.edit(content=f"error: {e}")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".lua") as tmp:
        tmp.write(data)
        input_path = tmp.name

    try:
        engine_name, confidence = detect_obfuscator(input_path)
        if engine_name:
            await status.edit(
                content=f"obfuscator: `{engine_name}`\n"
                        f"confidence: `{confidence}%`\n"
                        f"use `.deobf` to deobfuscate."
            )
        else:
            await status.edit(
                content="no recognized obfuscator detected.\n"
                        "script may be clean, unsupported, or the version is too new."
            )
    finally:
        try:
            os.unlink(input_path)
        except Exception:
            pass


@bot.command(name="engines")
async def engines(ctx):
    """
    .engines  —  list all supported obfuscators.
    """
    lines = [
        "**supported obfuscators**",
        "",
        "`luraph_v15`     Luraph v15 / v15.1 (full devirt)",
        "`luraph_v14`     Luraph v14.7 / v14.8 / v14.9",
        "`ironbrew2`      Ironbrew 2",
        "`ironbrew1`      Ironbrew 1",
        "`moonsec`        Moonsec v2 / v3",
        "`77fuscator`     77fuscator (bytecode VM)",
        "`prometheus`     Prometheus",
        "`clyde`          Clyde",
        "`luaobfuscator`  LuaObfuscator.com",
        "`ironveil`       Ironveil",
        "`hercules`       Hercules (BE / VM modes)",
        "`centurion`      Centurion 6.x",
        "`luast`          LUAST L3",
        "`flowauth`       FlowAuth",
        "",
        "use `.deobf --engine <name>` to force a specific one.",
    ]
    await ctx.send("\n".join(lines))


@bot.command(name="ping")
async def ping(ctx):
    """
    .ping  —  bot latency.
    """
    latency = round(bot.latency * 1000)
    await ctx.send(f"pong. `{latency}ms`")


@bot.command(name="help")
async def help_cmd(ctx):
    """
    .help  —  all commands.
    """
    lines = [
        "**Reverse.Luau**",
        "",
        "`.deobf <url>`                    auto-detect and deobfuscate (URL or attach file)",
        "`.deobf --engine <name> <url>`    force a specific engine",
        "`.paste <url>`                    deobf + embed with GitHub / Pastebin / Hastebin buttons",
        "`.paste --engine <name> <url>`    force engine on paste mode",
        "`.detect <url>`                   detect obfuscator only",
        "`.cancel`                         cancel your running job",
        "`.queue`                          jobs running right now (all users)",
        "`.history`                        your last 5 jobs",
        "`.engines`                        list all 14 supported obfuscators",
        "`.ping`                           bot latency",
        "`.help`                           this message",
        "",
        "for `.paste` buttons to work, add these to Replit Secrets:",
        "`GITHUB_TOKEN`  —  GitHub PAT with gist scope",
        "`PASTEBIN_API_KEY`  —  from pastebin.com/doc_api",
        "(hastebin needs no key)",
    ]
    await ctx.send("\n".join(lines))


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
    await ctx.send(f"error: {error}")


if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
