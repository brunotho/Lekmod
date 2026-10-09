# CLAUDE.md: working on this LEKMOD fork

## 0. Keep this file current (read this first)
This file records what has been **verified** about how this mod works, and how to work on it. Keep refining it:
- When you learn something new about how the game loads, builds, or behaves, update the relevant section in the same session.
- When something here turns out to be wrong, correct it, and note briefly what misled you. Several "obvious" assumptions in this project turned out false, see §8.
- Prefer verified facts (database query, log line, compiled result, playtest) over reasoning from code alone. Mark anything unverified as such.
- Keep it cohesive. Restructure rather than append when a section grows messy.

## 0b. Working agreement with the user (follow every session)
1. **Implement clear specs directly.** Don't wait for a confirmation round; the user explicitly dropped that rule.
   - Investigate, implement, then report what you found and changed.
   - Ask first only for genuine design decisions or ambiguities, and for outward-facing or hard-to-reverse actions (push, deleting the user's files, system settings).
2. **Small steps, each one recorded.**
   - After every implemented spec, add an entry to `changelog.txt` (repo root) and make a git commit.
   - Emulate the existing style of both. The changelog uses one section per item: `NAME (TYPE_KEY)`, a dashed underline, a one-line summary, then `- Changed:` / `- Added:` / `- Removed:` lines. Commits use a short imperative title (`Add PROMOTION_X: …`) plus a body when needed.
   - Commits go to branch `dev` in `civ-tools\lek` (§1, §2). **Never push without asking.**
   - **`changelog.txt` has a dual purpose.** It tracks development (and should line up with the git history), and it is the source for **player patch notes** on a future website. Keep it machine-readable:
     - `## <release>` opens a release block. New work goes under `## UNRELEASED (...)`.
     - Item: `NAME (TYPE_KEY)` + dashed underline + `Tags: a, b` + a short player-facing summary.
     - Player-facing lines: the summary, `- Added:`, `- Changed:`, `- Removed:`, `- Fixed:`. Write them for players with no development knowledge: effects and quick-speed numbers, no column names, C++ names or file paths.
     - **Player lines describe the net change compared to the previous release** (for the current block: upstream LEKMOD v35.4). Example: Heal Instantly "50 -> 25", not "50 -> 40" and then "40 -> 25".
     - Bugs we introduced and fixed before a release never reached players, so they go on `Dev:` lines. Only bugs that exist in the previous release are `Fixed:`.
     - Every line starts with one of the prefixes; no bare lines. Things that are defined but not yet reachable in game (e.g. ungranted promotions) get a `- Note:`.
     - Developer-only lines: `- Note:`, `- DLL:`, `- Dev:` (skipped by the website).
     - **Tags:** the first tag is the item's group (the website's section header); further tags are cross-cutting filters. Vocabulary (extend deliberately, and update the file header too): promotions, units, civs, policies, religion, ruins, combat, movement, naval, air, game mechanics, world congress, ui, art, bugfix.
     - Tags belong to changelog items, not to commits. The website reads `changelog.txt`, and the git history is for developers.
     - Update an item's existing section rather than adding a duplicate. When a later change alters an item, rewrite its player lines to the new net state.
     - Rewritten to these rules on 2026-10-07; the earlier entries mixed in internal names and intermediate steps.
3. **Lekmod + quick speed always.**
   - Many things are defined in the base game and then overwritten by Lekmod. Always check the final, loaded value (§6).
   - Spec numbers are **quick-speed** numbers, while the code and data usually hold **standard-speed** values that the game scales by game speed. Convert, and check how each formula scales.
4. **This file is the ground truth doc.**
   - The user's earlier `ai_ground_truth_workflow.md` (only on the old branch `dev-bruno`, never in this repo) was merged in on 2026-10-09: its yield audit order and natural wonder notes are in §4. Its NQM load-order claim is in §3 (probably wrong); its belief wiring steps are covered by the general checklist in §3. Nothing else in it is needed.
   - Keep this file current.
   - When you come across something that should be documented here, or that contradicts this file, propose the amendment.
5. **Spec vocabulary:**
   - **"(from scratch)" / "(new)"**: none of the item's old effects or yields persist. Remove everything old, then add the spec.
   - **"NEW"**: an entirely new item that doesn't exist in the code yet, or exists only as disconnected leftovers of an unfinished implementation.
   - **No marker**: the spec adds to the existing item, or overwrites a value when it's functionally the same effect.
