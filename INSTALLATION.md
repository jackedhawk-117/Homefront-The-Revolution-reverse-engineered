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
4. [Method 2: Manual Replacement (If Sent Pre-Patched EXE)](#method-2-manual-replacement-if-sent-pre-patched-exe)
5. [In-Game Verification Checklist](#in-game-verification-checklist)
6. [How to Revert to Vanilla](#how-to-revert-to-vanilla)
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

4. **Apply all patches:**
   ```cmd
   python patcher.py --apply "C:\Program Files (x86)\Steam\steamapps\common\Homefront_The_Revolution\Bin64\Homefront2_Release.exe"
   ```
   *The patcher will automatically create a backup at `Homefront2_Release.exe.vanilla` and patch all 21 routines.*

5. Launch the game normally from your Steam Library!

---

### Linux / Proton

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered.git
   cd Homefront-The-Revolution-reverse-engineered
   ```

2. **Apply the patch directly:**
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

## Method 2: Manual Replacement (If Sent Pre-Patched EXE)

If a friend directly shared a pre-patched `Homefront2_Release.exe` with you:

1. Close the game and make sure it is not running in Steam.
2. Navigate to your game's directory:
   `Steam/steamapps/common/Homefront_The_Revolution/Bin64/`
3. **Backup your original executable:**
   Rename `Homefront2_Release.exe` $\to$ `Homefront2_Release.exe.bak`.
4. Copy the patched `Homefront2_Release.exe` into the `Bin64/` folder.
5. Launch the game via Steam.

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
5. **Third-Person Perspective:**
   - Confirm player character Ethan Brady is fully rendered in 3D (clothes, gear, backpack, and weapon).
   - Camera tracks behind Ethan Brady at a close 1.85m action distance with native geometry collision (no wall clipping).

---

## How to Revert to Vanilla

You can revert to clean unmodded gameplay at any time using any of these methods:

### Option A: Using the Patcher (Instant)
```bash
python3 patcher.py --revert /path/to/Homefront2_Release.exe
```

### Option B: Restoring the Automatic Backup
Delete `Homefront2_Release.exe` and rename `Homefront2_Release.exe.vanilla` back to `Homefront2_Release.exe`.

### Option C: Steam File Verification
In Steam: Right-click **Homefront: The Revolution** $\to$ **Properties** $\to$ **Installed Files** $\to$ **Verify integrity of game files**.

---

## Frequently Asked Questions & Troubleshooting

#### Q: Will this break my existing save files?
**A:** **No.** Save serialization in CryEngine stores follower assignments dynamically per NPC entity (`CGameAI::Serialize`). Your existing safehouse and campaign progress are 100% compatible.

#### Q: Does Steam detect this as a cheat?
**A:** **No.** *Homefront: The Revolution* single-player campaign has no anti-cheat software (Easy Anti-Cheat or BattlEye are not used in campaign mode). This mod is strictly for single-player offline campaign play.

#### Q: What happens if Steam updates the game?
**A:** If Steam downloads an update or verifies game files, it will simply replace `Homefront2_Release.exe` with vanilla. You just re-run `python3 patcher.py --apply` to re-enable all 25 patches.

#### Q: Why does the patcher report a byte mismatch?
**A:** Make sure your executable is the latest 64-bit Steam Release version (`Homefront2_Release.exe`, 41,827,328 bytes, MD5: `0326ea202fcd7ceb3760d14bc8d07f63`). If your game is already patched, `python3 patcher.py --verify` will show which patches are active.
