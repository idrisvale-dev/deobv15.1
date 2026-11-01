import subprocess
import tempfile
import os
import threading

from engines import get_engine

ENGINE_TIMEOUT = {
    "luraph_v15":    900,
    "luraph_v14":    600,
    "ironbrew2":     300,
    "ironbrew1":     300,
    "moonsec":       120,
    "77fuscator":    120,
    "prometheus":    180,
    "clyde":         180,
    "luaobfuscator": 180,
    "ironveil":      120,
    "hercules":      300,
    "centurion":     600,
    "luast":         600,
    "flowauth":      600,
}

DEFAULT_TIMEOUT = 300

# active jobs: user_id -> {"proc": Popen | None, "cancel": threading.Event}
_active_jobs: dict[int, dict] = {}
_lock = threading.Lock()


def register_job(user_id: int) -> threading.Event:
    """Register a new job for a user. Returns a cancel Event."""
    cancel_event = threading.Event()
    with _lock:
        _active_jobs[user_id] = {"proc": None, "cancel": cancel_event}
    return cancel_event


def set_job_proc(user_id: int, proc: subprocess.Popen):
    """Called by engine wrappers to hand off the live Popen so cancel can kill it."""
    with _lock:
        if user_id in _active_jobs:
            _active_jobs[user_id]["proc"] = proc


def cancel_job(user_id: int) -> bool:
    """Cancel a running job. Returns True if a job was found and cancelled."""
    with _lock:
        job = _active_jobs.get(user_id)
        if not job:
            return False
        job["cancel"].set()
        proc = job.get("proc")
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
        return True


def unregister_job(user_id: int):
    with _lock:
        _active_jobs.pop(user_id, None)


def has_active_job(user_id: int) -> bool:
    with _lock:
        return user_id in _active_jobs


def run_engine(engine_name: str, input_path: str, user_id: int = 0) -> str:
    """
    Run the deobfuscator engine on input_path.
    Returns output file path (caller must delete).
    Raises RuntimeError on failure or cancellation.
    """
    engine_fn = get_engine(engine_name)
    if not engine_fn:
        raise RuntimeError(f"unknown engine: {engine_name}")

    cancel_event = register_job(user_id) if user_id else threading.Event()

    output_fd, output_path = tempfile.mkstemp(suffix=".lua", prefix=f"deobf_{engine_name}_")
    os.close(output_fd)

    timeout = ENGINE_TIMEOUT.get(engine_name, DEFAULT_TIMEOUT)

    try:
        engine_fn(input_path, output_path, timeout, cancel_event=cancel_event, user_id=user_id)
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"engine `{engine_name}` timed out after {timeout}s. "
            "script may be too large or the engine hit an infinite loop."
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
        raise RuntimeError(
            f"engine `{engine_name}` exited with code {e.returncode}.\n"
            f"```\n{stderr[-800:]}\n```"
        )
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"engine `{engine_name}` error: {e}")
    finally:
        if user_id:
            unregister_job(user_id)

    if cancel_event.is_set():
        try:
            os.unlink(output_path)
        except Exception:
            pass
        raise RuntimeError("job was cancelled.")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError(f"engine `{engine_name}` produced no output.")

    return output_path
