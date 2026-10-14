"""Byte-safe edits for the DLL sources (keeps CRLF and non-UTF-8 bytes).
usage from python: from cpp_edit import edit; edit(path, anchor, text, mode='after'|'before'|'replace', count=1)
Anchors and texts are written with \n; they are converted to the file's line ending.
"""
import os
SRC = r"C:/Users/bbruno/civ-tools/lek/LEKMOD_DLL/CvGameCoreDLL_Expansion2/"

def edit(name, anchor, text, mode="after", count=1):
    p = name if os.path.isabs(name) else SRC + name
    b = open(p, "rb").read()
    crlf = b.count(b"\r\n") > b.count(b"\n") // 2
    s = b.decode("latin-1")
    nl = "\r\n" if crlf else "\n"
    a = anchor.replace("\n", nl)
    t = text.replace("\n", nl)
    n = s.count(a)
    if n != count:
        raise SystemExit(f"{name}: anchor found {n}x (expected {count}): {anchor[:80]!r}")
    if mode == "after":
        s = s.replace(a, a + t)
    elif mode == "before":
        s = s.replace(a, t + a)
    elif mode == "replace":
        s = s.replace(a, t)
    else:
        raise SystemExit("bad mode")
    open(p, "wb").write(s.encode("latin-1"))
    print(f"ok {name} ({mode})")

def balance(files):
    """Every touched file must have as many #if as #endif (an anchor ending in #endif once left an extra one: C1070)."""
    for f in files:
        d = 0
        for l in open(SRC + f, encoding="latin-1"):
            s = l.strip()
            if s.startswith("#if"): d += 1
            elif s.startswith("#endif"): d -= 1
        assert d == 0, (f, d)
    print("balanced", files)
