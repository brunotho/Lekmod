"""Checks that every <Row>/<Update> added to CIV5Units.xml by the given commits is in the loaded DB.
Usage: python verify_commits.py <commit> [...]"""
import os, re, sqlite3, subprocess, sys
import xml.etree.ElementTree as ET
REPO = "C:/Users/bbruno/civ-tools/lek"
F = "LEKMOD/Override/CIV5Units.xml"
c = sqlite3.connect(os.path.expanduser("~/Documents/My Games/Sid Meier's Civilization 5/cache/Civ5DebugDatabase.db"))
SKIP = {"GameData", "Row", "Update", "Where", "Set", "Delete", "Replace", "Table", "Column"}


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, encoding="utf-8").stdout


def norm(v):
    if v is None:
        return None
    v = str(v).strip()
    if v.lower() == "true":
        return "1"
    if v.lower() == "false":
        return "0"
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return v


ok = bad = 0
for commit in sys.argv[1:]:
    lines = git("show", commit + ":" + F).splitlines()
    diff = git("diff", "-U0", commit + "~1", commit, "--", F)
    blocks = []
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", diff, re.M):
        start, n = int(m.group(1)), int(m.group(2) or 1)
        if n:
            blocks.append((start, n))
    for start, n in blocks:
        text = "\n".join(lines[start - 1:start - 1 + n])
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        # table context: nearest preceding open tag that is a table name
        table = None
        for i in range(start - 2, -1, -1):
            mm = re.match(r"\s*<([A-Za-z_0-9]+)>\s*$", lines[i])
            if mm and mm.group(1) not in SKIP:
                table = mm.group(1)
                break
        # split into top-level elements, tracking table open tags inside the block
        for el in re.finditer(r"<(Row|Update)\b.*?</\1>|<Row\b[^>]*/>|<([A-Za-z_0-9]+)>\s*$", text, re.S | re.M):
            if el.group(2):
                if el.group(2) not in SKIP:
                    table = el.group(2)
                continue
            try:
                node = ET.fromstring(el.group(0))
            except ET.ParseError:
                continue
            if node.tag == "Row":
                vals = dict(node.attrib)
                vals.update({ch.tag: ch.text for ch in node})
                if not vals:
                    continue
                where = " and ".join('"%s" is ?' % k for k in vals)
                try:
                    hit = c.execute('select count(*) from "%s" where %s' % (table, where), [None] * len(vals)).fetchone()
                    rows = c.execute('select * from "%s"' % table).fetchall()
                    cols = [d[0] for d in c.execute('select * from "%s" limit 0' % table).description]
                except sqlite3.Error as e:
                    bad += 1
                    print("ERR", commit, table, e)
                    continue
                want = {k: norm(v) for k, v in vals.items()}
                found = any(all(norm(r[cols.index(k)]) == v for k, v in want.items() if k in cols) for r in rows)
                missing_cols = [k for k in want if k not in cols]
                if found and not missing_cols:
                    ok += 1
                else:
                    bad += 1
                    print("ROW", commit, table, want, "missing cols" if missing_cols else "", missing_cols)
            else:
                w = node.find("Where")
                s = node.find("Set")
                if w is None or s is None:
                    continue
                wa = dict(w.attrib)
                sa = dict(s.attrib)
                sa.update({ch.tag: ch.text for ch in s})
                try:
                    q = 'select %s from "%s" where %s' % (", ".join('"%s"' % k for k in sa), table, " and ".join('"%s" = ?' % k for k in wa))
                    got = c.execute(q, list(wa.values())).fetchall()
                except sqlite3.Error as e:
                    bad += 1
                    print("ERR", commit, table, wa, e)
                    continue
                exp = tuple(norm(v) for v in sa.values())
                if got and all(tuple(norm(x) for x in r) == exp for r in got):
                    ok += 1
                else:
                    bad += 1
                    print("UPD", commit, table, wa, "want", dict(zip(sa, exp)), "got", got[:3])
print("ok", ok, "mismatch", bad)
