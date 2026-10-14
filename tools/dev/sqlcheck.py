"""Prepares every SQL query of the DLL (PrepareResults / prepared strings in CacheResults) against the schema of
CIV5Units.xml, so errors like "ambiguous column name" (crash before the main menu, 2026-10-14) show up before a game start.
Schema: every <Table> in CIV5Units.xml; tables defined elsewhere come from the cached Civ5DebugDatabase.db.
Usage: python tools/dev/sqlcheck.py   (prints only queries that fail)"""
import os, re, sqlite3, glob
import xml.etree.ElementTree as ET

REPO = r"C:/Users/bbruno/civ-tools/lek"
SRC = REPO + "/LEKMOD_DLL/CvGameCoreDLL_Expansion2/"
CACHE = os.path.expanduser("~/Documents/My Games/Sid Meier's Civilization 5/cache/Civ5DebugDatabase.db")

db = sqlite3.connect(":memory:")
defined = set()
for t in ET.parse(REPO + "/LEKMOD/Override/CIV5Units.xml").getroot().iter("Table"):
    cols = [c.get("name") for c in t.iter("Column")]
    if t.get("name") in defined or not cols:
        continue
    defined.add(t.get("name"))
    db.execute('create table "%s" (%s)' % (t.get("name"), ", ".join('"%s"' % c for c in cols)))
cache = sqlite3.connect(CACHE)
for name, sql in cache.execute("select name, sql from sqlite_master where type='table'"):
    if name not in defined and sql:
        try:
            db.execute(sql)
        except sqlite3.Error:
            pass

bad = 0
for path in glob.glob(SRC + "*.cpp"):
    text = open(path, encoding="latin-1").read()
    for m in re.finditer(r'PrepareResults\(\s*\w+\s*,((?:\s*"(?:[^"\\]|\\.)*")+)', text):
        sql = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)))
        try:
            db.execute("explain " + sql, [None] * sql.count("?"))
        except sqlite3.Error as e:
            bad += 1
            line = text.count("\n", 0, m.start()) + 1
            print("%s:%d: %s\n    %s" % (os.path.basename(path), line, e, sql[:200]))
print("queries with errors:", bad)
