"""EXAMPLE ONLY (Phase 6 batch H, already applied): copy the pattern, do not rerun."""
import sys; sys.path.insert(0, '..')
from cpp_edit import edit, SRC, balance


edit("_Defines.h", """#define LEKMOD_CITY_TIMED_BUILDINGS
""", """// Batch H: Buildings.LekmodIsolatedPlotCultureCostMod/Range (Serai), LekmodSpreadCapitalReligionOnBuild and LekmodStartTurnMovesAround
// (Outremer), trait ints for the second city's building (Timurids), ocean before Astronomy and fish claims (Denmark), trade route
// religion spread (Arabia), combat in enemy territory of your religion (Jerusalem); all part of LEKMOD_CITY_TIMED_BUILDINGS /
// LEKMOD_CIV_TRAIT_FLAGS
""")

# ======================================================== trait ints
edit("CvTraitClasses.h", """	LTI_START_MELEE_PROMOTION,			// type: starting melee units get this promotion (Sioux: Scouting I)
""", """	LTI_SECOND_CITY_BUILDING,			// type: the second city founded gets this building (Timurids)
	LTI_OCEAN_WITHOUT_ASTRONOMY,		// naval and embarked units may enter Ocean before Astronomy (Denmark)
	LTI_FOUND_CLAIM_RESOURCE,			// type: founding a city claims tiles with this resource ... (Denmark: Fish)
	LTI_FOUND_CLAIM_RESOURCE_RANGE,		// ... within this range
	LTI_TRADE_ROUTE_RELIGION_SPREAD,	// trade routes to own cities and City-States spread the origin's religion like a prophet (Arabia)
	LTI_RELIGIOUS_ENEMY_TERRITORY_COMBAT,	// % combat strength inside enemy cities' territory that follow your religion (Jerusalem)
""")
edit("CvTraitClasses.cpp", """			"LekmodStartTurnFounderMoves", "LekmodStartMeleePromotion" };""", """			"LekmodStartTurnFounderMoves", "LekmodStartMeleePromotion", "LekmodSecondCityBuilding", "LekmodOceanWithoutAstronomy",
			"LekmodFoundClaimResource", "LekmodFoundClaimResourceRange", "LekmodTradeRouteReligionSpread", "LekmodReligiousEnemyTerritoryCombat" };""", mode="replace")
edit("CvTraitClasses.cpp", """			true, false, false, true };""", """			true, false, false, true, true, false, true, false, false, false };""", mode="replace")

# ======================================================== Denmark: ocean before Astronomy
edit("CvPlayer.cpp", """	if(m_pTraits)
	{
		if(m_pTraits->IsEmbarkedAllWater())
		{
			return (PromotionTypes)GC.getPROMOTION_ALLWATER_EMBARKATION();
		}
	}
""", """#ifdef LEKMOD_CIV_TRAIT_FLAGS
	if(m_pTraits && m_pTraits->GetLekmodTraitInt(LTI_OCEAN_WITHOUT_ASTRONOMY) > 0)
	{
		return (PromotionTypes)GC.getPROMOTION_ALLWATER_EMBARKATION();
	}
#endif
""")
edit("CvUnit.cpp", """	// Strip off Ocean Impassable promotion because of trait?
	if(kPlayer.GetPlayerTraits()->IsEmbarkedAllWater())""", """	// Strip off Ocean Impassable promotion because of trait?
#ifdef LEKMOD_CIV_TRAIT_FLAGS
	if(kPlayer.GetPlayerTraits()->IsEmbarkedAllWater() || kPlayer.GetPlayerTraits()->GetLekmodTraitInt(LTI_OCEAN_WITHOUT_ASTRONOMY) > 0)
#else
	if(kPlayer.GetPlayerTraits()->IsEmbarkedAllWater())
#endif""", mode="replace")

