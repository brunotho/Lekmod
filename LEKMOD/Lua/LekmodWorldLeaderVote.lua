-------------------------------------------------
-- LEKMOD: World Leader vote screen
-- Opens on the turn of each World Leader vote (CvLeague::LekmodDoWorldLeaderVote, result from
-- League:LekmodGetLastLeaderVote()). Nobody chooses anything: every civilization's Delegates count for itself.
-------------------------------------------------
local g_iShownTurn = -1;

local function GetLeague()
	if (Game.GetNumActiveLeagues() <= 0) then
		return nil;
	end
	local pLeague = Game.GetActiveLeague and Game.GetActiveLeague() or Game.GetLeague(0);
	if (pLeague == nil or pLeague.LekmodGetLastLeaderVote == nil) then
		return nil;
	end
	return pLeague;
end

local function Close()
	UIManager:DequeuePopup(ContextPtr);
end
Controls.CloseButton:RegisterCallback(Mouse.eLClick, Close);

ContextPtr:SetInputHandler(function(uiMsg, wParam, lParam)
	if (uiMsg == KeyEvents.KeyDown and (wParam == Keys.VK_ESCAPE or wParam == Keys.VK_RETURN)) then
		Close();
		return true;
	end
end);

local function Show(last)
	local iActivePlayer = Game.GetActivePlayer();
	Controls.Intro:SetText(Locale.Lookup("TXT_KEY_LEKMOD_WL_INTRO", last.Turn, last.Needed));

	-- one line per civilization, most Delegates first; yours highlighted
	local strVotes = "";
	local iFirst, iNumFirst = -1, 0;
	for i, v in ipairs(last.Votes) do
		if (i == 1) then
			iFirst = v.Delegates;
		end
		if (v.Delegates == iFirst) then
			iNumFirst = iNumFirst + 1;
		end
		local strLine = Locale.Lookup("TXT_KEY_LEKMOD_WORLD_LEADER_VOTE_LINE", Players[v.Player]:GetCivilizationShortDescriptionKey(), v.Delegates);
		if (v.Player == iActivePlayer) then
			strLine = "[COLOR_POSITIVE_TEXT]" .. strLine .. "[ENDCOLOR]";
		end
		if (strVotes ~= "") then
			strVotes = strVotes .. "[NEWLINE]";
		end
		strVotes = strVotes .. strLine;
	end
	Controls.Votes:SetText(strVotes);

	if (iNumFirst == 1 and iFirst >= last.Needed) then
		Controls.Result:SetText(Locale.Lookup("TXT_KEY_LEKMOD_WL_RESULT_WIN", Players[last.Votes[1].Player]:GetCivilizationShortDescriptionKey(), iFirst));
	else
		Controls.Result:SetText(Locale.Lookup("TXT_KEY_LEKMOD_WL_RESULT_NONE", last.Needed));
	end

	Controls.Content:CalculateSize();
	Controls.Content:ReprocessAnchoring();
	local width, height = Controls.Content:GetSizeVal();
	Controls.Frame:SetSizeVal(560, height + 90);
	UIManager:QueuePopup(ContextPtr, PopupPriority.VoteResults);
end

-- the vote is counted while the turn starts; open the screen once per vote
local function CheckForNewVote()
	local pLeague = GetLeague();
	if (pLeague == nil) then
		return;
	end
	local last = pLeague:LekmodGetLastLeaderVote();
	if (last.Turn == nil or last.Turn ~= Game.GetGameTurn() or last.Turn == g_iShownTurn) then
		return;
	end
	g_iShownTurn = last.Turn;
	Show(last);
end
Events.ActivePlayerTurnStart.Add(CheckForNewVote);
Events.SerialEventLeagueScreenDirty.Add(CheckForNewVote);

ContextPtr:SetHide(true);
