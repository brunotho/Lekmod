-- Author: EnormousApplePie

include("Lekmod_utilities.lua")
include("FLuaVector.lua")

local this_civ = GameInfoTypes["CIVILIZATION_NEW_ZEALAND"]
local is_active = LekmodUtilities:is_civilization_active(this_civ)

------------------------------------------------------------------------------------------------------------------------
-- New Zealand UA. Give a bonus to the player when they meet a new civ.
------------------------------------------------------------------------------------------------------------------------
function lekmod_new_zealand_ua_award_bonus(player, other_player)

   if not player:IsAlive() or player:GetCivilizationType() ~= this_civ then return end

   local rewards = {
      [1] = {reward = 10, type = "Faith", string = "[ICON_PEACE] Faith", method = "ChangeFaith"},
      [2] = {reward = 6, type = "Culture", string = "[ICON_CULTURE] Culture", method = "ChangeJONSCulture"},
      [3] = {reward = 12, type = "Science", string = "[ICON_RESEARCH] Science", method = "ChangeResearchProgress"},
      [4] = {reward = 40, type = "Gold", string = "[ICON_GOLD] Gold", method = "ChangeGold"}
   }

	local random = LekmodUtilities:get_random_between(1, 4)

   -- Science is handled on team level
   if rewards[random].method == "ChangeResearchProgress" then
      -- if the player is not currently researching anything, add the science to the overflow
      if player:GetCurrentResearch() == -1 then
         Teams[player:GetTeam()]:GetTeamTechs():ChangeResearchProgress(player:GetOverflowResearch(), rewards[random].reward, player:GetID())
      else
         Teams[player:GetTeam()]:GetTeamTechs():ChangeResearchProgress(player:GetCurrentResearch(), rewards[random].reward, player:GetID())
      end
   else
      player[rewards[random].method](player, rewards[random].reward)
   end

   if player:IsHuman() and Game.GetActivePlayer() == player:GetID() then
      local text = Locale.ConvertTextKey("TXT_KEY_NZ_MEET_BONUS", rewards[random].reward, rewards[random].string, other_player:GetName())
      Events.GameplayAlertMessage(text)
   end

end

function lekmod_new_zealand_ua_on_meet(team_met_id, player_team_id)

	local player_team = Teams[player_team_id]
	local team_met = Teams[team_met_id]
	
	local player_id = player_team:GetLeaderID()
	local met_player_id = team_met:GetLeaderID()

	lekmod_new_zealand_ua_award_bonus(Players[player_id], Players[met_player_id])
	lekmod_new_zealand_ua_award_bonus(Players[met_player_id], Players[player_id])

end
------------------------------------------------------------------------------------------------------------------------
if is_active then
	GameEvents.TeamMeet.Add(lekmod_new_zealand_ua_on_meet)
end