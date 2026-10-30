#!/usr/bin/env python3
"""
Homefront: The Revolution (PC / CryEngine 3.8) - Autonomous Guerrilla & Freedom Fighters Squad Overhaul Patcher
Author: jackedhawk-117
Repository: https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered

This tool applies or reverts binary patches directly to Homefront2_Release.exe (x86-64).
Zero-Data Modification Principle: Redirects native .text instruction displacements
and immediate operands to existing constants, maintaining binary section headers
and engine stability.

Feature Suite (30 Patches - Rock-Solid / Stable):
- Autonomous Guerrilla Presence (Patches #1-#9):
    Quadrupled ambient urban resistance population (caps raised 24 -> 96, 60 -> 150),
    accelerated reinforcement repopulation, extended patrol grid radius.
- 12-Man Squad Recruitment & Formations (Patches #10-#13):
    Full 12-follower recruitment ceiling, expanded formation radius, dynamic spacing,
    and adaptive follow corridors.
- Urban Collision Clearance & Leash Tether (Patches #14-#16):
    Zero companion doorway bottlenecks, 250m follower tether leash.
- Instant Combat Reactions & True Marksman Accuracy (Patches #17-#18, #20A-#20C, #21):
    Instant threat detection (0.0s latency), aggressive coordinated target acquisition,
    zero companion weapon spread neutralization.
- Freedom Fighters Squad Durability (Patch #19):
    75% companion damage resistance, matching classic Freedom Fighters durability.
- Permanent Infrastructure Hacking (Patches #29A-#29B):
    GTK Hack Tool converts enemy drones, vehicles, and turrets into permanent friendly allies.
- Freedom Fighters Tactical Squad Orders (Patches #30, #31A-#31D):
    Direct hardware keyboard query engine via USER32.dll!GetAsyncKeyState:
      F2 -> Regroup / Follow Leader
      F3 -> Attack / Push (25m look vector advance)
      F4 -> Defend / Hold Position
"""

import os
import sys
import json
import shutil
import hashlib
import argparse

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
PATCH_FILE = os.path.join(SCRIPT_DIR, "patches.json")

VANILLA_MD5 = "0326ea202fcd7ceb3760d14bc8d07f63"
VANILLA_SHA256 = "c81fc8d6d61195a8f99d303926bcf32f6ca6638d8fa2deac9fc2d10c9ae4133c"

PATCHED_MD5 = "d78abc8af063d015779600dd7005b26c"
PATCHED_SHA256 = "859a5ba7a05ac9e6fe89da0386f78d1ce9b708bcc6323deb9bdf3e122eeff9fe"


def compute_hashes(file_path):
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            md5.update(chunk)
            sha256.update(chunk)
    return md5.hexdigest(), sha256.hexdigest()


def load_patches():
    if not os.path.isfile(PATCH_FILE):
        print(f"[-] Error: patches.json not found at {PATCH_FILE}")
        sys.exit(1)
    with open(PATCH_FILE, "r") as f:
        data = json.load(f)
    return data.get("patches", [])


def verify_target(target_path, patches):
    if not os.path.isfile(target_path):
        print(f"[-] Error: Target executable not found: {target_path}")
        return False

    md5, sha256 = compute_hashes(target_path)
    print(f"[*] Target Binary: {target_path}")
    print(f"[*] Current MD5:    {md5}")
    print(f"[*] Current SHA256: {sha256}")

    applied_count = 0
    vanilla_count = 0
    custom_count = 0

    patch_states = {}

    with open(target_path, "rb") as f:
        for p in patches:
            p_id = str(p["id"])
            offset = p["offset"]
            orig = bytes.fromhex(p["original_hex"])
            pat = bytes.fromhex(p["patched_hex"])
            size = p["size"]

            f.seek(offset)
            current = f.read(size)

            if current == pat:
                status = "PATCHED"
                applied_count += 1
            elif current == orig:
                status = "VANILLA"
                vanilla_count += 1
            else:
                status = "CUSTOM"
                custom_count += 1

            patch_states[p_id] = status

    if md5 == VANILLA_MD5:
        print(f"[+] Binary Status: Clean Vanilla (Unmodified - 0/{len(patches)} Patches Active)")
    elif md5 == PATCHED_MD5:
        print(f"[+] Binary Status: Freedom Fighters & Guerrilla Overhaul Active (Stable / Complete - {applied_count}/{len(patches)} Patches Active)")
    else:
        print(f"[!] Binary Status: Custom / Partially Patched ({applied_count}/{len(patches)} Active)")

    # Group patches by category for visual display
    categories = {}
    for p in patches:
        cat = p.get("category", "General")
        categories.setdefault(cat, []).append(p)

    for cat_name, cat_patches in categories.items():
        print(f"\n--- {cat_name} ({len(cat_patches)} Patches) ---")
        for p in cat_patches:
            p_id = str(p["id"])
            st = patch_states.get(p_id, "UNKNOWN")
            print(f"  Patch #{p_id:<4} [{st:<7}] {p['name']:<38} (Offset: {hex(p['offset'])})")

    print(f"\n[*] Summary: {applied_count}/{len(patches)} Patched | {vanilla_count}/{len(patches)} Vanilla" + (f" | {custom_count} Custom" if custom_count else ""))
    return True


