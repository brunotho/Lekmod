import re
P = r"C:/Users/bbruno/civ-tools/lek/LEKMOD/Override/CIV5Units.xml"

def atlas(name, file):
    rows = []
    for s in (256, 214, 128, 80, 64, 45, 32):
        rows.append(f"""		<Row>
			<Atlas>{name}</Atlas>
			<IconSize>{s}</IconSize>
			<Filename>{file}_{s}.dds</Filename>
			<IconsPerRow>1</IconsPerRow>
			<IconsPerColumn>1</IconsPerColumn>
		</Row>""")
    return "\n".join(rows)

def res(unit, *pairs):
    s = f'\t<Unit_ResourceQuantityRequirements>\n\t\t<Delete UnitType="{unit}"/>\n'
    for r, n in pairs:
        s += f"\t\t<Row>\n\t\t\t<UnitType>{unit}</UnitType>\n\t\t\t<ResourceType>RESOURCE_{r}</ResourceType>\n\t\t\t<Cost>{n}</Cost>\n\t\t</Row>\n"
    return s + "\t</Unit_ResourceQuantityRequirements>\n"

def promos(unit, add=(), remove=(), remove_all=False):
    s = "\t<Unit_FreePromotions>\n"
    if remove_all:
        s += f'\t\t<Delete UnitType="{unit}"/>\n'
    for p in remove:
        s += f'\t\t<Delete UnitType="{unit}" PromotionType="PROMOTION_{p}"/>\n'
    for p in add:
        s += f"\t\t<Row>\n\t\t\t<UnitType>{unit}</UnitType>\n\t\t\t<PromotionType>PROMOTION_{p}</PromotionType>\n\t\t</Row>\n"
    return s + "\t</Unit_FreePromotions>\n"

def upd(table, where, sets):
    w = " ".join(f'{k}="{v}"' for k, v in where.items())
    st = " ".join(f'{k}="{v}"' for k, v in sets.items())
    return f"\t<{table}>\n\t\t<Update>\n\t\t\t<Where {w}/>\n\t\t\t<Set {st}/>\n\t\t</Update>\n\t</{table}>\n"

def unit(u, **sets):
    return upd("Units", {"Type": u}, sets)

def upgrade(u, cls):
    return f"\t<Unit_ClassUpgrades>\n\t\t<Delete UnitType=\"{u}\"/>\n\t\t<Row>\n\t\t\t<UnitType>{u}</UnitType>\n\t\t\t<UnitClassType>{cls}</UnitClassType>\n\t\t</Row>\n\t</Unit_ClassUpgrades>\n"

def rows(table, *dicts, delete=None):
    s = f"\t<{table}>\n"
    if delete:
        s += "\t\t<Delete " + " ".join(f'{k}="{v}"' for k, v in delete.items()) + "/>\n"
    for d in dicts:
        s += "\t\t<Row>\n" + "".join(f"\t\t\t<{k}>{v}</{k}>\n" for k, v in d.items()) + "\t\t</Row>\n"
    return s + f"\t</{table}>\n"

LAND = ["MELEE", "ARCHER", "RECON", "MOUNTED", "MOUNTED_RANGED", "SIEGE", "GUN", "ARMOR", "PARADROPPER", "HELICOPTER"]

def dummy(bid, cid, btype, ctype, desc, **extra):
    """A hidden dummy building with its own class (Cost -1, never captured unless extra overrides it)."""
    s = rows("BuildingClasses", {"ID": cid, "Type": ctype, "DefaultBuilding": btype, "MaxGlobalInstances": -1,
                                 "MaxTeamInstances": -1, "MaxPlayerInstances": -1, "ExtraPlayerInstances": 0,
                                 "NoLimit": "false", "Monument": "false"})
    d = {"ID": bid, "Type": btype, "BuildingClass": ctype, "Description": desc, "Civilopedia": "Trait",
         "Strategy": "Trait", "Help": "Trait", "NeverCapture": "true", "NukeImmune": "true", "Cost": -1,
         "HurryCostModifier": -1, "ArtDefineTag": "MONUMENT", "GreatWorkCount": -1, "PortraitIndex": 2, "IconAtlas": "LEKMOD_AKKAD_ATLAS"}
    d.update(extra)
    return s + rows("Buildings", d)
