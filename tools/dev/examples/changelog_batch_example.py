"""EXAMPLE ONLY (Phase 6 batch H, already applied): copy the pattern, do not rerun."""
P = r"C:/Users/bbruno/civ-tools/lek/changelog.txt"
s = open(P, "rb").read().decode("utf-8")

def in_section(head, old, new):
    global s
    i = s.index(head)
    j = s.index("\n\n", i)
    sec = s[i:j + 1]
    assert sec.count(old) == 1, (head, old)
    s = s[:i] + sec.replace(old, new) + s[j + 1:]

in_section("TIMURIDS (CIVILIZATION_TIMURIDS)", "- Note: open: the Serai's faster border growth, the new UA (need C++)\n",
    "- Added: Serai: borders grow 15% faster while no other Serai is within 5 tiles\n"
    "- Changed: new UA Twin Courts: in the capital, Great Works and writer, artist and musician specialists +1 Culture +1 Gold, +10% Production towards buildings; in the second city, Great Works and those specialists +1 Science, Great Person improvements and world wonders +2 Science; both stay with their cities when captured\n"
    "- Removed: +15% Science, Culture and Gold and +5 Strength in the original capital\n"
    "- DLL: Building_LekmodLocalSpecialistYields, Traits.LekmodSecondCityBuilding (dummy 295, class 198), Buildings.LekmodIsolatedPlotCultureCostMod/Range\n")
in_section("DENMARK (CIVILIZATION_DENMARK)", "- Note: open: the new UA (needs C++)\n",
    "- Changed: new UA: all land units start with Amphibious I and pillage without spending movement; naval and embarked units may enter Ocean before Astronomy; new cities claim Fish within 2 tiles\n"
    "- Removed: +1 Movement for embarked units, the 1-movement disembark for every unit, civilians embarking for 1 movement\n"
    "- DLL: Traits.LekmodOceanWithoutAstronomy, LekmodFoundClaimResource/Range\n")
in_section("ARABIA (CIVILIZATION_ARABIA)", "- Note: open: the new UA (trade route conversion, Oasis Faith; needs C++)\n",
    "- Changed: new UA: trade routes to your own cities and City-States spread the origin city's religion like a Great Prophet; Oases +2 Faith with Calendar; double Oil kept\n"
    "- Removed: faster luxury improvements and +2 Culture +2 Gold from luxury buildings\n"
    "- DLL: Traits.LekmodTradeRouteReligionSpread\n")
in_section("JERUSALEM (CIVILIZATION_JERUSALEM)", "- Note: open: UA, Outremer religion spread and movement (need C++)\n",
    "- Added: units +15% inside the territory of an enemy city that follows your religion\n"
    "- Added: Outremer: when built, spreads the capital's religion like a Great Prophet; units in or next to the city +2 Movement for one turn\n"
    "- DLL: Traits.LekmodReligiousEnemyTerritoryCombat; Buildings.LekmodSpreadCapitalReligionOnBuild, LekmodStartTurnMovesAround (one-shot dummy 296, class 199, removed after the next unit reset)\n")
open(P, "wb").write(s.encode("utf-8"))
print("ok")
