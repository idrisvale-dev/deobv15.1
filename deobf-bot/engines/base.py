"""
Shared subprocess helper for all engine wrappers.
Handles cancel_event so .cancel works from the bot.
"""
import subprocess
import threading
import os


def popen_run(
    cmd: list,
    cwd: str,
    timeout: int,
    cancel_event: threading.Event = None,
    user_id: int = 0,
    env: dict = None,
):
    """
    Runs cmd as a subprocess. If cancel_event is set mid-run, kills the process.
    Raises subprocess.TimeoutExpired or subprocess.CalledProcessError on failure.
    """
    # lazy import to avoid circular
    try:
        from runner import set_job_proc
    except ImportError:
        set_job_proc = None

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        env=env or os.environ.copy(),
    )

    if set_job_proc and user_id:
        set_job_proc(user_id, proc)

    # poll with cancel check
    import time
    deadline = time.time() + timeout
    while True:
        try:
            stdout, stderr = proc.communicate(timeout=1)
            break
        except subprocess.TimeoutExpired:
            if cancel_event and cancel_event.is_set():
                proc.kill()
                proc.communicate()
                return  # caller checks cancel_event after return
            if time.time() >= deadline:
                proc.kill()
                proc.communicate()
                raise subprocess.TimeoutExpired(cmd, timeout)

    if proc.returncode != 0:
        raise subprocess.CalledProcessError(
            proc.returncode,
            cmd,
            output=stdout,
            stderr=stderr,
        )
