import sqlite3,os,sys
c=sqlite3.connect(os.path.expanduser("~/Documents/My Games/Sid Meier's Civilization 5/cache/Localization-Merged.db"))
for t in sys.argv[1:]:
    op = 'like' if '%' in t else '='
    for r in c.execute(f"select Tag,Text from LocalizedText where Language='en_US' and Tag {op} ?", (t,)): print(r[0], '=>', r[1]); print()
