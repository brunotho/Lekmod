import sqlite3,os,re,subprocess,sys
c=sqlite3.connect(os.path.expanduser("~/Documents/My Games/Sid Meier's Civilization 5/cache/Civ5DebugDatabase.db"))
known=set()
for (t,) in c.execute("select name from sqlite_master where type='table'"):
    cols=[r[1] for r in c.execute(f'pragma table_info("{t}")')]
    if 'Type' in cols: known|={r[0] for r in c.execute(f'select Type from "{t}"')}
known|={r[0] for r in c.execute("select Atlas from IconTextureAtlases")}
diff=subprocess.run(['git','-C','C:/Users/bbruno/civ-tools/lek','diff','-U0',sys.argv[1] if len(sys.argv)>1 else 'HEAD','--','LEKMOD/Override/CIV5Units.xml'],capture_output=True,text=True).stdout
added=[l[1:] for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++')]
toks=set()
for l in added:
    if l.strip().startswith('<!--'): continue
    toks|=set(re.findall(r'\b(?:UNIT|PROMOTION|BUILDING|BUILDINGCLASS|UNITCLASS|TECH|TRAIT|IMPROVEMENT|RESOURCE|YIELD|DOMAIN|FLAVOR|ERA|CIVILIZATION|UNITCOMBAT|FEATURE|TERRAIN|GREAT_WORK_SLOT|LEKMOD)_[A-Z0-9_]+\b',l))
new={t for l in added for t in re.findall(r'<Type>([A-Z0-9_]+)</Type>',l)} | {t for l in added for t in re.findall(r'<Atlas>([A-Z0-9_]+)</Atlas>',l)}
missing=sorted(t for t in toks if t not in known and t not in new)
print('missing:',missing)
