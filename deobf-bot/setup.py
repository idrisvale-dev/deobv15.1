"""
setup.py — extract all deobfuscator ZIPs into vendor/
Run this once after uploading the ZIP/RAR files to the same directory as this script.
"""
import zipfile
import os
import sys
import shutil
import ctypes

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR  = os.path.join(SCRIPT_DIR, "vendor")

# (zip_filename, extraction_dest_name)
ZIP_MAP = {
    "luraph-v15-v14_x-deobfuscator-main.zip": "luraph_v15zip",
    "hercules-deobfuscator-main.zip":           "hercules",
    "MoonsecDeobfuscator-master.zip":           "moonsec",
    "77fuscatorDeobfuscator-main.zip":          "77fuscator",
    "ClydeDeobfuscator-main.zip":               "clyde",
    "FlowAuth-Deobfuscator-main.zip":           "flowauth",
    "Ironveil-Deobfuscator-V1-main.zip":        "ironveil",
    "LuaObfuscator-Deobfuscator-main.zip":      "luaobfuscator",
    "Prometheus-Deobfuscator-main.zip":         "prometheus",
    "centurion-deobfuscator.zip":               "centurion",
    "Luast-main.zip":                           "luast",
    "ib2-deobf.zip":                            "ib2bot",
}

RAR_MAP = {
    "Luraph_v15_1_Deobfuscator_Fixed_All_Errors_1.rar": "luraph_v151",
}


def extract_zip(zip_path, dest):
    print(f"  extracting {os.path.basename(zip_path)} -> {dest}")
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        # strip top-level directory from paths
        members = zf.namelist()
        prefix  = members[0].split("/")[0] + "/" if "/" in members[0] else ""
        for member in members:
            target = os.path.join(dest, member[len(prefix):]) if prefix else os.path.join(dest, member)
            if member.endswith("/"):
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())


def extract_rar_libarchive(rar_path, dest):
    """Extract RAR5 using libarchive ctypes (no unrar needed)."""
    print(f"  extracting {os.path.basename(rar_path)} -> {dest} (libarchive)")
    os.makedirs(dest, exist_ok=True)

    lib = ctypes.cdll.LoadLibrary("libarchive.so.13")
    lib.archive_read_new.restype                 = ctypes.c_void_p
    lib.archive_read_support_filter_all.argtypes = [ctypes.c_void_p]
    lib.archive_read_support_format_all.argtypes = [ctypes.c_void_p]
    lib.archive_read_open_filename.argtypes      = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.archive_read_next_header.argtypes        = [ctypes.c_void_p, ctypes.c_void_p]
    lib.archive_entry_pathname.argtypes          = [ctypes.c_void_p]
    lib.archive_entry_pathname.restype           = ctypes.c_char_p
    lib.archive_entry_size.argtypes              = [ctypes.c_void_p]
    lib.archive_entry_size.restype               = ctypes.c_int64
    lib.archive_entry_filetype.argtypes          = [ctypes.c_void_p]
    lib.archive_entry_filetype.restype           = ctypes.c_uint
    lib.archive_read_data.argtypes               = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    lib.archive_read_data.restype                = ctypes.c_ssize_t
    lib.archive_read_free.argtypes               = [ctypes.c_void_p]

    a = lib.archive_read_new()
    lib.archive_read_support_filter_all(a)
    lib.archive_read_support_format_all(a)
    lib.archive_read_open_filename(a, rar_path.encode(), 10240)

    entry_p = ctypes.c_void_p()
    ARCHIVE_OK = 0

    # detect common prefix to strip
    names = []
    while True:
        ret = lib.archive_read_next_header(a, ctypes.byref(entry_p))
        if ret != ARCHIVE_OK:
            break
        names.append(lib.archive_entry_pathname(entry_p.value).decode())
    lib.archive_read_free(a)

    prefix = ""
    if names:
        first = names[0]
        if "/" in first:
            prefix = first.split("/")[0] + "/"

    # second pass: extract
    a = lib.archive_read_new()
    lib.archive_read_support_filter_all(a)
    lib.archive_read_support_format_all(a)
    lib.archive_read_open_filename(a, rar_path.encode(), 10240)

    while True:
        ret = lib.archive_read_next_header(a, ctypes.byref(entry_p))
        if ret != ARCHIVE_OK:
            break
        name = lib.archive_entry_pathname(entry_p.value).decode()
        size = lib.archive_entry_size(entry_p.value)
        stripped = name[len(prefix):] if prefix and name.startswith(prefix) else name
        target = os.path.join(dest, stripped)

        if not stripped or stripped.endswith("/") or size == 0:
            os.makedirs(target.rstrip("/"), exist_ok=True)
            continue

        os.makedirs(os.path.dirname(target), exist_ok=True)
        buf = ctypes.create_string_buffer(size)
        lib.archive_read_data(a, buf, size)
        with open(target, "wb") as f:
            f.write(buf.raw)

    lib.archive_read_free(a)


def main():
    print("deobf-bot vendor setup")
    print(f"vendor dir: {VENDOR_DIR}")
    print()

    # look for archives next to this script or in CWD
    search_dirs = [SCRIPT_DIR, os.getcwd()]

    errors = []
    for filename, dest_name in ZIP_MAP.items():
        dest = os.path.join(VENDOR_DIR, dest_name)
        found = None
        for d in search_dirs:
            candidate = os.path.join(d, filename)
            if os.path.exists(candidate):
                found = candidate
                break
        if not found:
            print(f"  SKIP {filename} (not found — upload it alongside this script)")
            errors.append(filename)
            continue
        extract_zip(found, dest)

    for filename, dest_name in RAR_MAP.items():
        dest = os.path.join(VENDOR_DIR, dest_name)
        found = None
        for d in search_dirs:
            candidate = os.path.join(d, filename)
            if os.path.exists(candidate):
                found = candidate
                break
        if not found:
            print(f"  SKIP {filename} (not found — upload it alongside this script)")
            errors.append(filename)
            continue
        extract_rar_libarchive(found, dest)

    print()
    if errors:
        print(f"missing {len(errors)} archive(s). upload them and re-run setup.py.")
    else:
        print("all archives extracted. run `python main.py` to start the bot.")


if __name__ == "__main__":
    main()
