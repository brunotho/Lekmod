-------------------------------------------------
-- LEKMOD: World Leader vote screen
-- Opens on the turn of each World Leader vote (CvLeague::LekmodDoWorldLeaderVote, counts from
-- League:LekmodGetLastLeaderVote()). Nobody chooses anything: every civilization's Delegates count for itself.
-- The counts are frozen on this turn; the result applies next turn (CvLeague::LekmodResolveWorldLeaderVote),
-- so this screen announces what will happen.
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

	-- who wins, or who gains a permanent Delegate (first and second place, everyone tied counts)
	local iFirst = last.Votes[1].Delegates;
	local iNumFirst, iSecond = 0, -1;
	for _, v in ipairs(last.Votes) do
		if (v.Delegates == iFirst) then
			iNumFirst = iNumFirst + 1;
		elseif (iSecond < 0) then
			iSecond = v.Delegates;
		end
	end
	local bWinner = (iNumFirst == 1 and iFirst >= last.Needed);

	-- one line per civilization, most Delegates first: winner or Delegate gainers in green, yours with the capital icon
	local strVotes = "";
	for i, v in ipairs(last.Votes) do
		local strLine = Locale.Lookup("TXT_KEY_LEKMOD_WORLD_LEADER_VOTE_LINE", Players[v.Player]:GetCivilizationShortDescriptionKey(), v.Delegates);
		local bGreen;
		if (bWinner) then
			bGreen = (i == 1);
		else
			bGreen = (v.Delegates == iFirst or v.Delegates == iSecond);
		end
		if (bGreen) then
			strLine = "[COLOR_POSITIVE_TEXT]" .. strLine .. "[ENDCOLOR]";
		end
		if (v.Player == iActivePlayer) then
			strLine = strLine .. "  [ICON_CAPITAL]";
		end
		if (strVotes ~= "") then
			strVotes = strVotes .. "[NEWLINE]";
		end
		strVotes = strVotes .. strLine;
	end
	Controls.Votes:SetText(strVotes);

	if (bWinner) then
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

-- the vote is counted while the turn starts; open the screen once per vote, before its result applies
local function CheckForNewVote()
	local pLeague = GetLeague();
	if (pLeague == nil) then
		return;
	end
	local last = pLeague:LekmodGetLastLeaderVote();
	if (last.Turn == nil or last.Resolved or last.Turn ~= Game.GetGameTurn() or last.Turn == g_iShownTurn) then
		return;
	end
	g_iShownTurn = last.Turn;
	Show(last);
end
Events.ActivePlayerTurnStart.Add(CheckForNewVote);
Events.SerialEventLeagueScreenDirty.Add(CheckForNewVote);

ContextPtr:SetHide(true);