# ======================================================== found(): Denmark fish claims, Timurid second city building
edit("CvPlayer.cpp", """	// Spain: founding a city other than the first reveals the area and gives a free unit
	if (getNumCities() > 1)
	{""", """	// Denmark: claim tiles with a resource (Fish) within a range
	{
		const int eClaimResource = GetPlayerTraits()->GetLekmodTraitType(LTI_FOUND_CLAIM_RESOURCE);
		const int iClaimRange = GetPlayerTraits()->GetLekmodTraitInt(LTI_FOUND_CLAIM_RESOURCE_RANGE);
		for (int iDX = -iClaimRange; iDX <= iClaimRange && eClaimResource != -1; iDX++)
		{
			for (int iDY = -iClaimRange; iDY <= iClaimRange; iDY++)
			{
				CvPlot* pClaimPlot = plotXYWithRangeCheck(iX, iY, iDX, iDY, iClaimRange);
				if (pClaimPlot && pClaimPlot->getOwner() == NO_PLAYER && pClaimPlot->getResourceType(getTeam()) == (ResourceTypes)eClaimResource)
					pCity->DoAcquirePlot(pClaimPlot->getX(), pClaimPlot->getY());
			}
		}
	}
	// Timurids: the second city gets a building
	if (getNumCities() == 2 && GetPlayerTraits()->GetLekmodTraitType(LTI_SECOND_CITY_BUILDING) != -1)
		pCity->GetCityBuildings()->SetNumRealBuilding((BuildingTypes)GetPlayerTraits()->GetLekmodTraitType(LTI_SECOND_CITY_BUILDING), 1);
""", mode="before")

# ======================================================== Arabia: trade routes spread religion
edit("CvTradeClasses.cpp", """		if (bConnectedToArabs && bConnectedToPersia && bConnectedToMongols && bConnectedToChina && bConnectedToIndia)
		{
			gDLL->UnlockAchievement(ACHIEVEMENT_XP2_29);
		}
	}

	return true;
}""", """		if (bConnectedToArabs && bConnectedToPersia && bConnectedToMongols && bConnectedToChina && bConnectedToIndia)
		{
			gDLL->UnlockAchievement(ACHIEVEMENT_XP2_29);
		}
	}

#ifdef LEKMOD_CIV_TRAIT_FLAGS
	// Arabia: a route to an own city or a City-State spreads the origin city's religion there like a Great Prophet
	if (pOriginCity && pDestCity && m_pPlayer->GetPlayerTraits()->GetLekmodTraitInt(LTI_TRADE_ROUTE_RELIGION_SPREAD) > 0
		&& (pDestCity->getOwner() == pOriginCity->getOwner() || GET_PLAYER(pDestCity->getOwner()).isMinorCiv()))
	{
		const ReligionTypes eOriginReligion = pOriginCity->GetCityReligions()->GetReligiousMajority();
		if (eOriginReligion > RELIGION_PANTHEON)
			pDestCity->LekmodProphetSpread(eOriginReligion, m_pPlayer->GetID());
	}
#endif

	return true;
}""", mode="replace")
edit("CvCity.h", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
	void LekmodOnBuildingAdded(const CvBuildingEntry* pkBuilding);""", """#ifdef LEKMOD_CIV_TRAIT_FLAGS
	void LekmodProphetSpread(ReligionTypes eReligion, PlayerTypes eResponsiblePlayer);
#endif
""", mode="before")
edit("CvCity.cpp", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
//	--------------------------------------------------------------------------------
/// A building was added: start its timed dummy building and/or We Love the King Day (turn columns are standard speed)""", """#ifdef LEKMOD_CIV_TRAIT_FLAGS
//	--------------------------------------------------------------------------------
/// Spread a religion here with the strength of a Great Prophet (Arabia's trade routes, Outremer)
void CvCity::LekmodProphetSpread(ReligionTypes eReligion, PlayerTypes eResponsiblePlayer)
{
	if (eReligion <= RELIGION_PANTHEON)
		return;
	const UnitTypes eProphet = (UnitTypes)GC.getInfoTypeForString("UNIT_PROPHET", true);
	const int iStrength = (eProphet != NO_UNIT && GC.getUnitInfo(eProphet)) ? GC.getUnitInfo(eProphet)->GetReligiousStrength() : 1000;
	GetCityReligions()->AddProphetSpread(eReligion, GC.getRELIGION_MISSIONARY_PRESSURE_MULTIPLIER() * iStrength, eResponsiblePlayer);
}
#endif
""", mode="before")

