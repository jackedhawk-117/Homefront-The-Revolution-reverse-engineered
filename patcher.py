#!/usr/bin/env python3
"""
Homefront: The Revolution (PC / CryEngine 3.8) - Autonomous Guerrilla & 12-Man Squad Patcher
Author: jackedhawk-117
Repository: https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered

This tool applies or reverts binary patches directly to Homefront2_Release.exe (x86-64).
Zero-Data Modification Principle: Redirects native .text instruction displacements
and immediate operands to existing constants, maintaining binary section headers
and engine stability.

Modular Patch Architecture:
- Core Overhaul (Patches #1-#21, 23 patches) [STABLE / DEFAULT]:
    Autonomous Guerrilla presence, 12-man squad recruitment cap, 75% squad damage
    resistance (Freedom Fighters durability), urban collision clearance, instant combat
    reactions, true marksman accuracy, and expanded perimeter formations.
- Third-Person Camera Suite (Patches #22A-#28, 9 patches) [OPTIONAL / EXPERIMENTAL]:
    Over-The-Shoulder (OTS) perspective, F1 hotkey toggle, dynamic ADS 1P zoom,
    and cover fire override bypass.
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

CORE_PATCHED_MD5 = "96f593ff3c734855066daced924e6521"
CORE_PATCHED_SHA256 = "f9766b5340eb5edf84e3441c6b51be86e2316156db1137d07176a294867d074e"

FULL_PATCHED_MD5 = "f9bcf502666adfe038d9143e2ab4d861"
FULL_PATCHED_SHA256 = "e3c7d3b439b56308effe3c9e8f428e7044d2cceb303c98fceab117299b9be2f2"

CORE_PATCH_IDS = {
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19",
    "20A", "20B", "20C", "21"
}

THIRD_PERSON_PATCH_IDS = {
    "22A", "22B", "23", "24A", "24B", "25A", "25B", "26", "28"
}


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

    core_patches = [p for p in patches if str(p["id"]) in CORE_PATCH_IDS]
    tps_patches = [p for p in patches if str(p["id"]) in THIRD_PERSON_PATCH_IDS]

    core_applied = 0
    tps_applied = 0
    total_applied = 0
    total_vanilla = 0
    total_custom = 0

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
                total_applied += 1
                if p_id in CORE_PATCH_IDS:
                    core_applied += 1
                elif p_id in THIRD_PERSON_PATCH_IDS:
                    tps_applied += 1
            elif current == orig:
                status = "VANILLA"
                total_vanilla += 1
            else:
                status = "CUSTOM"
                total_custom += 1

            patch_states[p_id] = status

    if md5 == VANILLA_MD5:
        print("[+] Binary Status: Clean Vanilla (Unmodified - 0/32 Patches Active)")
    elif md5 == CORE_PATCHED_MD5:
        print(f"[+] Binary Status: Core Squad Overhaul Active (Stable / Recommended - {core_applied}/{len(core_patches)} Core Patches, 3P Camera Inactive)")
    elif md5 == FULL_PATCHED_MD5:
        print(f"[+] Binary Status: Full Overhaul Active (Core + Third-Person Camera - All {total_applied}/{len(patches)} Patches Active)")
    else:
        print(f"[!] Binary Status: Custom / Partially Patched ({core_applied}/{len(core_patches)} Core, {tps_applied}/{len(tps_patches)} Third-Person)")

    print("\n--- [1] Core Squad & Guerrilla Overhaul (Patches #1-#21) [STABLE / DEFAULT] ---")
    for p in core_patches:
        p_id = str(p["id"])
        st = patch_states.get(p_id, "UNKNOWN")
        print(f"  Patch #{p_id:<4} [{st:<7}] {p['name']:<38} (Offset: {hex(p['offset'])})")

    print("\n--- [2] Third-Person Camera Suite (Patches #22A-#28) [OPTIONAL / EXPERIMENTAL] ---")
    for p in tps_patches:
        p_id = str(p["id"])
        st = patch_states.get(p_id, "UNKNOWN")
        print(f"  Patch #{p_id:<4} [{st:<7}] {p['name']:<38} (Offset: {hex(p['offset'])})")

    print(f"\n[*] Summary: {total_applied}/{len(patches)} Patched ({core_applied}/{len(core_patches)} Core, {tps_applied}/{len(tps_patches)} Third-Person) | {total_vanilla}/{len(patches)} Vanilla" + (f" | {total_custom} Custom" if total_custom else ""))
    return True


def apply_patches(target_path, patches, selected_ids=None, backup=True, profile_name="Core Squad Overhaul"):
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

    print(f"[*] Applying Profile: {profile_name}")

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

    if md5 == CORE_PATCHED_MD5:
        print("[+] Verified: Executable matches verified Core Squad Overhaul build (Stable)!")
    elif md5 == FULL_PATCHED_MD5:
        print("[+] Verified: Executable matches verified Full Overhaul build (Core + Third-Person Camera)!")

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
    elif md5 == CORE_PATCHED_MD5:
        print("[+] Verified: Executable cleanly restored to Core Squad Overhaul (Third-Person Camera removed)!")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Homefront: The Revolution (CryEngine 3.8) Binary Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Installation Modes & Examples:

  1. Recommended Stable Installation (Core Autonomous Guerrilla & 12-Man Squad Overhaul):
     python3 patcher.py --apply Homefront2_Release.exe
     (Applies Patches #1-#21: 12-man squad, 75% durability, 4x urban war pop, true aim)

  2. Full Overhaul including Experimental Third-Person OTS Camera Suite:
     python3 patcher.py --apply --with-third-person Homefront2_Release.exe
     (Applies all 32 patches: Core Squad Overhaul + Third-Person Camera features)

  3. Remove Third-Person Camera Only (keep Core Squad Overhaul active):
     python3 patcher.py --revert-third-person Homefront2_Release.exe
     (Reverts Patches #22A-#28 back to vanilla, restoring the stable 12-man squad build)

  4. Verify Executable Status:
     python3 patcher.py --verify Homefront2_Release.exe

  5. Full Revert to 100% Clean Vanilla:
     python3 patcher.py --revert Homefront2_Release.exe

  6. Selective Patch Application:
     python3 patcher.py --apply Homefront2_Release.exe --patches 10,19,20A,20B,20C,21
"""
    )
    parser.add_argument("target", help="Path to Homefront2_Release.exe")
    parser.add_argument("--verify", action="store_true", help="Verify status of all patches on target binary")
    parser.add_argument("--apply", action="store_true", help="Apply patches (Core Overhaul by default; use --with-third-person for 3P camera)")
    parser.add_argument("--with-third-person", "--all", action="store_true", dest="with_third_person",
                        help="Include optional / experimental Third-Person OTS Camera Suite (Patches #22A-#28)")
    parser.add_argument("--third-person-only", action="store_true",
                        help="Apply only the optional Third-Person Camera Suite (Patches #22A-#28)")
    parser.add_argument("--revert", action="store_true", help="Revert patches to clean vanilla")
    parser.add_argument("--revert-third-person", "--without-third-person", action="store_true", dest="revert_third_person",
                        help="Revert only the Third-Person Camera Suite (Patches #22A-#28), keeping Core Overhaul intact")
    parser.add_argument("--patches", type=str, help="Comma-separated patch IDs to apply/revert (e.g. 10,19,21)")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a .vanilla backup before patching")

    args = parser.parse_args()

    patches = load_patches()

    # Determine patch selection and profile
    if args.revert_third_person:
        # Revert only third-person camera patches
        revert_patches(
            args.target,
            patches,
            selected_ids=THIRD_PERSON_PATCH_IDS,
            description="Core Squad Overhaul (Disabling Third-Person Camera)"
        )
    elif args.revert:
        selected_ids = [s.strip() for s in args.patches.split(",")] if args.patches else None
        desc = f"Selected Patches ({args.patches})" if selected_ids else "Clean Vanilla"
        revert_patches(args.target, patches, selected_ids=selected_ids, description=desc)
    elif args.apply:
        if args.patches:
            selected_ids = [s.strip() for s in args.patches.split(",")]
            profile = f"Custom Patches ({args.patches})"
        elif args.third_person_only:
            selected_ids = THIRD_PERSON_PATCH_IDS
            profile = "Third-Person Camera Suite Only (Patches #22A-#28)"
        elif args.with_third_person:
            selected_ids = None  # None means all patches in patches.json
            profile = "Full Overhaul (Core Squad Overhaul + Third-Person Camera Suite)"
        else:
            # Default behavior: Core Overhaul only
            selected_ids = CORE_PATCH_IDS
            profile = "Core Squad & Guerrilla Overhaul (Stable / Default - Patches #1-#21)"
            print("[*] Note: Applying stable Core Overhaul. To include experimental 3P camera, use '--with-third-person'.")

        apply_patches(
            args.target,
            patches,
            selected_ids=selected_ids,
            backup=not args.no_backup,
            profile_name=profile
        )
    else:
        # Default action: verify
        verify_target(args.target, patches)


if __name__ == "__main__":
    main()
