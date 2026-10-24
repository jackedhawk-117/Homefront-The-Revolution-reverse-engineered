# Installation & Usage Guide

This guide provides step-by-step instructions on how to install, verify, and uninstall the **Autonomous Guerrilla & 12-Man Squad Overhaul** for *Homefront: The Revolution*.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Default Steam Game Paths](#default-steam-game-paths)
3. [Method 1: Automated Patcher (Recommended)](#method-1-automated-patcher-recommended)
   - [Windows (CMD / PowerShell)](#windows-cmd--powershell)
   - [Linux / Proton](#linux--proton)
   - [Steam Deck](#steam-deck)
4. [Choosing Your Installation Profile](#choosing-your-installation-profile)
   - [Profile 1: Core Squad & Guerrilla Overhaul (Stable / Default)](#profile-1-core-squad--guerrilla-overhaul-stable--default)
   - [Profile 2: Full Overhaul with Third-Person Camera (Optional / Experimental)](#profile-2-full-overhaul-with-third-person-camera-optional--experimental)
5. [In-Game Verification Checklist](#in-game-verification-checklist)
6. [How to Revert or Switch Modes](#how-to-revert-or-switch-modes)
   - [Revert Third-Person Camera Only (Keep Squad Mod)](#revert-third-person-camera-only-keep-squad-mod)
   - [Full Revert to Clean Vanilla](#full-revert-to-clean-vanilla)
7. [Frequently Asked Questions & Troubleshooting](#frequently-asked-questions--troubleshooting)

---

## Prerequisites
- A legally owned copy of **Homefront: The Revolution** on PC (Steam).
- **Python 3.7+** installed:
  - **Windows:** Download from [python.org](https://www.python.org/) (ensure **"Add Python to PATH"** is checked during installation).
  - **Linux / Steam Deck:** Pre-installed on almost all distributions.

---

## Default Steam Game Paths

Locate your game's `Bin64` directory:

| Operating System | Default Install Location |
| :--- | :--- |
| **Windows** | `C:\Program Files (x86)\Steam\steamapps\common\Homefront_The_Revolution\Bin64\Homefront2_Release.exe` |
| **Linux (Native Steam)** | `~/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe` |
| **Linux (Flatpak Steam)** | `~/.var/app/com.valvesoftware.Steam/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe` |
| **Steam Deck** | `/home/deck/.local/share/Steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe` |

> [!TIP]
> **To find your exact path in Steam:**
> Right-click **Homefront: The Revolution** in your Steam Library $\to$ **Manage** $\to$ **Browse local files** $\to$ open the **`Bin64`** folder.

---

## Choosing Your Installation Profile

The patcher supports modular installation:

### Profile 1: Core Squad & Guerrilla Overhaul (Stable / Default)
*Command:* `python3 patcher.py --apply <target>`
- **Recommended for all players.**
- Applies Patches #1–#21 (23 patches): 12-man companion recruitment cap, 75% squad damage resistance (4x HP), instant combat reactions (<200ms), true marksman aim, doorway collision avoidance, and 4x active urban war presence.
- 100% stable, fully tested, zero camera quirks. Keeps native first-person perspective intact.

### Profile 2: Full Overhaul with Third-Person Camera (Optional / Experimental)
*Command:* `python3 patcher.py --apply --with-third-person <target>`
- Applies all 32 patches (Core Overhaul + Third-Person OTS Camera Suite).
- Enables over-the-shoulder 3rd-person traversal, F1 hotkey toggle, and dynamic 1P iron sights aiming.
- **Note:** Because the game was originally designed exclusively for first-person gameplay, 3P camera features can experience engine-level friction (such as interior wall collision clipping, vehicle cameras, and specific weapon animation states).

---

## Method 1: Automated Patcher (Recommended)

The patcher modifies only the specific instruction bytes in your existing executable, creates an automatic backup (`Homefront2_Release.exe.vanilla`), and verifies file integrity in **under 0.1 seconds**.

### Windows (CMD / PowerShell)

1. **Download the repository:**
   Click the green **Code** button $\to$ **Download ZIP**, then extract it to a folder (e.g. `Downloads\Homefront-Mod`).
   
   *Alternatively, via Git:*
   ```cmd
   git clone https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered.git
   cd Homefront-The-Revolution-reverse-engineered
   ```

2. **Open Command Prompt or PowerShell** inside that folder.

3. **Verify your game binary:**
   ```cmd
   python patcher.py --verify "C:\Program Files (x86)\Steam\steamapps\common\Homefront_The_Revolution\Bin64\Homefront2_Release.exe"
   ```
   *You should see:* `[+] Binary Status: Clean Vanilla (Unmodified)`.

4. **Apply the stable Core Squad Overhaul (Recommended):**
   ```cmd
   python patcher.py --apply "C:\Program Files (x86)\Steam\steamapps\common\Homefront_The_Revolution\Bin64\Homefront2_Release.exe"
   ```
   *The patcher will automatically create a backup at `Homefront2_Release.exe.vanilla` and apply the 23 core routines.*

   *(Optional) If you wish to test the experimental Third-Person Camera suite:*
   ```cmd
   python patcher.py --apply --with-third-person "C:\Program Files (x86)\Steam\steamapps\common\Homefront_The_Revolution\Bin64\Homefront2_Release.exe"
   ```

5. Launch the game normally from your Steam Library!

---

### Linux / Proton

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered.git
   cd Homefront-The-Revolution-reverse-engineered
   ```

2. **Apply the stable Core Squad Overhaul:**
   ```bash
   python3 patcher.py --apply ~/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe
   ```

   *(Optional) To install with Third-Person Camera:*
   ```bash
   python3 patcher.py --apply --with-third-person ~/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe
   ```

3. Launch the game via Steam with your preferred Proton version (e.g. Proton GE or Proton Experimental).

---

### Steam Deck

1. Switch your Steam Deck to **Desktop Mode** (Steam Button $\to$ **Power** $\to$ **Switch to Desktop**).
2. Open the **Konsole** terminal application.
3. Clone and apply:
   ```bash
   git clone https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered.git
   cd Homefront-The-Revolution-reverse-engineered
   python3 patcher.py --apply /home/deck/.local/share/Steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe
   ```
4. Return to **Gaming Mode** and play!

---

## In-Game Verification Checklist

Once inside the campaign:

1. **Recruitment Check:**
   - Walk up to friendly fighters in a safehouse or street.
   - Press **`[E] Recruit`** on 12 consecutive fighters.
   - Confirm all 12 followers receive 3D world overhead chevron icons and compass/minimap markers.
2. **Doorway & Outpost Exit Check:**
   - Walk through a standard interior door or safehouse exit.
   - Confirm all 12 followers stream out smoothly in a queue rather than freezing or wedging in the entrance.
3. **Combat Reaction Speed:**
   - Encounter a KPA patrol or airship alert.
   - Notice that both friendly fighters and KPA open fire instantly (~150ms) without standing around staring at each other.
4. **Squad Survivability & Aim:**
   - Observe followers during a firefight: they survive 12–15 bullets (4x durability) and reliably hit targets with center-mass marksmanship.
5. **(Optional) Third-Person Controls (if `--with-third-person` was used):**
   - Press **`F1`** to toggle between 1st-person and 3rd-person OTS view.
   - Click **Right Mouse Button** (vanilla toggle ADS) to dynamically snap into 1st-person iron sights / reflex / sniper scope aiming.
   - Map (`M`), Weapon Customization (`X`), and Phone (`V`) automatically revert to first-person view.

---

## How to Revert or Switch Modes

You can manage or revert modifications at any time:

### Revert Third-Person Camera Only (Keep Squad Mod)
If you tried the experimental 3P camera and want to remove it while keeping your 12-man squad overhaul active:
```bash
python3 patcher.py --revert-third-person /path/to/Homefront2_Release.exe
```
*Restores the binary cleanly to the verified Core Squad Overhaul state (`96f593ff3c734855066daced924e6521`).*

### Full Revert to Clean Vanilla
Restores the executable 100% back to unmodded vanilla original (`0326ea202fcd7ceb3760d14bc8d07f63`):
```bash
python3 patcher.py --revert /path/to/Homefront2_Release.exe
```

### Alternative Revert Methods
- **Restoring Backup:** Delete `Homefront2_Release.exe` and rename `Homefront2_Release.exe.vanilla` back to `Homefront2_Release.exe`.
- **Steam Verification:** In Steam: Right-click **Homefront: The Revolution** $\to$ **Properties** $\to$ **Installed Files** $\to$ **Verify integrity of game files**.

---

## Frequently Asked Questions & Troubleshooting

#### Q: Which mode should I install?
**A:** We strongly recommend the **Core Squad Overhaul** (`python3 patcher.py --apply ...`). It gives you the full *Freedom Fighters* squad experience (12 followers, 4x health, instant reaction, true marksman accuracy, quadrupled war spawns) with 100% stability. The Third-Person Camera is an optional experimental addition for players who specifically want an OTS perspective.

#### Q: How do I know which mode is currently active on my executable?
**A:** Run `python3 patcher.py --verify /path/to/Homefront2_Release.exe`. The patcher will inspect all 32 routines and report whether the binary is Clean Vanilla, Core Squad Overhaul Active, or Full Overhaul Active.

#### Q: Will this break my existing save files?
**A:** **No.** Save serialization in CryEngine stores follower assignments dynamically per NPC entity (`CGameAI::Serialize`). Your existing safehouse and campaign progress are 100% compatible.

#### Q: Does Steam detect this as a cheat?
**A:** **No.** *Homefront: The Revolution* single-player campaign has no anti-cheat software. This mod is strictly for single-player offline campaign play.

#### Q: What happens if Steam updates the game?
**A:** If Steam downloads an update or verifies game files, it will replace `Homefront2_Release.exe` with vanilla. You simply re-run `python3 patcher.py --apply` to re-apply the mod.
