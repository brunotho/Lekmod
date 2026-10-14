"""EXAMPLE ONLY (Phase 6 batch H, already applied): copy the pattern, do not rerun."""
import sys; sys.path.insert(0, '..')
from helpers import *

b = open(P, "rb").read().decode("utf-8")
def once(old, new):
    global b
    assert b.count(old) == 1, old
    b = b.replace(old, new)

once('\t\t<Column name="LekmodStartMeleePromotion" type="text" reference="UnitPromotions(Type)" default="NULL"/>\n',
     '\t\t<Column name="LekmodStartMeleePromotion" type="text" reference="UnitPromotions(Type)" default="NULL"/>\n'
     '\t\t<Column name="LekmodSecondCityBuilding" type="text" reference="Buildings(Type)" default="NULL"/>\n'
     '\t\t<Column name="LekmodOceanWithoutAstronomy" type="integer" default="0"/>\n'
     '\t\t<Column name="LekmodFoundClaimResource" type="text" reference="Resources(Type)" default="NULL"/>\n'
     '\t\t<Column name="LekmodFoundClaimResourceRange" type="integer" default="0"/>\n'
     '\t\t<Column name="LekmodTradeRouteReligionSpread" type="integer" default="0"/>\n'
     '\t\t<Column name="LekmodReligiousEnemyTerritoryCombat" type="integer" default="0"/>\n')
once('    \t<Column name="LekmodTrainedUnitStackMax" type="integer" default="0"/>',
     '    \t<Column name="LekmodTrainedUnitStackMax" type="integer" default="0"/>\n'
     '    \t<Column name="LekmodSpreadCapitalReligionOnBuild" type="boolean" default="false"/>\n'
     '    \t<Column name="LekmodStartTurnMovesAround" type="integer" default="0"/>\n'
     '    \t<Column name="LekmodIsolatedPlotCultureCostMod" type="integer" default="0"/>\n'
     '    \t<Column name="LekmodIsolatedRange" type="integer" default="0"/>')
once('\t<Table name="Trait_LekmodBuildingClassDefense">\n', """	<Table name="Building_LekmodLocalSpecialistYields">
		<Column name="BuildingType" type="text" reference="Buildings(Type)"/>
		<Column name="SpecialistType" type="text" reference="Specialists(Type)"/>
		<Column name="YieldType" type="text" reference="Yields(Type)"/>
		<Column name="Yield" type="integer" default="0"/>
	</Table>
	<Table name="Trait_LekmodBuildingClassDefense">
""")


WONDERS = """PYRAMID GREAT_LIBRARY STONEHENGE HANGING_GARDEN COLOSSUS GREAT_LIGHTHOUSE ORACLE GREAT_WALL HAGIA_SOPHIA ANGKOR_WAT NOTRE_DAME
MACHU_PICHU CHICHEN_ITZA KREMLIN FORBIDDEN_PALACE SISTINE_CHAPEL HIMEJI_CASTLE PORCELAIN_TOWER TAJ_MAHAL BIG_BEN BRANDENBURG_GATE LOUVRE
EIFFEL_TOWER STATUE_OF_LIBERTY CRISTO_REDENTOR PENTAGON SYDNEY_OPERA_HOUSE STATUE_ZEUS TEMPLE_ARTEMIS MAUSOLEUM_HALICARNASSUS ALHAMBRA
CN_TOWER HUBBLE LEANING_TOWER MOSQUE_OF_DJENNE NEUSCHWANSTEIN PETRA TERRACOTTA_ARMY GREAT_FIREWALL UFFIZI GLOBE_THEATER BROADWAY RED_FORT
PRORA_RESORT BOROBUDUR PARTHENON INTERNATIONAL_SPACE_STATION ALTHING LAKE_WONDER ARSENAL_OF_VENICE TOWER_OF_BELEM LEKMOD_MINISTRY_OF_TRUTH
LEKMOD_EXTRAORDINARY_SESSION""".split()
CULTURE_SPEC = ("SPECIALIST_WRITER", "SPECIALIST_ARTIST", "SPECIALIST_MUSICIAN")
GP_IMPROVEMENTS = ("SACRED_GROVE", "DOCK", "ACADEMY", "CONCERT", "CUSTOMS_HOUSE", "MANUFACTORY", "CITADEL", "LANDMARK", "HOLY_SITE")

B = ["\t<!-- Phase 6 C++ batch H (2026-10-14) -->\n"]
B.append("\t<!-- Timurids (new UA Twin Courts): capital (BUILDING_ULUG, Lua-managed capital dummy): Great Works +1 Culture +1 Gold, writer/artist/musician specialists +1 Culture +1 Gold, +10% Production towards buildings; second city (dummy 295): Great Works +1 Science, those specialists +1 Science, Great Person improvements +2 Science, world wonders +2 Science; both stay with the city when captured -->\n")
for t in ("Building_YieldModifiers", "Building_YieldChanges"):
    B.append(f"\t<{t}>\n\t\t<Delete BuildingType=\"BUILDING_ULUG\"/>\n\t</{t}>\n")
