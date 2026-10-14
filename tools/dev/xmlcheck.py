import xml.etree.ElementTree as ET, collections
base = r"C:/Users/bbruno/civ-tools/lek/LEKMOD/Override/"
for f in ("CIV5Units.xml", "CIV5Units_Mongol.xml"):
    root = ET.parse(base + f).getroot()
    bad = 0
    for row in root.iter('Row'):
        c = collections.Counter(ch.tag for ch in row)
        d = [k for k, v in c.items() if v > 1]
        if d: bad += 1; print(f, 'dup', d, row.findtext('Type') or row.get('Tag'))
    print(f, 'ok, rows with repeated columns:', bad)
root = ET.parse(base + "CIV5Units_Mongol.xml").getroot()
tags = collections.Counter(r.get('Tag') for r in root.iter('Row') if r.get('Tag'))
print('dup Row tags:', [t for t, v in tags.items() if v > 1 and 'POINT_BLANK' in t])
ids = collections.Counter(r.findtext('ID') for r in root.iter() if False)
u = ET.parse(base + "CIV5Units.xml").getroot()
for sec in u.iter('UnitPromotions'):
    i = collections.Counter(r.findtext('ID') for r in sec.findall('Row') if r.findtext('ID'))
    dd = [k for k, v in i.items() if v > 1]
    if dd: print('dup promotion IDs', dd)
