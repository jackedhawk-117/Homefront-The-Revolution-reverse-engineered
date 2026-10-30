# Installation & Usage Guide

This guide provides step-by-step instructions on how to install, verify, and use the **Autonomous Guerrilla & Freedom Fighters Squad Overhaul** for *Homefront: The Revolution*.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Default Steam Game Paths](#default-steam-game-paths)
3. [Method 1: Automated Patcher (Recommended)](#method-1-automated-patcher-recommended)
   - [Windows (CMD / PowerShell)](#windows-cmd--powershell)
   - [Linux / Proton](#linux--proton)
   - [Steam Deck](#steam-deck)
4. [Freedom Fighters Tactical Squad Hotkeys](#freedom-fighters-tactical-squad-hotkeys)
5. [In-Game Verification Checklist](#in-game-verification-checklist)
6. [How to Revert to Clean Vanilla](#how-to-revert-to-clean-vanilla)
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

4. **Apply the Freedom Fighters & Guerrilla Overhaul:**
   ```cmd
   python patcher.py --apply "C:\Program Files (x86)\Steam\steamapps\common\Homefront_The_Revolution\Bin64\Homefront2_Release.exe"
   ```
   *The patcher will automatically create a backup at `Homefront2_Release.exe.vanilla` and apply all 31 verified patches.*

5. Launch the game normally from your Steam Library!

---

### Linux / Proton

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered.git
   cd Homefront-The-Revolution-reverse-engineered
   ```

2. **Apply the Freedom Fighters & Guerrilla Overhaul:**
   ```bash
   python3 patcher.py --apply ~/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe
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

## Freedom Fighters Tactical Squad Hotkeys

While in-game, you can direct your recruited Resistance fighters at any time:

| Hotkey | Tactical Order | Action & Squad Behavior |
| :---: | :--- | :--- |
| **`F2`** | **Follow / Regroup** | Calls all squad members to your position. Followers break off holding or pushing and dynamically follow Ethan Brady in tactical formation. |
| **`F3`** | **Attack / Push** | Orders the squad to advance **25 meters forward** in the direction you are looking. Followers push into enemy positions, engaging targets aggressively. |
| **`F4`** | **Defend / Hold Ground** | Freezes the squad's formation anchor at your current location. Followers take waist-high cover around the anchor, establish a defensive perimeter, and hold the ground. |

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
3. **Tactical Commands Check:**
   - Aim towards an open street or enemy barrier and press **`F3`**: squad advances 25m forward into the zone.
   - Press **`F4`**: squad establishes a defensive line and holds ground.
   - Press **`F2`**: squad regroups back to you immediately.
4. **Combat Reaction Speed:**
   - Encounter a KPA patrol or airship alert.
   - Notice that both friendly fighters and KPA open fire instantly (~150ms) without standing around staring at each other.
5. **Squad Survivability & Aim:**
   - Observe followers during a firefight: they survive 12–15 bullets (4x durability) and reliably hit targets with center-mass marksmanship.
6. **Permanent Equipment Hack Check:**
   - Throw a GTK Hack Tool near an enemy drone, automated turret, or vehicle. Confirm that it converts to friendly, displays a full circular HUD timer, and fights alongside Ethan Brady indefinitely rather than reverting after a short timeout.

---

## How to Revert to Clean Vanilla

Restores the executable 100% back to unmodded vanilla original (`0326ea202fcd7ceb3760d14bc8d07f63`):
```bash
python3 patcher.py --revert /path/to/Homefront2_Release.exe
```

### Alternative Revert Methods
- **Restoring Backup:** Delete `Homefront2_Release.exe` and rename `Homefront2_Release.exe.vanilla` back to `Homefront2_Release.exe`.
- **Steam Verification:** In Steam: Right-click **Homefront: The Revolution** $\to$ **Properties** $\to$ **Installed Files** $\to$ **Verify integrity of game files**.

---

## Frequently Asked Questions & Troubleshooting

#### Q: How do I verify my installation status?
**A:** Run `python3 patcher.py --verify /path/to/Homefront2_Release.exe`. The patcher inspects all 31 routines and confirms the binary's MD5 checksum.

#### Q: Will this break my existing save files?
**A:** **No.** Save serialization in CryEngine stores follower assignments dynamically per NPC entity (`CGameAI::Serialize`). Your existing safehouse and campaign progress are 100% compatible.

#### Q: Does Steam detect this as a cheat?
**A:** **No.** *Homefront: The Revolution* single-player campaign has no anti-cheat software. This mod is strictly for single-player offline campaign play.

#### Q: What happens if Steam updates the game?
**A:** If Steam downloads an update or verifies game files, it will replace `Homefront2_Release.exe` with vanilla. You simply re-run `python3 patcher.py --apply` to re-apply the mod.