B.append(upd("Buildings", {"Type": "BUILDING_ULUG"}, {"Defense": 0, "BuildingProductionModifier": 10, "NeverCapture": "false", "ConquestProb": 100}))
B.append(rows("Building_GreatWorkYieldChanges", *[{"BuildingType": "BUILDING_ULUG", "YieldType": y, "YieldChange": 1} for y in ("YIELD_CULTURE", "YIELD_GOLD")],
    {"BuildingType": "BUILDING_LEKMOD_TIMURID_SECOND_COURT", "YieldType": "YIELD_SCIENCE", "YieldChange": 1}))
B.append(dummy(295, 198, "BUILDING_LEKMOD_TIMURID_SECOND_COURT", "BUILDINGCLASS_LEKMOD_TIMURID_SECOND_COURT", "TXT_KEY_BUILDING_LEKMOD_TIMURID_SECOND_COURT",
    NeverCapture="false", ConquestProb=100))
B.append(rows("Building_LekmodLocalSpecialistYields",
    *[{"BuildingType": "BUILDING_ULUG", "SpecialistType": s, "YieldType": y, "Yield": 1} for s in CULTURE_SPEC for y in ("YIELD_CULTURE", "YIELD_GOLD")],
    *[{"BuildingType": "BUILDING_LEKMOD_TIMURID_SECOND_COURT", "SpecialistType": s, "YieldType": "YIELD_SCIENCE", "Yield": 1} for s in CULTURE_SPEC]))
B.append(rows("Building_ImprovementYieldChanges", *[{"BuildingType": "BUILDING_LEKMOD_TIMURID_SECOND_COURT", "ImprovementType": "IMPROVEMENT_" + i,
    "YieldType": "YIELD_SCIENCE", "Yield": 2} for i in GP_IMPROVEMENTS]))
B.append(rows("Building_LekmodConditionalYields", *[{"BuildingType": "BUILDING_LEKMOD_TIMURID_SECOND_COURT", "YieldType": "YIELD_SCIENCE", "Yield": 2,
    "RequiresBuildingClass": "BUILDINGCLASS_" + w} for w in WONDERS]))
B.append(upd("Traits", {"Type": "TRAIT_ULUG"}, {"LekmodSecondCityBuilding": "BUILDING_LEKMOD_TIMURID_SECOND_COURT"}))
B.append("\t<!-- Timurids: Serai -15% tile culture cost (faster border growth) while no other Serai is within 5 tiles -->\n")
B.append(upd("Buildings", {"Type": "BUILDING_SERAI"}, {"LekmodIsolatedPlotCultureCostMod": -15, "LekmodIsolatedRange": 5}))

B.append("\t<!-- Denmark (new UA): land units Amphibious I and free pillaging; naval and embarked units may enter Ocean before Astronomy; new cities claim Fish within 2 tiles -->\n")
B.append(upd("Traits", {"Type": "TRAIT_VIKING_FURY"}, {"ExtraEmbarkMoves": 0, "EmbarkedToLandFlatCost": "false", "CiviliansEmbarkOneMove": "false",
    "LekmodOceanWithoutAstronomy": 1, "LekmodFoundClaimResource": "RESOURCE_FISH", "LekmodFoundClaimResourceRange": 2}))
B.append("\t<Trait_FreePromotionUnitCombats>\n\t\t<Delete TraitType=\"TRAIT_VIKING_FURY\"/>\n\t</Trait_FreePromotionUnitCombats>\n")
B.append(rows("Trait_FreePromotionUnitCombats", *[{"TraitType": "TRAIT_VIKING_FURY", "UnitCombatType": "UNITCOMBAT_" + c, "PromotionType": p}
    for c in LAND for p in ("PROMOTION_AMPHIBIOUS_1", "PROMOTION_FREE_PILLAGE_MOVES")]))

B.append("\t<!-- Arabia (new UA): 2x Oil kept; trade routes to own cities and City-States spread the origin's religion like a prophet; Oasis +2 Faith with Calendar -->\n")
for t in ("Trait_BuildImprovementBuildTimeOverride", "Trait_BuildingClassYieldChanges"):
    B.append(f"\t<{t}>\n\t\t<Delete TraitType=\"TRAIT_LAND_TRADE_GOLD\"/>\n\t</{t}>\n")
B.append(upd("Traits", {"Type": "TRAIT_LAND_TRADE_GOLD"}, {"LekmodTradeRouteReligionSpread": 1}))
B.append(rows("Trait_LekmodPlotYields", {"TraitType": "TRAIT_LAND_TRADE_GOLD", "YieldType": "YIELD_FAITH", "Yield": 2, "FeatureType": "FEATURE_OASIS", "TechType": "TECH_CALENDAR"}))