# ======================================================== Outremer: spread on build, moves around (via a 1-turn dummy)
edit("CvBuildingClasses.h", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
	int GetLekmodTimedBuilding() const;""", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
	bool IsLekmodSpreadCapitalReligionOnBuild() const;
	int GetLekmodStartTurnMovesAround() const;
	int GetLekmodIsolatedPlotCultureCostMod() const;
	int GetLekmodIsolatedRange() const;
	int GetLekmodTimedBuilding() const;""", mode="replace")
edit("CvBuildingClasses.h", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
	int m_iLekmodTimedBuilding;""", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
	bool m_bLekmodSpreadCapitalReligionOnBuild;
	int m_iLekmodStartTurnMovesAround;
	int m_iLekmodIsolatedPlotCultureCostMod;
	int m_iLekmodIsolatedRange;
	int m_iLekmodTimedBuilding;""", mode="replace")
edit("CvBuildingClasses.cpp", """	m_iLekmodTimedBuilding = GC.getInfoTypeForString(kResults.GetText("LekmodTimedBuilding"), true);
""", """	m_bLekmodSpreadCapitalReligionOnBuild = kResults.GetBool("LekmodSpreadCapitalReligionOnBuild");
	m_iLekmodStartTurnMovesAround = kResults.GetInt("LekmodStartTurnMovesAround");
	m_iLekmodIsolatedPlotCultureCostMod = kResults.GetInt("LekmodIsolatedPlotCultureCostMod");
	m_iLekmodIsolatedRange = kResults.GetInt("LekmodIsolatedRange");
""", mode="before")
edit("CvBuildingClasses.cpp", """/// A dummy building the city gets for GetLekmodTimedBuildingTurns() (standard speed) turns after this one is built (Jongmyo: Jaegye)""", """/// When built, spread the capital's religion here like a Great Prophet (Outremer)
bool CvBuildingEntry::IsLekmodSpreadCapitalReligionOnBuild() const
{
	return m_bLekmodSpreadCapitalReligionOnBuild;
}
/// Units starting the turn in or next to the city get extra moves (Outremer's 1-turn dummy)
int CvBuildingEntry::GetLekmodStartTurnMovesAround() const
{
	return m_iLekmodStartTurnMovesAround;
}
/// % plot culture cost while no other building of this class of the owner is within GetLekmodIsolatedRange() (Serai)
int CvBuildingEntry::GetLekmodIsolatedPlotCultureCostMod() const
{
	return m_iLekmodIsolatedPlotCultureCostMod;
}
int CvBuildingEntry::GetLekmodIsolatedRange() const
{
	return m_iLekmodIsolatedRange;
}
""", mode="before")
edit("CvCity.cpp", """	if (pkBuilding->GetLekmodWLTKDTurnsOnBuild() > 0)
	{""", """#ifdef LEKMOD_CIV_TRAIT_FLAGS
	if (pkBuilding->IsLekmodSpreadCapitalReligionOnBuild() && GET_PLAYER(getOwner()).getCapitalCity() != NULL)
		LekmodProphetSpread(GET_PLAYER(getOwner()).getCapitalCity()->GetCityReligions()->GetReligiousMajority(), getOwner());
#endif
""", mode="before")
edit("CvPlayer.cpp", """		// Maurya: workers starting the turn on a road or railroad""", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
		// Outremer: units starting the turn in or next to a city with the (1-turn) muster building
		if (pLoopUnit->plot() && pLoopUnit->getDomainType() != DOMAIN_AIR)
		{
			int iAround = 0;
			for (int iDirection = -1; iDirection < NUM_DIRECTION_TYPES; iDirection++)
			{
				CvPlot* pNear = (iDirection < 0) ? pLoopUnit->plot() : plotDirection(pLoopUnit->getX(), pLoopUnit->getY(), (DirectionTypes)iDirection);
				CvCity* pNearCity = pNear ? pNear->getPlotCity() : NULL;
				if (pNearCity == NULL || pNearCity->getOwner() != GetID())
					continue;
				for (int iBuilding = 0; iBuilding < GC.getNumBuildingInfos(); iBuilding++)
				{
					CvBuildingEntry* pkBuilding = GC.getBuildingInfo((BuildingTypes)iBuilding);
					if (pkBuilding && pkBuilding->GetLekmodStartTurnMovesAround() > 0 && pNearCity->GetCityBuildings()->GetNumBuilding((BuildingTypes)iBuilding) > 0)
						iAround = std::max(iAround, pkBuilding->GetLekmodStartTurnMovesAround());
				}
			}
			if (iAround > 0)
				pLoopUnit->changeMoves(iAround * GC.getMOVE_DENOMINATOR());
		}
#endif
""", mode="before")

# ======================================================== Serai: isolated border growth
edit("CvCity.cpp", """	int iModifier = GET_PLAYER(getOwner()).GetPlotCultureCostModifier() + m_iPlotCultureCostModifier + iReligionMod;
""", """#ifdef LEKMOD_CITY_TIMED_BUILDINGS
	// Serai: cheaper tiles while no other one of the owner is within range
	for (int iBuilding = 0; iBuilding < GC.getNumBuildingInfos(); iBuilding++)
	{
		CvBuildingEntry* pkBuilding = GC.getBuildingInfo((BuildingTypes)iBuilding);
		if (pkBuilding == NULL || pkBuilding->GetLekmodIsolatedPlotCultureCostMod() == 0 || m_pCityBuildings->GetNumBuilding((BuildingTypes)iBuilding) <= 0)
			continue;
		bool bIsolated = true;
		int iCityLoop;
		for (const CvCity* pLoopCity = GET_PLAYER(getOwner()).firstCity(&iCityLoop); pLoopCity != NULL && bIsolated; pLoopCity = GET_PLAYER(getOwner()).nextCity(&iCityLoop))
		{
			if (pLoopCity != this && pLoopCity->GetCityBuildings()->GetNumBuilding((BuildingTypes)iBuilding) > 0
				&& plotDistance(getX(), getY(), pLoopCity->getX(), pLoopCity->getY()) <= pkBuilding->GetLekmodIsolatedRange())
				bIsolated = false;
		}
		if (bIsolated)
			iReligionMod += pkBuilding->GetLekmodIsolatedPlotCultureCostMod();
	}
#endif
""", mode="before")

# ======================================================== Jerusalem: combat in religious enemy territory
edit("CvUnit.cpp", """	// Gadrauht: bonus for adjacent melee/gunpowder units attacking a wounded unit""", """	// Jerusalem: inside the territory of an enemy city that follows your religion
	{
		const int iReligiousMod = GET_PLAYER(getOwner()).GetPlayerTraits()->GetLekmodTraitInt(LTI_RELIGIOUS_ENEMY_TERRITORY_COMBAT);
		const CvPlot* pMyPlot = plot();
		if (iReligiousMod != 0 && pMyPlot && pMyPlot->getOwner() != NO_PLAYER && GET_TEAM(getTeam()).isAtWar(GET_PLAYER(pMyPlot->getOwner()).getTeam()))
		{
			ReligionTypes eMyReligion = GC.getGame().GetGameReligions()->GetReligionCreatedByPlayer(getOwner());
			if (eMyReligion <= RELIGION_PANTHEON && GET_PLAYER(getOwner()).getCapitalCity() != NULL)
				eMyReligion = GET_PLAYER(getOwner()).getCapitalCity()->GetCityReligions()->GetReligiousMajority();
			const CvCity* pTerritoryCity = pMyPlot->getWorkingCity();
			if (eMyReligion > RELIGION_PANTHEON && pTerritoryCity && pTerritoryCity->GetCityReligions()->GetReligiousMajority() == eMyReligion)
			{
				iModifier += iReligiousMod;
				if (kModifierList)
				{
					GC.getGame().BuildCombatModHelpText(*kModifierList, "TXT_KEY_LEKMOD_COMBATMOD_RELIGIOUS_TERRITORY", iReligiousMod);
				}
			}
		}
	}
""", mode="before")

balance(["CvTraitClasses.h", "CvTraitClasses.cpp", "CvCity.cpp", "CvCity.h", "CvPlayer.cpp", "CvTradeClasses.cpp", "CvUnit.cpp", "CvBuildingClasses.h", "CvBuildingClasses.cpp", "_Defines.h"])
print("all done")