def apply_patches(target_path, patches, selected_ids=None, backup=True):
    if not os.path.isfile(target_path):
        print(f"[-] Error: Target executable not found: {target_path}")
        return False

    if backup:
        backup_path = target_path + ".vanilla"
        if not os.path.isfile(backup_path):
            print(f"[*] Creating backup at {backup_path}...")
            shutil.copy2(target_path, backup_path)
            print("[+] Backup created successfully.")
        else:
            print(f"[*] Existing backup found at {backup_path}.")

    desc = f"Selected Patches ({len(selected_ids)})" if selected_ids else f"Freedom Fighters Overhaul (All {len(patches)} Patches)"
    print(f"[*] Applying: {desc}")

    applied = 0
    with open(target_path, "r+b") as f:
        for p in patches:
            p_id = str(p["id"])
            if selected_ids and p_id not in selected_ids:
                continue

            offset = p["offset"]
            orig = bytes.fromhex(p["original_hex"])
            pat = bytes.fromhex(p["patched_hex"])
            size = p["size"]

            f.seek(offset)
            current = f.read(size)

            if current == pat:
                print(f"  [-] Patch #{p_id:<4} already applied: {p['name']}")
                continue
            elif current != orig:
                print(f"  [!] Warning: Patch #{p_id} ({p['name']}) byte mismatch at {hex(offset)} (Expected: {orig.hex()[:8]}..., Found: {current.hex()[:8]}...) - Skipping")
                continue

            f.seek(offset)
            f.write(pat)
            applied += 1
            print(f"  [+] Applied Patch #{p_id:<4} {p['name']:<38} -> {p['desc']}")

    md5, sha256 = compute_hashes(target_path)
    print(f"\n[+] Successfully applied {applied} patches.")
    print(f"[*] New Binary MD5:    {md5}")
    print(f"[*] New Binary SHA256: {sha256}")

    if md5 == PATCHED_MD5:
        print("[+] Verified: Executable matches verified Freedom Fighters & Guerrilla Overhaul build!")

    return True


def revert_patches(target_path, patches, selected_ids=None, description="Clean Vanilla"):
    if not os.path.isfile(target_path):
        print(f"[-] Error: Target executable not found: {target_path}")
        return False

    print(f"[*] Reverting Target to: {description}")

    reverted = 0
    with open(target_path, "r+b") as f:
        for p in patches:
            p_id = str(p["id"])
            if selected_ids and p_id not in selected_ids:
                continue

            offset = p["offset"]
            orig = bytes.fromhex(p["original_hex"])
            pat = bytes.fromhex(p["patched_hex"])
            size = p["size"]

            f.seek(offset)
            current = f.read(size)

            if current == orig:
                print(f"  [-] Patch #{p_id:<4} already vanilla: {p['name']}")
                continue
            elif current != pat:
                print(f"  [!] Warning: Patch #{p_id} ({p['name']}) byte mismatch at {hex(offset)} (Expected: {pat.hex()[:8]}..., Found: {current.hex()[:8]}...) - Skipping")
                continue

            f.seek(offset)
            f.write(orig)
            reverted += 1
            print(f"  [+] Reverted Patch #{p_id:<4} {p['name']:<38} to Vanilla")

    md5, sha256 = compute_hashes(target_path)
    print(f"\n[+] Successfully reverted {reverted} patches.")
    print(f"[*] New Binary MD5:    {md5}")
    print(f"[*] New Binary SHA256: {sha256}")

    if md5 == VANILLA_MD5:
        print("[+] Verified: Executable restored to 100% Clean Vanilla state!")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Homefront: The Revolution (CryEngine 3.8) Binary Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Installation Modes & Examples:

  1. Apply Complete Freedom Fighters & Guerrilla Overhaul (All 30 Patches):
     python3 patcher.py --apply Homefront2_Release.exe
     (12-man squad, 75% durability, 4x urban war pop, permanent GTK hack, tactical squad orders F2-F4)

  2. Verify Executable Status:
     python3 patcher.py --verify Homefront2_Release.exe

  3. Full Revert to 100% Clean Vanilla:
     python3 patcher.py --revert Homefront2_Release.exe

  4. Selective Patch Application:
     python3 patcher.py --apply Homefront2_Release.exe --patches 10,19,30,31A,31B,31C,31D
"""
    )
    parser.add_argument("target", help="Path to Homefront2_Release.exe")
    parser.add_argument("--verify", action="store_true", help="Verify status of all patches on target binary")
    parser.add_argument("--apply", action="store_true", help="Apply complete Freedom Fighters & Guerrilla Overhaul (All 30 Patches)")
    parser.add_argument("--revert", action="store_true", help="Revert patches to clean vanilla")
    parser.add_argument("--patches", type=str, help="Comma-separated patch IDs to apply/revert (e.g. 10,19,30,31A)")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a .vanilla backup before patching")

    args = parser.parse_args()

    patches = load_patches()

    if args.revert:
        selected_ids = [s.strip() for s in args.patches.split(",")] if args.patches else None
        desc = f"Selected Patches ({args.patches})" if selected_ids else "Clean Vanilla"
        revert_patches(args.target, patches, selected_ids=selected_ids, description=desc)
    elif args.apply:
        selected_ids = [s.strip() for s in args.patches.split(",")] if args.patches else None
        apply_patches(
            args.target,
            patches,
            selected_ids=selected_ids,
            backup=not args.no_backup
        )
    else:
        # Default action: verify
        verify_target(args.target, patches)


if __name__ == "__main__":
    main()
