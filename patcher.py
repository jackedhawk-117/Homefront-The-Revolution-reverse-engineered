#!/usr/bin/env python3
"""
Homefront: The Revolution (PC / CryEngine 3.8) - Autonomous Guerrilla & 12-Man Squad Patcher
Author: jackedhawk-117
Repository: https://github.com/jackedhawk-117/Homefront-The-Revolution-reverse-engineered

This tool applies or reverts binary patches directly to Homefront2_Release.exe (x86-64).
Zero-Data Modification Principle: Redirects native .text instruction displacements
and immediate operands to existing constants, maintaining binary section headers
and engine stability.
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
FULL_PATCHED_MD5 = "96f593ff3c734855066daced924e6521"
FULL_PATCHED_SHA256 = "f9766b5340eb5edf84e3441c6b51be86e2316156db1137d07176a294867d074e"


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

    if md5 == VANILLA_MD5:
        print("[+] Binary Status: Clean Vanilla (Unmodified)")
    elif md5 == FULL_PATCHED_MD5:
        print("[+] Binary Status: Fully Patched (All 21 Patches Active)")
    else:
        print("[!] Binary Status: Custom / Partially Patched")

    print("\n[+] Inspecting Individual Patch States:")
    applied_count = 0
    vanilla_count = 0
    other_count = 0

    with open(target_path, "rb") as f:
        for p in patches:
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
                status = "UNKNOWN"
                other_count += 1

            print(f"  Patch #{p['id']:<4} [{status:<7}] {p['name']:<38} (Offset: {hex(offset)})")

    print(f"\n[*] Summary: {applied_count}/{len(patches)} Patched, {vanilla_count}/{len(patches)} Vanilla, {other_count} Custom")
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
    return True


def revert_patches(target_path, patches, selected_ids=None):
    if not os.path.isfile(target_path):
        print(f"[-] Error: Target executable not found: {target_path}")
        return False

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
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Homefront: The Revolution (CryEngine 3.8) Binary Patcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 patcher.py --verify Homefront2_Release.exe
  python3 patcher.py --apply Homefront2_Release.exe
  python3 patcher.py --revert Homefront2_Release.exe
  python3 patcher.py --apply Homefront2_Release.exe --patches 10,19,20A,20B,20C,21
"""
    )
    parser.add_argument("target", help="Path to Homefront2_Release.exe")
    parser.add_argument("--verify", action="store_true", help="Verify status of all patches on target binary")
    parser.add_argument("--apply", action="store_true", help="Apply patches to target binary")
    parser.add_argument("--revert", action="store_true", help="Revert patches to clean vanilla")
    parser.add_argument("--patches", type=str, help="Comma-separated patch IDs to apply/revert (e.g. 10,19,21)")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a .vanilla backup before patching")

    args = parser.parse_args()

    patches = load_patches()
    selected_ids = [s.strip() for s in args.patches.split(",")] if args.patches else None

    if args.verify:
        verify_target(args.target, patches)
    elif args.apply:
        apply_patches(args.target, patches, selected_ids, backup=not args.no_backup)
    elif args.revert:
        revert_patches(args.target, patches, selected_ids)
    else:
        # Default action: verify
        verify_target(args.target, patches)


if __name__ == "__main__":
    main()
