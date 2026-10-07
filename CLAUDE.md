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
     - Player-facing lines: the summary, `- Added:`, `- Changed:`, `- Removed:`, `- Fixed:`. Write them for players (effects and numbers, no internal field names if avoidable).
     - Developer-only lines: `- Note:`, `- DLL:`, `- Dev:` (skipped by the website).
     - Tag vocabulary (extend deliberately, and update the file header too): promotions, units, civs, policies, religion, ruins, combat, movement, naval, air, game mechanics, world congress, ui, art, bugfix.
     - Update an item's existing section rather than adding a duplicate.
3. **Lekmod + quick speed always.**
   - Many things are defined in the base game and then overwritten by Lekmod. Always check the final, loaded value (§6).
   - Spec numbers are **quick-speed** numbers, while the code and data usually hold **standard-speed** values that the game scales by game speed. Convert, and check how each formula scales.
4. **This file is the ground truth doc.**
   - The user's earlier `ai_ground_truth_workflow.md` exists on branch **`origin/dev-bruno`** (repo root, Apr 19–21). It is not on main.
   - It has useful rules: the Override files are the authority, belief DLL wiring steps, a yield audit order, quick = 67% of standard, natural wonder notes.
   - It also contains a load-order claim that is probably wrong (see §3).
   - Merge its still-valid content into this file when `dev-bruno` is integrated.
   - Keep it current.
   - When you come across something that should be documented here, or that contradicts this file, propose the amendment.
5. **Spec vocabulary:**
   - **"(from scratch)" / "(new)"**: none of the item's old effects or yields persist. Remove everything old, then add the spec.
   - **"NEW"**: an entirely new item that doesn't exist in the code yet, or exists only as disconnected leftovers of an unfinished implementation.
   - **No marker**: the spec adds to the existing item, or overwrites a value when it's functionally the same effect.
