# Art sources and conversion (Lekmod custom art)

This folder holds the **original** art behind every custom Lekmod image, plus the tools that turn it into the
game files. It is not part of the mod download (players only get `LEKMOD/`). The rule: never edit the game files in
`LEKMOD/Art/...` by hand; change the source or the tool here, then rebuild.

## Folder layout

| Path | What |
|---|---|
| `promotions/manifest.csv` | One line per custom promotion icon: name, source file, symbol size (`scale`), `key` (`border` or `all`, see step 2), notes. **The single place to look up where an icon comes from.** |
| `promotions/original_ai_2026-04/` | The April 2026 AI-made icons (256 px, opaque dark background), recovered from git (`fde09fce^`). Amphibious I-III here are superseded by the user art. |
| `promotions/user_art/` | Art the user supplied later: Envelopment and Bunker Busting (2026-10-05, 256 px), Sitting Ducks (64 px), Amphibious I-III and Nuke Resistance (45 px PNG, 2026-10-10). |
| `promotions/superseded/` | Earlier user versions that were replaced (kept for reference). |
| `units/vanguard_corps/` | Vanguard Corps portrait (user, square, 256 px) and map flag source (`White Fortress Watchtower Icon.png`). |
| `menu_backgrounds/` | The 11 main menu paintings (PNG) and the original Great Wall background (already a DDS). |
| `tools/` | `build_promotion_icons.py` (the whole promotion pipeline), `reshape_icons.py` (background key-out). |

## Promotion icons

### Where the game shows them
- **Promotion choice** (unit panel, when a promotion is ready): 64 px (45 px on small screens). The game draws a round frame around the icon, so the icon itself is a **gold glyph on transparency**.
- **Earned promotions** next to the unit portrait: **32 px, no frame**. The base game draws these as the gold glyph on a **blue square tile** (`PromotionSquare32`). Without the tile our icons vanished into the dark panel.
- **Civilopedia**: 256 px.

### Building (one command)
From the repo root: `python art_sources/tools/build_promotion_icons.py [name ...]` (no names = all).
Preview without writing: add `--preview out.png`. Needs Pillow and `texconv.exe` (`civ-tools\texconv.exe`, or set `TEXCONV`).
It writes `LEKMOD/Art/Promotions/<name>_{256,64,45,32}.dds`. The atlas rows (`IconTextureAtlases`, one 1x1 atlas per icon,
e.g. `LEKMOD_NUKE_RESISTANCE_PROMOTION_ATLAS`) and the promotion's `IconAtlas`/`PortraitIndex` are in `LEKMOD/Override/CIV5Units.xml`.

### Pipeline steps and why
1. **Upscale the source to 256 px.** Sources come in 45, 64 or 256 px. A small source makes the 256 px (Civilopedia) image soft; ask for 256 px or larger art when possible.
2. **Key out the background** (`reshape_icons.reshape`): only background **connected to the image border** becomes transparent, so dark details inside the glyph (eye patch, skull eyes) stay. With `key=all` in the manifest, enclosed dark areas are cleared too (outline shapes, e.g. the Nuke Resistance shield, whose inside would otherwise show as a dark patch on the 32 px tile). The glyph test is "max(R,G) > 90" (gold); edges get a soft alpha.
3. **Crop and fit the glyph** to `scale` x 256 px (0.72 normally, leaves room for the round frame). Nuke Resistance uses 0.80 because its trefoil detail was lost at 0.72.
4. **Even out the gold**: the AI art had baked-in lighting (bright top-left, darker orange right/bottom), which looked thin and weak on the right at 64 px. Gold/orange pixels (hue 25-60 deg, saturated) are lifted to the same brightness (V 0.97, hue at least 42 deg); dark details are untouched.
5. **Shift 8 px right** (2 px at 64 px): in the promotion choice the icons looked 1-2 px too far left.
6. **Write the sizes**: 256 px as BC3 (DXT5) with mips; **64/45 px uncompressed** (B8G8R8A8, one mip). BC3 compresses 4x4 pixel blocks and smeared fine detail at small sizes (very visible on Nuke Resistance); uncompressed small files are only 8-16 KB and use the same DDS format as the menu background, which the game reads.
7. **32 px tile**: the glyph (from the 256 px result) on a blue square tile (box 4,5-27,28; navy-to-teal gradient, lighter 1 px edge), uncompressed.

### Tried and rejected (2026-10-10)
- Blue-recoloured glyph on the 32 px tile: the base game keeps the gold glyph at every size.
- Thickening strokes ("bolding") of thin AI art: helps a little, but close lines merge; better to get bold art. What works at 45-64 px: 2-3 thick shapes, wide spacing, no fine detail, solid gold (Envelopment is the reference).

### Adding a new promotion icon
1. Put the source in `promotions/user_art/` (best: 256 px or larger, gold glyph on a plain dark background, bold and simple).
2. Add a line to `promotions/manifest.csv`.
3. Run the build for that name; check the preview first.
4. Add the 1x1 atlas rows (256/64/45/32) and point the promotion's `IconAtlas` at it (`PortraitIndex` 0).

### Re-running everything with a better process
Change the tool, run `--preview` for all icons, compare with the current files, then build all. The build always starts
from the sources, so it can be run any number of times (nothing gets shifted or evened twice).

## Unit art (Vanguard Corps)
- **Portrait** (unit panel, Civilopedia): the square source is resized to a 173 px circle at (41,42) in a 256 px cell (the layout of all Lekmod unit portraits), then 256/128/80/64/45/32 px, BC3. Built by a one-off script on 2026-10-10 (see the session notes in CLAUDE.md §7); the source is in `units/vanguard_corps/`.
- **Map flag**: a white silhouette on transparency, scaled to 18 px tall, placed at x = centre + 2 px, y = 4 px in a 32 px canvas (it must stay inside the tapering flag shape), BC3 with one mip. The game tints it in the player's colours.

## Building icons
- Sources: `buildings/<name>/<name>_<size>.dds` as delivered by the user (OneDrive art inbox, see CLAUDE.md section 7).
- Base-game layout (measured on `BuildingPortraits3_*_Exp2Patch.dds`): a circle 171 px wide at (43,42) in a 256 px cell
  (128: 22..107, 64: 11..54, 45: 8..38), transparent around it, no frame. The city screen draws its bronze ring
  (`IconFrame64.dds`) around that circle; the production list shows the bare circle.
- `python art_sources/tools/round_building_icon.py <name>`: trims 5% of the source's dark border, scales it into that
  circle, masks it (anti-aliased) and writes 32/45/64/80/128/214/256 to `LEKMOD/Art/Lekmod (v 1)/Art/Buildings/`.
  Used for Sanctuary, Stupa and the Uranium Mapping Project (2026-10-11).
- Atlases: one 1x1 atlas per icon.

## Main menu backgrounds
Each PNG is scaled to cover 1920x1200 (centre crop), then BC1 (no alpha) with one mip: about 1.2 MB each.
Files `LEKMOD/Art/Lekmod (v 1)/UI/lekmod_menu_background_01..11.dds` follow the alphabetical order of the PNGs here;
`lekmod_menu_background.dds` is the original Great Wall painting. `FrontEnd.lua` picks one at random
(`LEKMOD_MENU_BACKGROUND_COUNT`).