6. **Specs live in Notion** ("LEK — v3 — implementation checklist" and its section pages; agreed 2026-10-07):
   - Items **not yet implemented**: the user edits the spec freely. The spec as it reads at implementation time counts. Record what was implemented in the changelog and commit.
   - Items **already implemented**: the user doesn't edit the spec in place, but adds a "CHANGE (date): …" note under the item (or tells Claude). Look for these notes.
   - Don't edit the user's spec pages unless asked. Claude's own pages (tracker, "Specs to refine", "Multiplayer test sessions") are sub-pages of the checklist.
   - **Ticks (✓, [x], DONE) on the spec pages mean "done on an old branch". They do not mean "in the game".** Status lives only in the tracker.
   - Sub-page "POST EVERYTHING adjustments" (the user's): tweaks meant for after all specs are done. Don't implement from it unless asked.
7. **Underspecified specs** (agreed 2026-10-08):
   - Tracker items with Status = Needs spec are listed on the Notion page **"Specs to refine"** (a sub-page of the checklist). The user writes answers there and says in chat when they are done.
   - Keep that page in sync with the tracker. Don't implement those items before the user is done.
   - If other work depends on one of them, ask in chat **before** starting; the user answers right away.
   - **Comments on spec pages are ignored.** Only the page text counts.
   - Map/Lekmap items are done by the user in a separate folder, so they are Dropped from the tracker.
8. **Multiplayer test sessions** (agreed 2026-10-08): tests that need a second human player (or a special setup) go on the Notion page **"Multiplayer test sessions"** (sub-page of the checklist), with concrete steps and expected results. Add to it whenever such an item is implemented, and remove items the user reports as passed.
9. **The tracker is the single source of item status** (set up 2026-10-07):
   - Notion database **"Tracker (v35.4 port)"**, a sub-page of the checklist. Data source: `collection://311b2761-ecf0-448c-9f6b-81d808f4361c` (query it with the Notion tools).
   - One row per spec item. Columns: Item, ID (LEK-n), Section, **Status**, **Phase**, Where (Mod / Lekmap / Website), Old code, Commits, Notes, Spec (link to the section page).
   - **Status:** `Needs spec` (open questions; the user refines it) → `Ready` → `Implemented` (on `dev`, not yet playtested) → `Playtested` (the user confirmed it in game on the port). Also `Blocked` (waiting on another item; the reason is in Notes) and `Dropped`.
   - **Phase** = implementation order, by dependency:
     1. Promotions, Game Mechanics, Ruins, City States, Bugfixes, Interface
     2. Units, Resources, Tech Tree
     3. Religion, Buildings, National Wonders
     4. Tourism (great work rework) and everything blocked on it
     5. Policies, Diplomat/Spy, World Congress
     6. Civs
     9. Final interface tuning.
     Map rows (Lekmap) and Website have no phase.
   - **Old code** lists commits on old branches (`dev-bruno`, `civ-changes-bruno`) for implementation ideas only. Never merge them. **These branches are only in `civ-tools\lekbuild`** (its remote `origin` = ashwintrisal/Lekmod), not in `lek`: read them with `git -C ../lekbuild show <hash>`. kubugaming and Ashwin code is excluded (§1).
   - **Workflow per item:** read the spec page (and any "CHANGE" notes or comment threads), implement, add the changelog entry, commit, then set the row to `Implemented` with the commit hash. When the user reports a playtest, set `Playtested`. Record deviations from the spec and spec conflicts in Notes, and ask the user about them.
   - **Testing policy** (agreed 2026-10-07):
     - Simple value or formula changes: Claude verifies them in the loaded DB (`Civ5DebugDatabase.db`, written when a game starts) and the logs. The user does not test them by hand.
     - Behaviour changes (new mechanics, UI, situations that must be set up): the user tests them by hand; give concrete expected values.
     - Everything is covered later by full multiplayer games, which also catch ripple effects.
     - Status stays `Implemented` until the user playtests. Note DB-verified items in the row's Notes ("DB-verified <date>").
   - **Discarding old work for cleanliness is allowed** (user, 2026-10-07): if an implemented item is messy, redo it from the spec.
   - The scratchpad on the checklist page holds unrefined ideas. They are tracked under Section "Scratchpad", mostly as `Needs spec`. Help the user turn them into specs when asked.
   - The old audit page ("Implementation status audit (2026-10-06)") is superseded by the tracker.
   - When the user says something "tested / works" in chat, set those rows to `Playtested` right away.
10. **Session start routine:** read §9 here, then query the tracker (`Status = 'Ready'`, ordered by Phase) and the "Specs to refine" page for new answers. Check `git status` (only `Lua/UI/FrontEnd.lua` should be dirty, because of its `LEKMOD_UI_CHECK_DONE` flag; any other tracked `Lua/UI` file showing up means its committed copy is stale, see §2) and `git log --oneline -15`.
11. **Working style the user likes:** take large chunks of work without asking; batch several items, then report with concrete in-game checks. Keep chat answers short; findings go into Notion/changelog. Ask with the question tool when two readings of a spec are equally plausible (give the numbers for each option).

---

## 1. Project context
- **Lekmod** is a large Civ V (BNW) multiplayer balance and content mod. Upstream: `github.com/EnormousApplePie/Lekmod`.
- **The user's repo (since 2026-10-07): `github.com/brunotho/Lekmod`.** It's a GitHub fork of EAP's repo at **v35.4** (`201df6c5`), and the user owns it.
  - Work happens on branch **`dev`**. `main` stays equal to upstream's main.
  - `dev` = v35.4 + the user's own work ported from the old fork: ruins overhaul, kill-yield fix, Demographics, the promotion batch, changelog, DLL. See §9 "Port to v35.4".
  - **User decision: no code from Ashwin or kubugaming.** That excludes the World Congress changes, the June fixes, and the `dev`/`stratresourcechanges` policies.
  - Everything else gets re-implemented from the Notion specs, cohesively and in one style. Old code may be read for implementation ideas only.
- **The old fork, `github.com/ashwintrisal/Lekmod`, is now reference only.** It branched from upstream at **v34.11** (`f4b96af9`) and had 39 commits by brunotho (the user) and Ashwin:
  - World Congress changes (Ashwin, Feb)
  - ~15 promotions and a ruins overhaul (brunotho, Apr, largely AI-written)
  - Ashwin's June "fixes"
  - plus unmerged branches (§9)
- Pull upstream updates by **merging** `upstream/main` into `dev`. Don't push, open PRs to EAP, or rewrite published history without asking.
- The user is taking over development, is new to this codebase and to compiling, and playtests changes themselves. Explain mechanics plainly. Ask before anything outward-facing (git push, posting) or hard to reverse.

## 2. Where things live
| Location | What |
|---|---|
| `...\Civilization V\Assets\DLC\WIP_LEKMOD\` | The **live mod** the game loads. It's a **junction (link) to `civ-tools\lek\LEKMOD\`**, so every edit there is an edit in the repo. Players only ever receive the `LEKMOD/` folder. |
| **Never move or delete `DLC\WIP_LEKMOD` in Explorer** | Moving a junction copies its contents and then deletes the originals, which are the repo's files (2026-10-08: an aborted move deleted 3,940 tracked files; restored with `git ls-files -d -z -- LEKMOD \| xargs -0 git checkout --`). To swap mods, run `lekmod_off.bat` first (removes only the link), then put the other mod in. |
| `C:\Users\bbruno\civ-tools\lekmod_on.bat` / `lekmod_off.bat` | The user's mod switch. They create or remove the junction only, never the repo. `on` also runs `ui_check.bat`. `lekmod_setup_link.bat` was the one-time setup that moved the old folder to `civ-tools\WIP_LEKMOD_backup_2026-10-07`. |
| `C:\Users\bbruno\civ-tools\lek\` | **The working repo**: a full clone of `brunotho/Lekmod`, branch `dev`. Remotes: `origin` (the user's fork), `upstream` (EAP), `old` (= `lekbuild`, reference). DLL builds run here (short path, §5). |
| `C:\Users\bbruno\civ-tools\lekbuild\` | Old sparse checkout of Ashwin's fork. Branch `repair-batch-1` holds the 2026-10-05/06 repairs. **Reference only** since the port. |
| `C:\Users\bbruno\Desktop\civ mods\WIP_lekmod_full_repo\` | The user's own full checkout of the fork (all folders). Untouched by Claude so far. |
| `C:\Users\bbruno\civ-tools\` | Tools: `texconv.exe`, `7zip\7z.exe`, `vs2008\` (installer source), `dll_backup\` (previous DLLs). |
| `Documents\My Games\Sid Meier's Civilization 5\Logs\` | Game logs (§6). Logging is enabled in `config.ini` (`LoggingEnabled = 1`). |
| `Documents\My Games\Sid Meier's Civilization 5\cache\` | The loaded game database as SQLite (§6). |

Repo layout (GitHub): `LEKMOD/` (the mod), `LEKMOD_DLL/` (C++ source), `Lekmap/` (map script, a separate download into `Assets\Maps`), `LekmodInstaller/`, `docs/`, `.github/workflows/ci.yaml` (upstream's automated DLL build).

This file lives at the **repo root** (`civ-tools\lek\CLAUDE.md`), so it doesn't ship to players. Start Claude sessions in `civ-tools\lek`. A session started in the game folder won't see this file.

**Generated UI:** `ui_check.bat` writes `LEKMOD/Lua/UI/` and `LEKMOD/*.bak`. Always run it **through the junction** (`DLC\WIP_LEKMOD\ui_check.bat`): it looks for EUI in the folder above itself.
- Most of `Lua/UI/` is git-ignored, but upstream **tracks about a dozen files there** (`FrontEnd.lua`, `StagingRoom.lua`, `MainMenu.lua`…).
- Edit UI in the templates under `Lua/tmp/`. **The tracked `Lua/UI` copies ship to players too, so keep them equal to their templates:** after changing a template whose file is tracked in `Lua/UI`, commit the regenerated copy with it.
  - Exception: `FrontEnd.lua` must be committed with `LEKMOD_UI_CHECK_DONE = false` (the template's value); `ui_check.bat` sets it to `true` locally, so it always shows as modified. Stage the template's content without touching the working copy: `git update-index --cacheinfo 100644,$(git hash-object -w --path=LEKMOD/Lua/UI/FrontEnd.lua LEKMOD/Lua/tmp/ui/FrontEnd/FrontEnd.lua.ignore),LEKMOD/Lua/UI/FrontEnd.lua`.
  - Until 2026-10-09 this file said "never commit generated output", which left the committed `StagingRoom.lua/.xml`, `MPGameOptions.lua` and `FrontEnd.lua` without the lobby preset, the Immortal default and the menu background (fixed in `668bf45e`).

**Git notes:**
- Git has `core.autocrlf=true`, while the Override files are LF. Compare with `diff --strip-trailing-cr`. `sed -i` in Git Bash strips CRs from CRLF files; use Python byte I/O, or check line endings afterwards.
- To split one file's changes into several commits, use `civ-tools\stage_hunks.py <file> <regex> [--invert] [--range A-B]`. It uses 3-line context; zero-context hunks (`-U0` + `--unidiff-zero`) misplaced inserted lines once. After staging, check with `git diff -U0` that what remains is exactly what you expect.
- After merging `upstream/main`, check for **silently doubled members and columns**. Upstream's v35.4 `PillageChange` duplicated ours without a conflict.
- Upstream compacted `CIV5Units.xml` in v35 (~35k default-value lines removed), so line diffs against older versions look huge even when little changed.

## 3. How the game loads the mod (verified)
The folder is a **DLC package** (`MPModsPack.Civ5Pkg`), not a ModBuddy mod:
1. **`CvGameCore_Expansion2.dll`**: the compiled game core (all rules, combat, ruins, World Congress…). It replaces Firaxis's. Built from `LEKMOD_DLL/` (§5).
2. **`Override\`**: each file replaces the base-game file of the **same name**.
   - About 520 files there are **empty** on purpose. They blank out base-game data.
   - **`Override\CIV5Units.xml`** (~308k lines) holds **all gameplay data** for every table (units, promotions, ruins/GoodyHuts, policies, World Congress, icon atlases, `<Table>` column definitions…). The file name is misleading.
   - **`Override\CIV5Units_Mongol.xml`** (~145k lines) holds **all text** (`Language_en_US`, using both `<Row Tag>` and `<Replace Tag>`).
3. **`Lua\UI\*.lua`** (and some `.xml`): UI files. They override the base-game UI file of the same name, e.g. `GoodyHutPopup.lua` = the ruin reward popup.
   - **`Lua\UI\` is generated output.** Players are told to run `ui_check.bat`, which **deletes `Lua\UI\` and rebuilds it** by copying templates from `Lua\tmp\ui\...\*.ignore` (standard UI) or `Lua\tmp\eui\...\*.ignore` (when EUI is installed as `DLC\UI_bc1`).
   - **Edit the template** and sync it into `Lua\UI\`, otherwise the next `ui_check.bat` run silently reverts the change.
   - The user runs the standard UI (no EUI folder).
   - Base-game UI layouts that Lekmod doesn't override come from `Assets\DLC\Expansion2\UI\InGame\...`. Overriding one means adding the XML to the templates, to `ui_check.bat`, and to `Lua\UI\`.
   - Base-game scripts Lekmod overrides since 2026-10-08: `CivilopediaScreen.lua` (both UIs), `DiploList.lua` (standard UI; `ui_check.bat` copies it unless EUI has its own) and `ChooseGoodyHutReward.lua` (both UIs; the ruin choice). Copy the Expansion2 file into `Lua\tmp\ui\...` and add a `ui_check.bat` rule.
   - **Any network message from Lua (`Network.Send*`) un-ends a finished multiplayer turn.** Screens must not send hidden messages (e.g. statistics) once the turn is ended: check `Network.HasSentNetTurnComplete()`.
   - Lobby options are `GameOptions` rows in `CIV5Units.xml` (explicit IDs; Lekmod's: 67 strategic trading, 68 high-contrast colors, 69/70 wonder tie Neither/Both, 71 start at war, 72 mode Casual, 73 preset-applied flag; 68–73 are hidden). The DLL reads them with `isOption("GAMEOPTION_X")`. **An unset option reads as its DB default (0), never -1.**
   - **Lobby (2026-10-08):** `MPGameOptions.lua` (template `Lua/tmp/ui/Lobby/`) is shared by the host setup screen (`MPGameSetupScreen.xml`) and the staging room, but the staging room has its **own options panel in `StagingRoom.xml`**: layout changes must go into both XMLs. The Mode dropdown (Tournament default / Casual) applies the whole preset (`LekmodApplyModePreset`); only map type, Mode, Civ Colors and the map script's options are visible; mode decisions show as bullet lines (`g_LekmodModeInfoLines`); everything else is hidden by `LekmodApplyLobbyVisibility` via `Lekmod*` control IDs.
4. **`Art\`**: graphics. `.dds` textures are found **by file name anywhere** under it.
   - **XML and `.modinfo` files under `Art\` are NOT loaded as game data.** They're leftovers from the source mods Lekmod was assembled from.
   - Verified twice. The promotions in `Art\Promotions\LekmodPromotions.xml` and the ruin values in `Art\No Quitters Mod (v 11)\gameplay\GoodyHutChanges.xml` were absent from the loaded database.
   - **To make data live, put it in the two Override files.**
   - **Conflicting claim to keep in mind:** `ai_ground_truth_workflow.md` says the NQM `.modinfo` (317 `UpdateDatabase` entries, e.g. `gameplay/GoodyHutChanges.xml`) loads before `CIV5Units.xml`, and that `CIV5Units.xml` then wipes most tables via `<Delete />`. Evidence against NQM loading at all (2026-10-06):
     - NQM rows that target tables missing from the DB (e.g. `AIEconomicStrategy_Flavors`, `Trait_YieldChangesLuxuryResources`) produce **no** "no such table" errors in `Database.log`, while other failed inserts do get logged.
     - NQM `.sql` `ALTER TABLE` scripts leave no trace.
     - Practically both models agree: anything in a table that `CIV5Units.xml` re-creates or wipes must be edited there.
     - If you ever see an `Art/` file take effect, document it here.

**A feature that needs new C++ only works when ALL of these hold** (names must match exactly):
- the column is defined in `CIV5Units.xml` (`<Table name="X"><Column .../>`), and values are set in `CIV5Units.xml`
- the text is in `CIV5Units_Mongol.xml`
- the C++ reads the column **by name** (`kResults.GetInt("Col")` in `CacheResults`)
- the DLL is **rebuilt and installed**
- (optional) Lua UI displays it, and the Lua logic matches the data

## 4. Data conventions and gotchas
- **Promotion IDs are explicit** (`<ID>`). Every row in the `UnitPromotions` section has one. New rows get the next unused ID: currently up to **371**. v35.4 uses IDs up to 343; ours are 344–371. Upstream's IDs already have gaps (e.g. 271–273), which is fine. Check uniqueness *within the section*, since other tables reuse the same numbers.
- **Line endings differ per file; check before scripting.** The repo stores LF; in the `lek` working copy most C++ and Lua templates are CRLF, while **both Override XML files**, `_Defines.h`, `changelog.txt` and `CLAUDE.md` are LF (verified 2026-10-08 with byte counts; an earlier note here said the Override files were CRLF, which was wrong). The game reads either.
  - Prefer the Edit tool, which keeps a file's endings.
  - When scripting, read and write **bytes** and match the file's ending. Count with Python (`b.count(b'\r\n')`); `grep -c $'\r'` in Git Bash gave wrong answers.
- **Tooling pitfalls (cost time repeatedly):**
  - **Bash heredocs mangle backslashes** (`\\` collapses, `\U`/`\N`/`\s` break Python strings). Write Python scripts with the Write tool into the scratchpad (raw strings), or use the Edit tool. Never put Windows paths or regexes with backslashes into a heredoc.
  - **The Edit tool rewrites non-UTF-8 bytes** (e.g. the Firaxis header's copyright byte in some `.h` files becomes U+FFFD). After editing C++ headers, check `git diff` for a changed line 2 and restore it from `git show HEAD:<file>`.
  - Byte-safe C++ edits: the scratchpad helper pattern `cpp_edit.py` (exact-once anchors, keeps CRLF and non-UTF-8 bytes) worked well; recreate it if the scratchpad is gone.
  - Unit combat strength has two parallel code paths in `CvUnit.cpp` (old `GetMaxAttackStrength(pFromPlot,...)` and v35.4's `GetMaxAttackStrength(const CvCombatInfo&...)`, same for defense/ranged). New combat modifiers must go into both.
  - **`sed -i` strips CRs** from CRLF files (the C++ sources). Use the Edit tool or Python byte I/O.
  - **The Write tool strips trailing whitespace**, and many Override lines end with a space (`<Row> `, `</Table> `). Use short anchors without line ends, or match by regex.
  - **XML tables contain commented-out `<Row>` blocks.** Row-editing scripts must skip `<!-- ... -->` regions (2026-10-08: a script edited commented rows; caught in the diff).
  - Bulk value changes to existing rows can be done with `<Update><Where Type="X"/><Set Col="v"/></Update>` blocks after a table's section (used for building purchase costs and tech costs). Later per-row changes must then edit those Update values, not the original rows.
- **Broken upstream helpers / engine quirks (2026-10-09):** `CvCityBuildings::HasBuildingClass` always returns false (its list `m_buildingsThatExistAtLeastOnce` is never filled); loop the class's buildings with `GetNumBuilding` instead. `SetNumFreeBuilding` doesn't notify the renderer (walls/wonders don't appear until reload); call `gDLL->GameplayWallCreated` etc. yourself.
- **Strategic node sizes** live in the mod (`Resources.AmountMajor/AmountMinor`) and are read by the map script; the Lekmap copy in this repo still hardcodes them (the user's map folder is the authority). An earlier conclusion here that they were map-only was wrong.
- **Valid text icons:** `[ICON_PEACE]` = Faith (`[ICON_FAITH]` does **not** exist). `[ICON_EXPERIENCE]` and `[ICON_HEALING]` do **not** exist.
  - The authority is the loaded `IconFontMapping` table in `Civ5DebugDatabase.db` (884 icons).
  - Don't judge by whether a tag appears in any text: `[ICON_STAR]` is valid but appears in no text.
- Text keys must be unique. Check `CIV5Units_Mongol.xml` before adding a key; existing keys may already be used by other content (e.g. `TXT_KEY_PROMOTION_DISCIPLINE`).
- Numeric text placeholders: `{1_Num}`. A text that expects a number but gets none renders **blank**.
- **Game speed: always assume QUICK.** The user only plays quick speed, and their specs state quick-speed numbers.
  - When a formula involves game speed (culture, faith, production costs, turn counts…), check how speed scaling affects it, and make the result match the spec *at quick speed*.
  - Other speeds don't matter.
- **Text style (user preference) for all player-facing text** (tooltips, popups, pedia):
  - **Be greedy with spacing for readability.**
    - Each sentence goes on its own line (`[NEWLINE]`).
    - Distinct topics or effects are separated by an empty line (`[NEWLINE][NEWLINE]`), e.g. bonus vs. penalty, or combat vs. movement.
    - This applies to all new and changed tooltips. Older tooltips will be retrofitted later (user's intention).
  - **Exception:** list or menu rows with fixed height, like the Shoshone ruin choice (`ChooseDescription`), must be short, matter-of-fact one-liners.
  - No spec or implementation notes ("Eligible: naval melee", "Requires Bombardment II", "policy-granted"); the UI shows those itself.
  - Distinctions that matter to players stay, e.g. Discipline "(non-air units)" vs Discipline (Air) "(air units)".
  - After changing any number, update its tooltip (failure pattern 7b).
- **Civilopedia (user, 2026-10-08):** update pages aggressively to the current rules whenever work touches a topic. Be verbose with gameplay information (all relevant numbers, at quick speed), and remove history and flavor text. Goal: every page eventually shows all relevant gameplay info and nothing else. Pages are `Concepts` rows in `CIV5Units.xml` (explicit IDs; check uniqueness *within the section*, other tables reuse the numbers) with texts in `CIV5Units_Mongol.xml`. The pedia has no clickable links between concepts; order comes from `InsertAfter` chains. Since 2026-10-08 Lekmod overrides the pedia script (`Lua/tmp/ui/Civilopedia/CivilopediaScreen.lua.ignore`, a copy of Expansion2's; ui_check.bat copies it for both UIs), so page layouts per category can be changed there (e.g. the City-States tab shows type rules instead of history).
- Promotion icons: 4 sizes (256/64/45/32), DXT5 `.dds`, **transparent background**; the game draws the round frame. See §7.
- C++ feature switches live in `LEKMOD_DLL/CvGameCoreDLL_Expansion2/_Defines.h` (e.g. `LEKMOD_NEW_ANCIENT_RUIN_REWARDS`, `FULL_YIELD_FROM_KILLS`, `LEKMOD_RELOCATE_PROMOTION_PREREQ_ORS`). Check which are on before reasoning about code paths.
- Lekmod-specific tables worth knowing:
  - `UnitPromotions_PromotionPrereqOrs`: a missing referenced promotion is silently skipped through an INNER JOIN.
  - `UnitPromotions_YieldFromKills` and `UnitPromotions_KillYieldValidEras`: promotion yields from kills. A promotion yields nothing unless the killed unit's era is listed.
  - `UnitPromotions_UnitCombats`, `Unit_FreePromotions`, `Policy_FreePromotions`: how promotions become obtainable.
- **Yield audit (what does tile X yield?):** a tile's yield is the **sum of all matching rows across tables**; never cite one table alone. Check in the loaded DB: `Terrain_Yields` → `Feature_YieldChanges` (+ `Feature_RiverYieldChanges`/`HillsYieldChanges`/`MountainYieldChanges`) → `Resource_YieldChanges` → `Improvement_Yields` / `Improvement_ResourceType_Yields` → `Improvement_TechYieldChanges` → `Belief_*YieldChanges` → `Building_SeaResourceYieldChanges`, `Trait_ImprovementYieldChanges` etc. Then grep `_Defines.h` for DLL hooks that add yields in C++. Internal keys often differ from display names (`BELIEF_TEARS_OF_NOOBS` = "Tears of the Gods"); check the text file.
- **Natural wonders** (from the old ground-truth doc, re-verified in the DB 2026-10-09):
  - Tile yields are not speed-scaled (no yields are); `Feature_YieldChanges` values are used as they are.
  - `Features.Help` shows on the pedia page and, since 2026-10-09, in the tile hover (`GetNatureString` in `PlotMouseoverInclude`; the base game never showed it in the hover, contrary to the old ground-truth doc).
  - Krakatoa is `FEATURE_VOLCANO`.
  - Lekmod tables since 2026-10-09 (`LEKMOD_NATURAL_WONDER_EFFECTS`): `Feature_BuildingClassYieldChanges`, `Feature_HolyCityYieldChanges` (working city), `Feature_AdjacentPlotYieldChanges` (neighbour plots, optional ImprovementType/AdjacentFeatureType), `Feature_AdjacentCityYieldModifiers`, `Features.FirstFinderGoldPerEra`.

## 5. Building and installing the DLL
**Toolchain:** Visual C++ 2008 Express SP1 (`C:\Program Files (x86)\Microsoft Visual Studio 9.0\`).
- It was installed from archive.org's `VS2008-Express-w-SP1.ISO`, which upstream CI also uses.
- Running setup from the mounted ISO fails; it works from the **7-Zip-extracted** copy in `civ-tools\vs2008\VCExpress\setup.exe /q`.
- The install also added an unneeded SQL Server 2005 Express service.

**Build** (PowerShell):
```
Set-Location C:\Users\bbruno\civ-tools\lek
& "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\vcpackages\vcbuild.exe" "LEKMOD_DLL\CvGameCoreDLL_Expansion2\CvGameCoreDLL_Expansion2.vcproj" Release *> C:\Users\bbruno\civ-tools\build_release.log
```
- Takes a few minutes. Run it in the background. "0 error(s)" with ~780 warnings is normal.
- Output: `LEKMOD_DLL\CvGameCoreDLL_Expansion2\BuildOutput\VS2008_ReleaseWin32\CvGameCore_Expansion2.dll`.
- VS2008 has a **~260-character path limit**, so the checkout must stay at a short path. The scratchpad path is too long.

**Install:**
1. Civ V must be **closed**; the DLL is locked while the game runs. Ask the user, and never kill the game.
2. Back up the current DLL to `civ-tools\dll_backup\`.
3. Copy the build output to `LEKMOD\CvGameCore_Expansion2.dll`. Through the junction, that file *is* the game's DLL. Compare md5 checksums.
4. Commit the DLL (convention: a separate `Rebuild CvGameCore_Expansion2.dll` commit).
5. Start a **new game** for every test. Old saves break when the DLL adds saved fields.

**Windows Smart App Control** blocks unsigned, unknown DLLs. A blocked load shows up as a crash before the main menu, and `Logs\GameCore.log` says *"LoadLibrary failed with error 4551: An Application Control policy has blocked this file."* The user turned it **off** on this PC (2026-10-05). Players with it on hit the same issue with any fresh unsigned Lekmod DLL. The upstream norm is documentation; the real fix is code signing.

## 6. Verification toolkit (use it; don't trust impressions or code reading alone)
- **Loaded data:** `cache\Civ5DebugDatabase.db` (SQLite; query with Python `sqlite3`). It is written at game startup and **matches what the running game uses** (verified with a Lua diagnostic). Text lives in `cache\Localization-Merged.db` (`LocalizedText`, `Language='en_US'`).
  - Caveat: effects **computed in C++** don't appear there (e.g. hardcoded ruin formulas).
- **Logs** (`Logs\`):
  - `Database.log`: XML load errors. The garbage "unrecognized token" and `ArtDefine_StrategicView ... not unique` lines are pre-existing noise.
  - `Lua.log`: Lua errors and `print()` output. Pre-existing noise: Lekmap `FeatureGenerator` and `Demographics.lua manyinclude` errors.
  - `GameCore.log`: DLL load problems.
  - `stopwatch.log`: load phases.
- **Lua diagnostic trick:** add a temporary `print("TAG", ...)` to a UI script that runs at the right moment (e.g. `GoodyHutPopup.lua`), have the user trigger it in game, then `grep TAG Lua.log`. Back up the file first, and remove the print afterwards.
- For gameplay checks, give the user **concrete expected values** (formulas → numbers) to compare against, then cross-check the database and logs yourself.

## 7. Art pipeline
Python with Pillow reads `.dds`. `civ-tools\texconv.exe` writes them:
```
texconv -nologo -y -f BC3_UNORM -m 0 -o out icon_N.png    # 256/64/32: full mips
texconv -nologo -y -f BC3_UNORM -m 1 -o out icon_45.png   # 45px: 1 mip, matching the originals
```
- Fixing the AI-made promotion icons: key out the dark background (alpha from brightness of max(R,G)), crop to the glyph, scale to ~70%, center, then export all 4 sizes.
- **Reshape done for all 19 icons in `Art\Promotions`** (originals in scratchpad `backup/icons_all`). The improved method only makes background *connected to the image border* transparent, so dark interior details (One Good Eye's patch, Stargazing's pupil) are kept. No colours are changed.
- **Icon provenance:**
  - The user's original art set has 15 distinct icons, added in commit `d224c97d`: Amphibious I–III, Carpet Bombing, Discipline, Feared Elephant, Hatamoto, Iaijutsu, Marauder, Mountaineering, One Good Eye, Repair Crew, Stargazing, Supply Ship, Swift Transport.
  - Fear Aura (17:31) and Zealot (17:12) were added on 2026-04-06 with their own images; the Fear Aura image is the user's intended art.
  - Envelopment and Bunker Busting were added later the same day and **copied the Fear Aura image as a placeholder**. Those two need real art.
  - Glutton uses a generic shield (`ABILITY_ATLAS` 14). The user remembers an apple icon, but none exists in the repo, the mod folder or the user's folders. Ask the user for the original art file.
  - The Feared Elephant original icon isn't wired up; the upstream promotion has its own icon.

## 8. Failure patterns found in the fork (check new work for these)
1. **Data placed where the game doesn't read it**: XML under `Art\`, `.modinfo` edits.
2. **C++ never compiled.** April C++ only reached the game on 2026-10-05; a June "compile fix" actually broke compilation.
3. **Parallel duplicate implementations.** The ruins overhaul existed as a hardcoded draft (slipped into the Amphibious commit `18d18874`) **and** a column-based version (`4f6af0bb`). They came from separate branches merged together.
4. **Unrelated changes bundled into commits.** E.g. "reduce Heal Instantly" also rewrote the faith ruin's data. Don't trust commit titles; diff the commit.
5. **Data changed without its consumers.** The ruin popup Lua picks its text by data fields that the data change made zero, so the popup came out blank.
6. **Dead edits**: targeting rows that aren't used (`GOODY_EXPERIENCE` vs the live `GOODY_EXPERIENCE_MOVE`), and promotions that nothing grants (see §9).
7. **Upstream bugs exposed by new content**, e.g. the kill-yield era flags (fixed, §9).
7b. **Balance tweaks without text updates.** Coastal Raider, Boarding Party, Heal Instantly (`INSTA_HEAL_RATE` define) and others changed numbers only, so their tooltips lied.
   - After any value change, diff the tooltip.
   - For promotions, verify the help text against the loaded DB values.
7c. **Wrong cross-references.** Bunker Busting's bomber prerequisite pointed to `PROMOTION_SIEGE` (a melee/gun promotion) instead of `PROMOTION_AIR_SIEGE_*`.
   - Check prerequisites against `UnitPromotions_UnitCombats` of the same unit type.
7d. **Off-by-one in new C++.** The Amphibious "max moves after domain change" formula left 0 MP instead of 1. Sanity-check new formulas with concrete numbers.
8. **AI art**: icons with baked backgrounds, and one image reused for several promotions.
9. **Upstream code that bypasses our hooks after a merge.** Our code merged cleanly but never ran: in v35.4, a new early return in `ConsumesAllMoves` bypassed Amphibious. After an upstream merge, re-read the functions around each of our hooks and retest every feature, not only the conflicting files.

**Debugging lesson:** twice a confident conclusion was wrong. "Zealot will work" was wrong; "the ruins aren't changed at all" was half wrong, because the C++ computed the effects. When the user's observation conflicts with your model, find a direct measurement (database, log, diagnostic) before arguing.

## 9. Status (update as things change)
### Current state (2026-10-09, end of session)
- `dev` = v35.4 (`201df6c5`) + our commits (148 ahead of v35.4 on 2026-10-09). **Not pushed** (the user hasn't asked). The installed DLL is the latest build (`05452f0e`).
- **The port is live.** The game's `WIP_LEKMOD` is a junction to `lek\LEKMOD`, and its DLL is this repo's build. The old fork's game folder is backed up in `civ-tools\WIP_LEKMOD_backup_2026-10-07`.
- **Item status, playtest results and open design questions live in the tracker (§0b.9), not here.** Query it at session start to see what's next.
- **Done so far:** Phase 1 complete except Cyrillic (waiting for the Tournament Mod authors' permission; their `Fonts` folder would work, ~85 MB, last in the queue) and the 6/7/8-player lobby (postponed by the user). Phase 2: Tech Tree done and playtested; **Resources all done** (2026-10-09: water yields playtested; rare luxuries, settle-on effects, natural wonders, strategic node amounts implemented; Spices, Cattle and Stone walls confirmed by the user). **Units partly done** (2026-10-09): strategic requirements, stat/cost changes, submarines, Spearman/Pikeman, Worker->Archaeologist, Festival, naval rework (Quinquereme, Caravel, Privateer, Frigate, Ship of the Line, Dreadnought, Blind Spot/Minimum Range/Docked, Swift Transport).
- **The user has not playtested anything from 2026-10-09 except the items named above.** Their plan: test the resource fixes (wonder building bonuses, wonder tooltips, walls visual, node sizes with their map) together with the units. Give them concrete checks from the changelog entries of 2026-10-09.
- **Next up (Phase 2 Units, tracker Status=Ready, Section=Units):** Infantry row rest (Expeditionary Force/Marines: Amphibious I+II instead of Amphibious/Embarkation with Defense; Marines upgrade to Mech Infantry keeping promotions), Nuclear Missile rebase under the fast-hand setting, Helicopter Sentry(+2)/Quick Study, Sitting Ducks, Great General (early model, citadel culture, citadel ZoC vs naval), Great Admiral drydock, Great Merchant custom house, GDR rework, Conquistador, Vanguard Corps, Skiff, Nelayan, Self-Propelled Artillery, spaceship parts as military units, Cargo Ship/Caravan equivalence. Then Phase 3.
- **Reopened by the user 2026-10-09 (Status Ready, details in the rows' Notes):** resource hover must show unique resource effects (Marble, Obsidian...), and the marsh-clearing build tooltip shows 1 Food instead of the real amount.
- **Strategic node sizes still 6 iron in the user's game (2026-10-09):** the map script does not read `Resources.AmountMajor/AmountMinor` yet. Fix in Lekmap (`HBAssignStartingPlots.lua` `GetMajorStrategicResourceQuantityValues` / `GetSmallStrategicResourceQuantityValues`: read `GameInfo.Resources[...]` amounts for the standard setting, keep the sparse/abundant offsets); the user's map folder is the authority, so agree with the user where to change it.
- **Obsidian '+11% toward melee units':** that is the data's -10% melee unit cost (`Resource_UnitCombatProductionCostModifiersLocal`) shown as a production bonus (1/0.9 = +11%); it applies to any city with Obsidian connected locally, including on the city tile. Working as designed.
- **Air evasion mechanics (verified in CvUnitCombat.cpp):** `EvasionChange` is the chance that an interception does not happen at all (`MAX_EVASION_PROBABILITY` 90 only limits picking evasion promotions; free promotions are not capped, so the old Stealth Bomber with 100 was never intercepted, as the user observed); the bombers' Evasion promotion is `InterceptionDefenseDamageModifier` -50 (less damage when intercepted). Two separate mechanisms.
- **Open question for the user (tracker row 'Battleship, Missile Cruiser...'):** Stealth Bomber evasion vs the bombers' Evasion promotion (which is -50% interception damage, not an evasion chance).
- **Open on "Specs to refine":** CS quests, Diplomat/Spy, Congress mechanics (unanswered); plane healing and ideologies (parked by the user).
- Messages can arrive while you work (mid-turn). Fold them into the current batch and mention them in the report.
- Port playtest lesson (2026-10-07): Amphibious merged cleanly but was dead, because v35.4's new `LEKMOD_WATER_WALK_IMPROVEMENT_RULES` block in `CvUnitMovement::ConsumesAllMoves` returned early (§8 pattern 9). Fixed in `f1706839`, playtested.
- Our promotion IDs: 344 Zealot, 345 Envelopment, 346 Glutton, 347–360 the April batch (Amphibious I–III, Bunker Busting, Repair Crew, Supply Ship, Sambuca, Carpet Bombing, Discipline, Discipline (Air), Fear Aura, Marauder, Mountaineering, Swift Transport), 361 Iaijutsu, 362 Hatamoto, 363 One Good Eye, 364 Stargazing, 365 No Pillage Heal, 366 Stealth Evasion (80%), 367 Anti-Mounted (Spear), 368 Blind Spot, 369 Minimum Range, 370 Docked, 371 Broadside. New unit IDs: 267 Dreadnought (classes 113 Ship of the Line, 114 Dreadnought).
- Promotions defined but not yet granted by anything: Discipline, Discipline (Air), Fear Aura, Marauder, Swift Transport, Iaijutsu, Hatamoto, One Good Eye, Stargazing. Their grants are part of other specs (Honor/Iron Fist, GDR/Berserker/Gauls, Privateer/Tunisia, naval units, Japan, Expansionism, Chile); the tracker rows name them.

**How the port was done:**
- Branch `port-src` = `old/repair-batch-1` with Ashwin's 7 World Congress commits reverted, and the dead `Art/` XML/modinfo edits and the DLL binary dropped.
- That branch was squash-merged onto v35.4 and committed by theme with `stage_hunks.py`.
- Ashwin's 2 June commits needed nothing: their C++ was inside the deleted ruins draft, and the rest was `Art/` wiring.
- Resolutions against v35.4:
  - **`PillageChange`**: v35.4 added the same promotion field with the same meaning (% bonus to pillage gold, used by Buganda). Our duplicate was removed, and Marauder uses theirs.
  - **Promotion IDs** renumbered +4 (upstream took 340–343).
  - **Heal while embarked**: allowed by `IsHealWhileEmbarked()` OR Buganda's `IsEmbarkedMissionAllowed(MISSION_HEAL)`, in both `CvPlayer::DoUnitReset` and `CvUnit::canHeal`.
  - **Embarked defense** (40% of max(melee, ranged) strength) re-applied inside upstream's moved `GetEmbarkedUnitDefense`.
  - **Sortie**: v35.4 computes all combat damage in `CvGame::getCombatDamage(CvCombatInfo&)`. The sweep reduction now lives there.
  - Upstream removed Anti-Naval 1–3. The Mobility prerequisite that references them is harmless (INNER JOIN skip).
  - Fixed while porting: the Pictish Warrior tooltip used the invalid `[ICON_FAITH]`.
- The kill-yield era fix is still an upstream bug: a candidate to offer EAP.

### Our DLL switches (`_Defines.h`; grep the name to find every hook)
- `LEKMOD_CS_WAR_DECLARATION_PENALTIES`: city-state war standing (Wary/Alienated/Antagonist) and pledge penalties.
- `LEKMOD_OPEN_BORDERS_INDEFINITE`: second open-borders deal item that lasts until war.
- `LEKMOD_MULTIPLE_DEAL_PROPOSALS`: several open deal offers at once; a deal that became impossible fails with a notification.
- `LEKMOD_MIDTURN_PICK_NOTIFICATIONS`: policy/belief pick notifications during the turn.
- `LEKMOD_RANDOMIZE_CITY_NAMES`, `LEKMOD_HIGH_CONTRAST_CIV_COLORS` (lobby Civ Colors), `LEKMOD_WAR_START` (+ `LEKMOD_WAR_START_PEACE_TURN 20`), `LEKMOD_WONDER_TIE_RULES` (same-turn wonders Neither/Both).
- `LEKMOD_AIR_COMBAT_FEEDBACK` (floating damage, "No resistance"), `LEKMOD_UNIT_ATTACKED_FLAG_ICON`.
- `LEKMOD_POLICY_GARRISON_ATTACH_TURN 70`, `LEKMOD_BARBARIAN_KILL_YIELDS_END_TURN 70`, `LEKMOD_RUIN_CHOICE`.
- `LEKMOD_UNIT_COMBAT_ATTACK_DEFENSE_MODS` (UnitPromotions_UnitCombatMods.Attack/Defense; both strength code paths), `LEKMOD_IMPROVEMENT_YIELD_PER_OWNER_ERA` (Improvement_YieldPerOwnerEra; refresh on era change in CvTeam::SetCurrentEra), `LEKMOD_NAVAL_PENALTY_PROMOTIONS` (Blind Spot/Minimum Range/Docked, looked up from promotions without saved unit fields).
- `LEKMOD_RESOURCE_CITY_EFFECTS` (Resources columns `ImprovementBuildTimeChange`, `FoundCity*`, `CityCenter*`: Gems/Perfume build time, Salt/Stone/Cattle/Rubber/Marble settle-on), `LEKMOD_NATURAL_WONDER_EFFECTS` (feature tables, see §4).
- Older ones from the port: ruins overhaul (`LEKMOD_NEW_ANCIENT_RUIN_REWARDS`), kill-yield era fix, Amphibious, Carpet Bombing, Iaijutsu/Hatamoto (see below).

### Behaviour and decisions to remember
- **Policy garrison effects from turn 70** (`LEKMOD_POLICY_GARRISON_ATTACH_TURN`): policy garrison yields and garrison happiness (Military Caste) work in every city from turn 70; building garrison yields still need a unit. Piety's and Tradition's garrison effects should use the same mechanism.
- **Turn 70 is the user's "stop the annoying early-game chores" point** (2026-10-08): garrison effects attach to cities, and barbarian kills stop giving yields (`LEKMOD_BARBARIAN_KILL_YIELDS_END_TURN`). Use the same turn for similar rules.
- **Luxury resources always yield at least 1 Gold unimproved** (user rule, 2026-10-08). If a change would drop it to 0, keep 1 and take the difference off the improvement instead, so the improved tile stays as specced.
- **Heal Instantly = 25 HP**, set by the `INSTA_HEAL_RATE` define in `CIV5Units.xml` (the DLL reads it; no rebuild needed).
- **Naming:** the bomber line `PROMOTION_AIR_SIEGE_1..3` displays as "Air Siege I–III" (renamed, text only). The melee/gun `PROMOTION_SIEGE` displays as "Siege". Bombardment exists for both bombers and naval units. Air Siege I is the bombers' Bunker Busting prerequisite (user-approved).
- **Carpet Bombing** (bombers, after Bombardment II): splash hits enemy units on tiles *adjacent* to the target, with `-X` floating text. No friendly fire (**this deviates from the spec**, which includes friendly units and CS war declarations; the user keeps it this way for now and will revisit after real-game playtests, 2026-10-07), and no splash on the target city's garrison (user decision). Air units' range-attack missions (e.g. from the "declare war?" popup) are routed through `CvUnitCombat::AttackAir` in `CvUnitMission.cpp`; before that they skipped all air logic, including interception.
- **Iaijutsu**: column `ExtraAttackVsFullHP`. In `ResolveMeleeCombat`, if the defender was at full HP before the attack, one attack is refunded (`CvUnit::RefundAttack`), once per turn; the flag resets in `CvPlayer::DoUnitReset`. Depends on `NQ_UNIT_TURN_ENDS_ON_FINAL_ATTACK` (on).
- **Hatamoto**: column `MovesNearGeneralChange`. +N moves in `DoUnitReset` when a friendly Great General is on the same or an adjacent tile (`CvUnit::IsGreatGeneralWithinOne`).
- Iaijutsu and Hatamoto are lost on upgrade, and their new `CvUnit` members are serialized (old saves are incompatible). One Good Eye and Stargazing are `VisibilityChange` 1, like Scouting I.
- **Amphibious**: I = flat embark cost, II = flat disembark cost, and I and III each add +1 to `MaxMovesAfterDomainChange` (it sums: with I–III, at most 2 MP are left after a domain change). The flat cost is 1 MP, capped so that at most that many MP remain (in both cost functions). `ConsumesAllMoves` lets flat-cost transitions through, and `CvUnit::move` skips `finishMoves()` for them. Walk-water tiles (pontoons, shallows) count as land on both sides of the check.
- **Ruin pool** (`HandicapInfo_Goodies`): CULTURE, GOLD, MAP, TECH (= the science ruin), UPGRADE_UNIT, FOOD, RANDOM_FAITH, TILE_GROW, EXPERIENCE_MOVE, PANTHEON_FAITH, and since 2026-10-08 GOODY_LEKMOD_TRADE (listed twice = double weight) and GOODY_LEKMOD_ANCIENT_TECH. SETTLER and WORKER are only in the Settler-difficulty pool.
  - Science ruin (2026-10-08): 20–30 × era science (max 90), half of it as Gold (rounded to 5), the unit takes 3× the science as damage (keeps 1 HP), no XP. Upgrade ruin: 20 damage.
  - PANTHEON_FAITH: only without a pantheon and with 0 Faith. RANDOM_FAITH (`ReligionFaith`) requires a pantheon. PROPHET_FAITH stays out of the pool, so edits to it are dead.
  - The Mobility "ancient only" limit is `BeforeEra=1` on `GOODY_EXPERIENCE_MOVE`.
  - `GoodyHutPopup.lua` (template `Lua\tmp\ui\AncientRuins\GoodyHutPopup.lua.ignore`) has a generic branch that shows the DLL-passed amount (`Data2`).
  - **Ruin choice** (`LEKMOD_RUIN_CHOICE`, 2026-10-08): `CvPlayer::doGoody` rolls 2 offers (3 with Native Tongue = `PROMOTION_GOODY_HUT_PICKER`) with the synced RNG on every machine and stores them per plot (`m_aiLekmodPendingRuins`, saved). One roll 0-999 per offer drives all its numbers; `CvPlayer::LekmodGoodyRand` replays it inside `receiveGoody`, so the popup text and the result always match. Any new rolled ruin value must use `LekmodGoodyRand` and get a branch in `LekmodGetRuinOfferText`. The choice arrives through `Network.SendGoodyChoice` → `LekmodChooseRuinOffer`; AIs pick at random; leftovers resolve in `doTurn`. The result popup only shows in single player (base-game rule).
- **Shoshone choose popup:** taller rows (78 px) were tried and reverted because players had to scroll. Choose entries (`ChooseDescription`) are one-liners; result popups (`Description`) keep the narrative texts.
- **Icons:** Glutton = `ABILITY_ATLAS` 57, the base "May Not Melee Attack" icon (user decision; the original art is lost). Feared Elephant uses the user's icon (`LEKMOD_FEARED_ELEPHANT_PROMOTION_ATLAS`). Envelopment and Bunker Busting have the user's new art. The reshape procedure is `civ-tools\reshape_icons.py <src_dir> <out_dir> name…`.

### Other fork branches (found 2026-10-06, unreviewed)
- `dev-bruno` (user, 144 commits, 2026-04-07 → 07-17; based on the 04-07 merge `1cd27eaa`):
  - 67 commits touching C++, with **no DLL ever rebuilt**
  - promotions, including new ones like Duck, still only in Art XML
  - the ruins draft still present
  - naval rework (Ship of the Line, Dreadnought, Quinquereme…), wonders, beliefs, city-state quests, policies
  - the user's Notion specs: open borders 10 turns (`40209953`), prophets killed on capture (`7fe60c6c`), trade routes 15 turns (`2cdc2fff`)
  - its own `changelog.txt` and `ai_ground_truth_workflow.md`
- `dev` / `stratresourcechanges` (**kubugaming**, June): policy work, an improvement-tourism table, a kill-yield fix, one commit marked "[BUGGED]". Excluded by user decision (§1).
- `civ-changes-bruno` (user, Feb): 8 civs (Huns, Egypt, Babylon, Gauls, Israel, China, Jerusalem, Aksum).
- `interface-bruno` (user): found 2026-10-07, not reviewed yet.

### History (old fork, 2026-10-05/06; details in `lekbuild` branch `repair-batch-1`)
- 16 repair commits on Ashwin's fork HEAD `a582fdf9`: compile fix (`REPLAY_MESSAGE_CHAT` define clash), ruins repair (hardcoded draft removed, values moved into `GoodyHuts` columns), kill-yield era fix, Amphibious, Carpet Bombing, Iaijutsu/Hatamoto, data and text migrated out of `Art\` XML, icons, gold ruin floating text, faith ruin rebalance, Demographics fixes, DLL rebuilds. All of it was ported (above).
- **Verified in game on the old fork:** Envelopment; ruins (faith, culture, upgrade, border expansion); Zealot icon and faith, including after another promotion (era-flag fix, tested together with the user); Bunker Busting (siege); Sortie; Amphibious river bonus and disembark cap; Repair Crew; Mountaineering.
- The upstream sync assessment (a trial `git merge-tree`) predicted the port's conflicts correctly. Its lessons are in §2 "Git notes" and the port resolutions above.