6. **Specs live in Notion** ("LEK — v3 — implementation checklist" and its section pages; agreed 2026-10-07):
   - Items **not yet implemented**: the user edits the spec freely. The spec as it reads at implementation time counts. Record what was implemented in the changelog and commit.
   - Items **already implemented**: the user doesn't edit the spec in place, but adds a "CHANGE (date): …" note under the item (or tells Claude). Look for these notes.
   - Don't edit the user's spec pages unless asked. Claude's own pages (audit, tracker) are sub-pages of the checklist.

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
| `C:\Users\bbruno\civ-tools\lekmod_on.bat` / `lekmod_off.bat` | The user's mod switch. They create or remove the junction only, never the repo. `on` also runs `ui_check.bat`. `lekmod_setup_link.bat` was the one-time setup that moved the old folder to `civ-tools\WIP_LEKMOD_backup_2026-10-07`. |
| `C:\Users\bbruno\civ-tools\lek\` | **The working repo**: a full clone of `brunotho/Lekmod`, branch `dev`. Remotes: `origin` (the user's fork), `upstream` (EAP), `old` (= `lekbuild`, reference). DLL builds run here (short path, §5). |
| `C:\Users\bbruno\civ-tools\lekbuild\` | Old sparse checkout of Ashwin's fork. Branch `repair-batch-1` holds the 2026-10-05/06 repairs. **Reference only** since the port. |
| `C:\Users\bbruno\Desktop\civ mods\WIP_lekmod_full_repo\` | The user's own full checkout of the fork (all folders). Untouched by Claude so far. |
| `C:\Users\bbruno\civ-tools\` | Tools: `texconv.exe`, `7zip\7z.exe`, `vs2008\` (installer source), `dll_backup\` (previous DLLs). |
| `Documents\My Games\Sid Meier's Civilization 5\Logs\` | Game logs (§6). Logging is enabled in `config.ini` (`LoggingEnabled = 1`). |
| `Documents\My Games\Sid Meier's Civilization 5\cache\` | The loaded game database as SQLite (§6). |

Repo layout (GitHub): `LEKMOD/` (the mod), `LEKMOD_DLL/` (C++ source), `Lekmap/` (map script, a separate download into `Assets\Maps`), `LekmodInstaller/`, `docs/`, `.github/workflows/ci.yaml` (upstream's automated DLL build).

This file lives at the **repo root** (`civ-tools\lek\CLAUDE.md`), so it doesn't ship to players. Start Claude sessions in `civ-tools\lek`. A session started in the game folder won't see this file.

**Generated UI:** `ui_check.bat` writes `LEKMOD/Lua/UI/` and `LEKMOD/*.bak`, and both are git-ignored. Always run it **through the junction** (`DLC\WIP_LEKMOD\ui_check.bat`): it looks for EUI in the folder above itself.

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
- **Promotion IDs are explicit** (`<ID>`). Every row in the `UnitPromotions` section has one. New rows get the next unused ID: currently up to **364**. v35.4 uses IDs up to 343; ours are 344–364. Upstream's IDs already have gaps (e.g. 271–273), which is fine. Check uniqueness *within the section*, since other tables reuse the same numbers.
- **Line endings: both Override files are LF.** When scripting edits, read and write **bytes** (`open(f,'rb')`). Text mode silently converts line endings.
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
- Promotion icons: 4 sizes (256/64/45/32), DXT5 `.dds`, **transparent background**; the game draws the round frame. See §7.
- C++ feature switches live in `LEKMOD_DLL/CvGameCoreDLL_Expansion2/_Defines.h` (e.g. `LEKMOD_NEW_ANCIENT_RUIN_REWARDS`, `FULL_YIELD_FROM_KILLS`, `LEKMOD_RELOCATE_PROMOTION_PREREQ_ORS`). Check which are on before reasoning about code paths.
- Lekmod-specific tables worth knowing:
  - `UnitPromotions_PromotionPrereqOrs`: a missing referenced promotion is silently skipped through an INNER JOIN.
  - `UnitPromotions_YieldFromKills` and `UnitPromotions_KillYieldValidEras`: promotion yields from kills. A promotion yields nothing unless the killed unit's era is listed.
  - `UnitPromotions_UnitCombats`, `Unit_FreePromotions`, `Policy_FreePromotions`: how promotions become obtainable.

## 5. Building and installing the DLL
**Toolchain:** Visual C++ 2008 Express SP1 (`C:\Program Files (x86)\Microsoft Visual Studio 9.0\`).
- It was installed from archive.org's `VS2008-Express-w-SP1.ISO`, which upstream CI also uses.
- Running setup from the mounted ISO fails; it works from the **7-Zip-extracted** copy in `civ-tools\vs2008\VCExpress\setup.exe /q`.
- The install also added an unneeded SQL Server 2005 Express service.

**Build** (PowerShell):
```
Set-Location C:\Users\bbruno\civ-tools\lekbuild
& "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\vcpackages\vcbuild.exe" "LEKMOD_DLL\CvGameCoreDLL_Expansion2\CvGameCoreDLL_Expansion2.vcproj" Release *> C:\Users\bbruno\civ-tools\build_release.log
```
- Takes a few minutes. Run it in the background. "0 error(s)" with ~780 warnings is normal.
- Output: `LEKMOD_DLL\CvGameCoreDLL_Expansion2\BuildOutput\VS2008_ReleaseWin32\CvGameCore_Expansion2.dll`.
- VS2008 has a **~260-character path limit**, so the checkout must stay at a short path. The scratchpad path is too long.
- Fork HEAD does not compile as-is. Ashwin's June commit enabled `#define REPLAY_MESSAGE_CHAT 7` in `_Defines.h`, which clashes with the enum entry in `CvEnums.h`. It's commented out again in `lekbuild`.

**Install:**
1. Civ V must be **closed**; the DLL is locked while the game runs. Ask the user, and never kill the game.
2. Back up the current DLL to `civ-tools\dll_backup\`, then copy the new one into `WIP_LEKMOD\` and compare md5 checksums.
3. Start a **new game** for every test. Old saves break when the DLL adds saved fields.

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

**Debugging lesson:** twice a confident conclusion was wrong. "Zealot will work" was wrong; "the ruins aren't changed at all" was half wrong, because the C++ computed the effects. When the user's observation conflicts with your model, find a direct measurement (database, log, diagnostic) before arguing.

## 9. Status (update as things change)
**Port to v35.4 (2026-10-07)**, in `civ-tools\lek`, branch `dev`: 6 commits on upstream `201df6c5`. **Not pushed, not installed yet.**
1. ruins overhaul
2. kill-yield fix (still an upstream bug; a candidate to offer EAP)
3. Demographics
4. promotion batch
5. changelog
6. DLL (0 errors)

How the port was done:
- Branch `port-src` = `old/repair-batch-1` with Ashwin's 7 World Congress commits reverted, and the dead `Art/` XML/modinfo edits and the DLL binary dropped.
- That branch was squash-merged onto v35.4 and committed by theme with `stage_hunks.py` (which now has `--range A-B`).
- Ashwin's 2 June commits needed nothing: their C++ was inside the deleted ruins draft, and the rest was `Art/` wiring.

Resolutions worth knowing:
- **`PillageChange`**: v35.4 added the same promotion field with the same meaning (% bonus to pillage gold, used by Buganda). Our duplicate was removed, and Marauder uses theirs. Git merged the duplicate *silently*, so after an upstream merge, check for doubled members and columns.
- **Promotion IDs** renumbered +4 to 344–364.
- **Heal while embarked**: allowed by `IsHealWhileEmbarked()` OR Buganda's `IsEmbarkedMissionAllowed(MISSION_HEAL)`. This is in both `CvPlayer::DoUnitReset` and `CvUnit::canHeal`.
- **Embarked defense** (40% of max(melee, ranged) strength) re-applied inside upstream's moved `GetEmbarkedUnitDefense`.
- **Sortie**: v35.4 computes all combat damage in `CvGame::getCombatDamage(CvCombatInfo&)`. The sweep reduction now lives there.
- Fixed while porting: the Pictish Warrior tooltip used the invalid `[ICON_FAITH]`.
- `sed -i` in Git Bash strips CRs from CRLF files. Use Python byte I/O, or check line endings afterwards.

**Everything below describes the old fork's state (pre-port). The game folder still runs that state until the port is installed.**

**In the game folder (untracked; previous versions backed up in the session scratchpad):**
- `CIV5Units.xml` / `CIV5Units_Mongol.xml`, new promotion rows:
  - PROMOTION_ZEALOT (ID 340, valid in all eras for kill yields)
  - PROMOTION_ENVELOPMENT (341)
  - PROMOTION_GLUTTON (342)
  - 14 April promotions (343–356): Amphibious I–III, Bunker Busting, Repair Crew, Supply Ship, Sambuca, Carpet Bombing, Discipline, Discipline (Air), Fear Aura, Marauder, Mountaineering, Swift Transport. Discipline uses new keys `TXT_KEY_PROMOTION_LEKMOD_DISCIPLINE(_HELP)`.
- Ruin values migrated into the `GoodyHuts` rows. The Mobility "ancient only" limit is on `GOODY_EXPERIENCE_MOVE` (`BeforeEra=1`).
- `Lua\UI\GoodyHutPopup.lua`: a generic branch shows the DLL-passed amount (`Data2`).
- Zealot icons reshaped (originals in scratchpad `backup/icons`).
- `CvGameCore_Expansion2.dll` = the build from `lekbuild` (ruins-repair).

**COMMITTED (2026-10-05)** in `civ-tools\lekbuild`, local branch **`repair-batch-1`**: 9 commits on top of fork HEAD `a582fdf9`. **Not pushed.**
1. compile fix
2. ruins repair
3. kill-yield era fix
4. Amphibious
5. Carpet Bombing
6. Iaijutsu/Hatamoto
7. data & text (Override files)
8. icons
9. rebuilt DLL

The checkout's sparse set is `LEKMOD/`, `LEKMOD_DLL/` and `changelog.txt`. Its `LEKMOD/` was verified identical to the game folder, apart from the generated `Lua/UI` and this file.

Committing lessons:
- **Never commit the game folder's `Lua/UI/`.** The repo tracks only a few files there; the rest is `ui_check.bat` output. Commit the templates in `Lua/tmp/`.
- To split one file's changes into several commits, use `civ-tools\stage_hunks.py <file> <regex> [--invert]`. It uses 3-line context; zero-context hunks (`-U0` + `--unidiff-zero`) misplaced inserted lines once. Verify after staging with `git diff -U0` that what remains is exactly what you expect.
- Git here has `core.autocrlf=true`, while the game folder's text files are LF. Compare with `diff --strip-trailing-cr`.

Follow-up commits (2026-10-06):
10. changelog format (tags, release block)
11. gold ruin floating text fix
12. faith ruin rebalance:
    - `GOODY_PANTHEON_FAITH` re-added to the pool (upstream had it commented out in `HandicapInfo_Goodies`).
    - `GOODY_RANDOM_FAITH` now has `ReligionFaith`, so it requires a pantheon.
    - The prophet ruin stays disabled.
13. rebuilt DLL

**Fork branches NOT in main (found 2026-10-06), all unreviewed:**
- `dev-bruno` (user, 144 commits, 2026-04-07 → 07-17; based on the 04-07 merge `1cd27eaa`, so it lacks Ashwin's June commits and our repairs). Contents:
  - 67 commits touching C++, with **no DLL ever rebuilt**.
  - promotions, including new ones like Duck, still only in Art XML
  - the ruins draft still present
  - naval rework (Ship of the Line, Dreadnought, Quinquereme…), wonders, beliefs, city-state quests, policies
  - the user's Notion specs: open borders 10 turns (`40209953`), prophets killed on capture (`7fe60c6c`), trade routes 15 turns (`2cdc2fff`)
  - its own `changelog.txt` and `ai_ground_truth_workflow.md`
- `dev` / `stratresourcechanges` (**kubugaming**, the third contributor, June): policy work (Tradition, Liberty, Honor, Eminence, Order "Re-education" / "Monuments of the People"), an improvement-tourism table, "Fixing the yield from kills bug" (compare with our kill-yield fix), and one commit marked "[BUGGED]" (strategic resource costs).
- `civ_changes` (user, Feb): 7 civs (Huns, Egypt, Babylon, Gauls, Israel, China, Jerusalem).
- The user's planned rebase onto upstream must decide which of these come along. Each needs the same treatment as main: check where the data lives, compile, test.

**Upstream sync assessment (2026-10-06)**, a trial merge via `git merge-tree` in lekbuild (remote `upstream` added). Nothing was changed.
- Divergence: upstream 100 commits (v34.12 → v35.4, 2026-10-01); ours 55 (39 fork + 16 repair).
- Upstream's `CIV5Units.xml` was compacted: ~35k default-value lines (`>false<`, `>0<`) were removed, with roughly the same row counts. So line diffs look huge but the content barely changed.
- Upstream also reworked combat and UI (`GenerateRangedCombatInfo` removed, air sweep rewritten), added new civs (Buganda, Mali), a trade refactor and World Congress changes.
- 20 files are changed by both sides. 15 merge automatically and 5 conflict:
  - **The DLL binary:** rebuild.
  - **`CIV5Units.xml`:** 6 blocks, all end-of-list appends (columns, atlases, promotion rows). Keep both sides.
  - **`CvPlayer.cpp` + `CvUnit.cpp` heal-while-embarked:** combine our `IsHealWhileEmbarked()` with upstream's Buganda `IsEmbarkedMissionAllowed` trait.
  - **`CvUnit.cpp` `GetEmbarkedUnitDefense`:** upstream moved it (still era-based). Drop our old copy and re-apply the 40% formula in theirs.
  - **`CvUnitCombat.cpp`:** the Sortie air-sweep change has to be re-applied inside upstream's rewritten `GenerateAirSweepCombatInfo(CvCombatInfo*)`.
- **Hidden issues that don't show up as conflicts:**
  - Upstream added promotions with **IDs 340–343** (Buganda ×2, Mali, No-fortify-vs-ranged). Ours (340–360) must be renumbered to 344+.
  - Upstream removed Anti-Naval 1–3. The Mobility prerequisite that references them is harmless (INNER JOIN skip).
  - World Congress vote code changed on both sides and merged textually. Review it during the WC rework.
- Our compile fix is moot upstream (the define is already commented out there). Upstream **still has the kill-yield era bug**, so offering our fix is a candidate.
- Estimate: about one evening for the merge, ID renumbering, rebuild and a retest checklist. Prefer a **merge** over a rebase, because rebasing 55 commits would replay the conflicts repeatedly.

**History of the uncommitted work before that (now all in the commits above):**
- `_Defines.h`: REPLAY_MESSAGE_CHAT define commented out.
- `CvPlayer.cpp`:
  - removed the hardcoded ruin draft (kept its HealWhileEmbarked hunk)
  - NO_TECH guard on the science ruin
  - `iEraRuinValue` feeds the popup
  - killed units with era −1 treated as ancient
- `CvUnit.cpp`: kill-yield era flags are now an OR over held promotions (previously any promotion change overwrote them).
- `CvUnitMovement.cpp`: Amphibious flat embark/disembark cost now leaves `MaxMovesAfterDomainChange` MP (was 0). Fixed in both cost functions.

**Playtest round 2 (2026-10-05):**
- Works: Bunker Busting (siege), Sortie change, Amphibious river bonus, Repair Crew, Mountaineering.
- Fixed afterwards:
  - Bunker Busting for bombers (prerequisite → `PROMOTION_AIR_SIEGE_1`; the exact tier was chosen by Claude, so confirm with the user)
  - Amphibious movement
  - tooltips for Coastal Raider I–III, Boarding Party I–III, Heal Instantly, Sambuca and Amphibious I–III
- Carpet Bombing "didn't show up", but its data wiring is correct (bombers, after Bombardment II). Still to confirm whether the test bomber had Bombardment II.
- Naming trap: the bomber line `PROMOTION_AIR_SIEGE_1..3` *displays* as "Siege I–III", while the melee/gun `PROMOTION_SIEGE` displays as "Siege". Bombardment exists for both bombers and naval units.
- Design changes from the user: Heal Instantly = **25 HP** (the `INSTA_HEAL_RATE` define in `CIV5Units.xml`; the DLL reads it, no rebuild needed). Tooltips must not contain spec notes ("Eligible: …", "Requires …"); removed from Supply Ship, Sambuca and Discipline.
- The `GoodyHutPopup.lua` fix is synced into `Lua\tmp\ui\AncientRuins\GoodyHutPopup.lua.ignore`.
- Line breaks applied to all fork-touched promotion tooltips and the ruin texts written by Claude.

**Round 3 (2026-10-05):**
- User decisions:
  - Bomber line renamed to "Air Siege I–III" (text only).
  - Air Siege I is fine as the Bunker Busting prerequisite.
  - Unobtainable promotions stay as they are; they get reworked with a later policy batch.
  - World Congress fixes are deferred to a full rework.
- Amphibious:
  - Disembark cap verified working.
  - Embark was still ending the turn: `CvUnit::move` calls `finishMoves()` after every embark. Fixed: skipped when `IsEmbarkFlatCost()`. Needs a retest.
  - The **movement preview** after disembark reportedly shows the uncapped moves. The UI pathfinder (`UIPathAdd` → `PathAdd` → `MovementCost(..., iStartMoves)`) looks correct in code. Retest with the new DLL; if still wrong, get an exact description from the user.
- Carpet Bombing:
  - The splash did exist for city targets, but it was invisible (no floating text) and also hit the attacker's own units.
  - Fixed: no friendly fire, and `-X` popup text added. Note: the splash hits units on tiles *adjacent* to the target, not the city's own garrison.
- Ruin pool reality (loaded `HandicapInfo_Goodies`): CULTURE, GOLD, MAP, TECH, UPGRADE_UNIT, SETTLER, WORKER, FOOD, RANDOM_FAITH, TILE_GROW, EXPERIENCE_MOVE.
  - **PANTHEON_FAITH and PROPHET_FAITH are not in the pool**, so edits to them are dead.
  - Shoshone choose-menu texts (`ChooseDescription`) were updated for tech, gold, upgrade, map, faith and food. The tech result text was rewritten as "dangerous ruins" flavour.
- Skeleton promotions (Hatamoto, Iaijutsu, One Good Eye, Stargazing): the user wants them filled in. **No spec exists anywhere** (changelog, commits); the effects must come from the user.

**Round 4 (2026-10-05):**
- User-provided specs, now implemented:
  - **Iaijutsu** (ID 357): new column `ExtraAttackVsFullHP`. In `ResolveMeleeCombat`, if the defender was at full HP before the attack, the attacker gets one attack refunded (`CvUnit::RefundAttack`), once per turn. The used flag resets in `CvPlayer::DoUnitReset`. Depends on `NQ_UNIT_TURN_ENDS_ON_FINAL_ATTACK`, which is on.
  - **Hatamoto** (358): new column `MovesNearGeneralChange`. +N moves in `DoUnitReset` when a friendly Great General is on the same or an adjacent tile (`CvUnit::IsGreatGeneralWithinOne`).
  - Both promotions are lost on upgrade.
  - **One Good Eye** (359) and **Stargazing** (360): `VisibilityChange` 1, the same as Scouting I.
  - All four are `CannotBeChosen` with **no grant yet**. Ask the user which units get them.
  - New `CvUnit` members are serialized, so old saves are incompatible.
- Carpet Bombing + "declare war?" popup:
  - The popup sends `MISSION_RANGE_ATTACK` → `AttackRanged` → `ResolveRangedUnitVsCombat`, which has no air logic (no Carpet Bombing, and no interception either).
  - Fix in `CvUnitMission.cpp`: air units' range-attack missions now go through `CvUnitCombat::AttackAir`.
  - Per the user, garrison units in a targeted city should **not** take splash damage (current behaviour).
- Glutton icon = `ABILITY_ATLAS` 57, the base "May Not Melee Attack" icon (user decision; the original art is lost).
- Shoshone choose popup:
  - Taller rows (78 px) were tried and then **reverted**, because players had to scroll.
  - Rule now: **choose-menu entries (`ChooseDescription`) are one-liners**, matter-of-fact, with at most a small flavour blip when it fits. No `[NEWLINE]` there.
  - Result popups (`Description`) keep the narrative texts.
- Mobility ruin (`GOODY_EXPERIENCE_MOVE`) has `ExcludeUnitClass = UNITCLASS_SCOUT`, which includes the Shoshone Pathfinder. That's why it is rarely or never offered when scouts pop ruins. Whether to keep this is open with the user.
- Icons:
  - The user's new Envelopment and Bunker Busting art (from Downloads) is reshaped and installed.
  - Feared Elephant now uses the user's icon (`LEKMOD_FEARED_ELEPHANT_PROMOTION_ATLAS`; it was `ABILITY_ATLAS` 59).
  - The reshape procedure is saved as `civ-tools\reshape_icons.py <src_dir> <out_dir> name…`.
- Deferred by the user to final tuning ("interface tuning at the very end"): a 2-row promotion display in the unit panel. The row is a fixed 260×26 box (~10 icons) inside `Expansion2\UI\InGame\WorldView\UnitPanel.xml`; it needs an XML override.

**Verified in game:**
- Envelopment works.
- Ruins: faith, culture, upgrade and border expansion work.
- Zealot icon and faith work; faith-after-another-promotion was still broken before the era-flag fix.

**Open / not yet verified:**
- Era-flag fix (Zealot after a level-up) and the 14 migrated promotions need a playtest.
- Ruins not yet tested: food+Glutton, tech→science, map 75%, gold+barbarian, pantheon (faith = 0 only), Mobility after the ancient era.
- **Not obtainable in game** (nothing grants them; their commits say "policy/UU-granted", but that was never wired): Discipline, Discipline (Air), Fear Aura, Marauder, Swift Transport. Wiring them is a design decision for the user.
- Empty skeletons (no effects, not migrated): Hatamoto, Iaijutsu, One Good Eye, Stargazing.
- World Congress:
  - The `NumMinorExtraLeagueVotes` column (XML) vs `NumMinorBonusVotes` (C++) name mismatch.
  - The vote-source tooltip doesn't list the new sources.
  - `TXT_KEY_LEAGUE_SPECIAL_SESSION_INFO` has no text.
- Remaining icons need reshaping; three promotions need new art.
- (Superseded: repo strategy, commits and this file's location are settled; see §1, §2 and "Port to v35.4" above.)
