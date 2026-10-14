"""Dump a civ's trait, unique units/buildings/improvements from the loaded DB.
usage: python civdump.py CIVILIZATION_X [...]"""
import sqlite3, sys, os
DB = os.path.expanduser(r"~\Documents\My Games\Sid Meier's Civilization 5\cache\Civ5DebugDatabase.db")
c = sqlite3.connect(DB); c.row_factory = sqlite3.Row

def nz(row):
    return {k: row[k] for k in row.keys() if row[k] not in (None, 0, '', 'NULL')}

def subtables(prefix, key, val):
    tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table' and name like ?", (prefix + '_%',))]
    for t in tabs:
        cols = [r[1] for r in c.execute(f'pragma table_info("{t}")')]
        if key not in cols: continue
        rows = c.execute(f'select * from "{t}" where {key}=?', (val,)).fetchall()
        for r in rows: print('   ', t, nz(r))

for civ in sys.argv[1:]:
    print('=' * 20, civ)
    for r in c.execute('select * from Civilization_Leaders where CivilizationType=?', (civ,)):
        for t in c.execute('select TraitType from Leader_Traits where LeaderType=?', (r['LeaderheadType'],)):
            tr = c.execute('select * from Traits where Type=?', (t[0],)).fetchone()
            print('TRAIT', nz(tr)); subtables('Trait', 'TraitType', t[0])
    for u in c.execute('select UnitType, UnitClassType from Civilization_UnitClassOverrides where CivilizationType=?', (civ,)):
        if not u[0]: continue
        ur = c.execute('select * from Units where Type=?', (u[0],)).fetchone()
        print('UNIT', nz(ur)); subtables('Unit', 'UnitType', u[0])
    for b in c.execute('select BuildingType from Civilization_BuildingClassOverrides where CivilizationType=?', (civ,)):
        if not b[0]: continue
        br = c.execute('select * from Buildings where Type=?', (b[0],)).fetchone()
        print('BUILDING', nz(br)); subtables('Building', 'BuildingType', b[0])
    for i in c.execute('select Type from Improvements where CivilizationType=?', (civ,)):
        ir = c.execute('select * from Improvements where Type=?', (i[0],)).fetchone()
        print('IMPROVEMENT', nz(ir)); subtables('Improvement', 'ImprovementType', i[0])
