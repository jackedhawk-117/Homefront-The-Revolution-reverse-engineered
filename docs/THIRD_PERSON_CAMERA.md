# Third-Person Over-the-Shoulder Camera & Dynamic Aiming System

## Overview
This document details the reverse engineering, disassembly, and implementation of the Over-The-Shoulder (OTS) Third-Person Camera and dynamic aiming system in *Homefront: The Revolution* (CryEngine 3.8 x86-64 PE).

---

## 1. Architecture & Call Hierarchy

```mermaid
flowchart TD
    subgraph Input & Perspective Pipeline
        A["F1 Key Press (GetAsyncKeyState VK_F1 0x70)"] --> B{"Toggle Mode<br><code>g_thirdPersonEnabled</code>"}
        B -->|0 (Default)| C["1st-Person Perspective (100% Vanilla)<br>• 1P Camera inside head<br>• 1P Iron Sights & Scopes<br>• 1P Smartphone Hacking Minigames<br>• 1P Interaction prompts"]
        B -->|1| D["3rd-Person Perspective Enabled"]
        D --> E{"Right Mouse Button (VK_RBUTTON 0x02)?"}
        E -->|Pressed (Holding RMB)| F["Dynamic ADS Snap to 1st Person<br>• Iron sights / scope right up to eye<br>• 100% Laser-accurate aim with zero parallax"]
        E -->|Released (Hipfire / Traversal)| G["Over-The-Shoulder 3rd Person View<br>• Gears of War camera placement (+0.38m Right, -0.18m elevation, 1.85m distance)<br>• Full 3D Ethan Brady character rendering<br>• Hipfire from 3rd person"]
    end
```

---

## 2. Reverse Engineering Findings

### A. F1 Hotkey Toggle & Right-Click ADS Switch (`0x1406e1e0c` & `0x141f79ad0`)
- CryEngine's local player perspective is determined by `CPlayer::IsThirdPerson()`.
- Instead of forcing third person unconditionally, `0x1406e1e0c` redirects to an input-driven stub at `0x141f79ad0` utilizing `USER32.dll!GetAsyncKeyState` (imported in IAT at `0x141f7e240`):
  1. **AI / Companions Check:** If `[rcx + 0x29c] == 0` (remote player or AI), returns `1` immediately so companions and enemies always render their full 3D bodies.
  2. **F1 Toggle:** Checks `GetAsyncKeyState(VK_F1 = 0x70)`. An edge-triggered latch flips `g_thirdPersonEnabled` between 0 and 1. The game starts in **1st-person mode by default** (`g_thirdPersonEnabled = 0`).
  3. **RMB Aiming:** When 3rd-person is active (`g_thirdPersonEnabled == 1`), the stub queries `GetAsyncKeyState(VK_RBUTTON = 0x02)`:
     - When Right Mouse Button is held down $\implies$ returns `0` (First Person). The game immediately executes vanilla iron sights / scope aiming with zero parallax.
     - When Right Mouse Button is released $\implies$ returns `1` (Third Person). Snaps back to OTS 3rd person.

### B. Gears of War Over-The-Shoulder Calibration (`0x14093f469` & `0x141f79b50`)
- In `CPlayerView::UpdateView`, right after `ProcessThirdPersonView`, the camera position and rotation quaternion $q = (x, y, z, w)$ are committed.
- To produce a true *Gears of War* perspective:
  - **Height:** Lowered by `-0.18m` ($18\text{ cm}$) so the viewpoint sits directly at upper shoulder level rather than looking down at Ethan's scalp.
  - **Lateral Right-Shoulder Offset:** From the view orientation quaternion $\hat{q}$, the horizontal Right-basis vector is derived:
    $$R_x = 1 - 2(q_y^2 + q_z^2)$$
    $$R_y = 2(q_x q_y + q_w q_z)$$
    The position is shifted along $\vec{R}$ by $+0.38\text{ m}$ ($38\text{ cm}$), maintaining the camera over Ethan's right shoulder across all 360° yaw rotations.

### C. Character Model Holstered Weapons Cleanup (`0x1406f5183`)
- In `CPlayer::UpdateCharacterAttachments()`, default socket attachments defined in the character mesh (shotgun on back, pistol on holster) were rendered even when not in inventory.
- At `0x1406f5183`, forcing `edi = 1` calls `IAttachment::HideAttachment(1)` for body sockets, removing unowned default props while preserving Ethan's active held weapon.

---

## 3. Binary Patch Specifications

| Patch Name | Virtual Address | File Offset | Size | Vanilla Bytes | Patched Bytes | Purpose |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `ThirdPerson_DynamicSwitch_Hook` | `0x1406e1e0c` | `0x6e120c` | 24 B | `33c038819c020000...` | `e9bf7c890190...` | Redirects `CPlayer::IsThirdPerson` to evaluator stub |
| `ThirdPerson_F1_RMB_Stub` | `0x141f79ad0` | `0x1f78ed0` | 128 B | `00` $\times 128$ | `4885c9746d80...` | F1 toggles 1P/3P (1P default); holding RMB switches to 1P iron sights |
| `ThirdPerson_CameraDistance` | `0x1408a481a` | `0x8a3c1a` | 8 B | `f30f101d86f37501` | `f30f101d0afb9401` | Tightens camera distance from 3.5m to 1.85m |
| `ThirdPerson_CameraOTS_Hook` | `0x14093f469` | `0x93e869` | 16 B | `8b0389078b430489...` | `e9e2a6630190...` | Intercepts view commit in `CPlayerView::UpdateView` |
| `ThirdPerson_CameraOTS_Stub` | `0x141f79b50` | `0x1f78f50` | 164 B | `00` $\times 164$ | `f30f104308f30f5c...` | Applies $+0.38\text{m}$ Right-vector offset and $-0.18\text{m}$ elevation |
| `ThirdPerson_HolsterCleanup` | `0x1406f5183` | `0x6f4583` | 6 B | `8bfe400f94c7` | `bf0100000090` | Hides unowned socket weapons on Ethan's mesh |

---

## 4. Verification Checksums

- **Vanilla Binary MD5:** `0326ea202fcd7ceb3760d14bc8d07f63`
- **Patched Binary MD5:** `a22285289209320e54c51cdff2b6d656`
- **Patched Binary SHA256:** `d5b24405a61f50a2078e391e4646f567fac3ffb3a74038d3f6abad568b4c3021`
