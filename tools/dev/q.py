import sqlite3,os,sys
c=sqlite3.connect(os.path.expanduser("~/Documents/My Games/Sid Meier's Civilization 5/cache/Civ5DebugDatabase.db"))
for q in sys.argv[1:]:
    cur=c.execute(q); 
    print('#',q); print([d[0] for d in cur.description])
    for r in cur.fetchall(): print(r)