B.append("\t<!-- Jerusalem: +15% combat inside enemy cities' territory that follow your religion; Outremer spreads the capital's religion when built and gives +2 moves for one turn to units in or next to the city -->\n")
B.append(upd("Traits", {"Type": "TRAIT_HOLYLAND"}, {"LekmodReligiousEnemyTerritoryCombat": 15}))
B.append(dummy(296, 199, "BUILDING_LEKMOD_OUTREMER_MUSTER", "BUILDINGCLASS_LEKMOD_OUTREMER_MUSTER", "TXT_KEY_BUILDING_OUTREMER", LekmodStartTurnMovesAround=2))
B.append(upd("Buildings", {"Type": "BUILDING_OUTREMER"}, {"LekmodSpreadCapitalReligionOnBuild": "true", "FreeBuildingThisCity": "BUILDINGCLASS_LEKMOD_OUTREMER_MUSTER"}))
i = b.rindex("</GameData>")
b = b[:i] + "".join(B) + b[i:]
open(P, "wb").write(b.encode("utf-8"))
print("xml ok")

T = r"C:/Users/bbruno/civ-tools/lek/LEKMOD/Override/CIV5Units_Mongol.xml"
t = open(T, "rb").read().decode("utf-8")
NEW = {
    "TXT_KEY_BUILDING_LEKMOD_TIMURID_SECOND_COURT": "Second Court",
    "TXT_KEY_LEKMOD_COMBATMOD_RELIGIOUS_TERRITORY": "In enemy lands of your faith: {1_Num}%",
}
REPLACE = {
    "TXT_KEY_TRAIT_ULUG": "Twin Courts.[NEWLINE][NEWLINE]In the [ICON_CAPITAL] Capital: Great Works and Writer, Artist and Musician specialists yield +1 [ICON_CULTURE] Culture and +1 [ICON_GOLD] Gold; +10% [ICON_PRODUCTION] Production towards buildings.[NEWLINE][NEWLINE]In your second city: Great Works and Writer, Artist and Musician specialists yield +1 [ICON_RESEARCH] Science; Great Person improvements and World Wonders +2 [ICON_RESEARCH] Science.[NEWLINE][NEWLINE]Both courts stay with their cities, also when they are captured.",
    "TXT_KEY_BUILDING_SERAI_HELP": "Replaces the Caravansary. Available at the Wheel and cheaper.[NEWLINE]+2 [ICON_GOLD] Gold; Caravans from this city reach 50% farther and give +2 [ICON_GOLD] Gold to international routes.[NEWLINE][NEWLINE]+1 [ICON_FOOD] Food for every other Serai of yours within 4 tiles.[NEWLINE]If no other Serai of yours is within 5 tiles: +3 [ICON_CULTURE] Culture and borders grow 15% faster.",
    "TXT_KEY_TRAIT_VIKING_FURY": "Land units start with Amphibious I and pillage without spending movement.[NEWLINE]Naval and embarked units may enter Ocean tiles before Astronomy.[NEWLINE][NEWLINE]New cities claim the Fish tiles within 2 tiles.",
    "TXT_KEY_TRAIT_LAND_TRADE_GOLD2": "Double quantity of [ICON_RES_OIL] Oil.[NEWLINE]Trade routes to your own cities and to [ICON_CITY_STATE] City-States spread the origin city's [ICON_RELIGION] Religion there like a Great Prophet.[NEWLINE]Oases yield +2 [ICON_PEACE] Faith once you know [ICON_TECH_CALENDAR] Calendar.",
    "TXT_KEY_TRAIT_HOLYLAND": "+1 [ICON_PEACE] Faith from [COLOR_GREEN]Luxury Resources[ENDCOLOR].[NEWLINE][NEWLINE]Units get +15% [ICON_STRENGTH] Combat Strength inside the territory of an enemy city that follows your [ICON_RELIGION] Religion.",
    "TXT_KEY_BUILDING_OUTREMER_HELP": "Replaces the Courthouse. Eliminates extra [ICON_HAPPINESS_4] Unhappiness from an [ICON_OCCUPIED] Occupied City.[NEWLINE][NEWLINE]When built: spreads your [ICON_CAPITAL] Capital's [ICON_RELIGION] Religion here like a Great Prophet, and units in or next to the city get +2 [ICON_MOVES] Movement for one turn.",
}
out = "\t\t<!-- Phase 6 C++ batch H -->\n"
for k, v in NEW.items():
    assert f'"{k}"' not in t, k
    out += f'\t\t<Row Tag="{k}">\n\t\t\t<Text>{v}</Text>\n\t\t</Row>\n'
for k, v in REPLACE.items():
    out += f'\t\t<Replace Tag="{k}">\n\t\t\t<Text>{v}</Text>\n\t\t</Replace>\n'
t = t.replace("\t</Language_en_US>", out + "\t</Language_en_US>")
open(T, "wb").write(t.encode("utf-8"))
print("text ok")
