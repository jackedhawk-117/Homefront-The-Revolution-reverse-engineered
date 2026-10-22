# Third-Person Over-the-Shoulder Camera & Dynamic Aiming System

## Overview
This document details the reverse engineering, disassembly, and implementation of the Over-The-Shoulder (OTS) Third-Person Camera and dynamic aiming system in *Homefront: The Revolution* (CryEngine 3.8 x86-64 PE).

---

## 1. Architecture & Call Hierarchy

```mermaid
flowchart TD
    subgraph View Pipeline
        A["CPlayerView::UpdateView()<br><code>0x14093f2c8</code>"] --> B{"CPlayer::IsThirdPerson()<br><code>0x1406e1e0c</code>"}
        B -->|Evaluator: 0 (ADS or Hacking)| C["ProcessFirstPersonView()<br><code>0x14093a2ec</code><br>• 1P Iron Sights / Scope Alignment<br>• Smartphone Hacking Minigame UI<br>• Zero aiming/laser parallax"]
        B -->|Evaluator: 1 (Traversal / Hipfire)| D["ProcessThirdPersonView()<br><code>0x140937478</code><br>• Distance: 1.85m (cl_tpvDist)<br>• Bone track: Head/Neck<br>• Collision Sweep: <code>0x1406e6ff8</code>"]
        D --> E["OTS Calibration Stub<br><code>0x141f79b00</code><br>• Lateral Right Shoulder: +0.38m<br>• Elevation Lowering: -0.18m"]
    end
    subgraph Character Mesh Management
        F["Mesh Visibility Manager<br><code>0x140704ee0</code>"] --> G{"IsThirdPerson()"}
        G -->|1 (3P)| H["<code>0x1406f5068</code>: Show Ethan Brady 3D Body (Slot 5)<br><code>0x140826318</code>: Suppress 1P floating arms<br><code>0x1406f5183</code>: Hide unowned socket attachments"]
        G -->|0 (1P ADS)| I["<code>0x1406f5068</code>: Suppress 3P Body (prevent clipping)<br><code>0x140826318</code>: Render 1P weapon model & iron sights"]
    end
```

---

## 2. Reverse Engineering Findings

### A. Dynamic 1P / 3P Switch (`CPlayer::IsThirdPerson` at `0x1406e1e0c` & `0x141f79ad0`)
- In CryEngine, the local player's view and rendering pipelines both check `CPlayer::IsThirdPerson()`.
- The engine includes a built-in state evaluator at `0x1406e3e88` taking `CPlayer::m_pController` (`[CPlayer + 0x1160]`):
  - Queries `IZoomMode::IsZoomed()`: returns `0` if player is Aiming Down Sights (ADS).
  - Queries `CPlayer::IsInteracting()`: returns `0` if player is using smartphone / hacking minigame.
  - Returns `1` during normal hipfire, sprinting, walking, and traversal.
- **Hook & Stub:**
  - `0x1406e1e0c` jumps to code cave at `0x141f79ad0`:
    ```assembly
    0x141f79ad0: xor    eax, eax
    0x141f79ad2: cmp    byte ptr [rcx + 0x29c], al      ; IsClient check
    0x141f79ad8: je     0x141f79af7                     ; AI / remote players return 1
    0x141f79ada: mov    rax, qword ptr [rcx + 0x1160]   ; Controller*
    0x141f79ae1: test   rax, rax
    0x141f79ae4: je     0x141f79af7
    0x141f79ae6: sub    rsp, 0x28
    0x141f79aea: mov    rcx, rax
    0x141f79aed: call   0x1406e3e88                     ; Dynamic evaluator
    0x141f79af2: add    rsp, 0x28
    0x141f79af6: ret
    0x141f79af7: mov    eax, 1
    0x141f79afc: ret
    ```

### B. Gears of War Over-The-Shoulder Calibration (`0x14093f469` & `0x141f79b00`)
- In `CPlayerView::UpdateView`, right after `ProcessThirdPersonView`, the camera position and rotation quaternion `q = (x, y, z, w)` are committed.
- To produce a true *Gears of War* perspective:
  - **Height:** The camera was lowered by `-0.18m` ($18\text{ cm}$) so the viewpoint sits directly at shoulder height rather than looking down at Ethan's scalp.
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
| `ThirdPerson_DynamicSwitch_Stub` | `0x141f79ad0` | `0x1f78ed0` | 48 B | `00` $\times 48$ | `31c038819c020000...` | Evaluates ADS and hacking states for dynamic 1P/3P switching |
| `ThirdPerson_CameraDistance` | `0x1408a481a` | `0x8a3c1a` | 8 B | `f30f101d86f37501` | `f30f101d0afb9401` | Tightens camera distance from 3.5m to 1.85m |
| `ThirdPerson_CameraOTS_Hook` | `0x14093f469` | `0x93e869` | 16 B | `8b0389078b430489...` | `e992a6630190...` | Intercepts view commit in `CPlayerView::UpdateView` |
| `ThirdPerson_CameraOTS_Stub` | `0x141f79b00` | `0x1f78f00` | 172 B | `00` $\times 172$ | `f30f104308f30f5c...` | Applies $+0.38\text{m}$ Right-vector offset and $-0.18\text{m}$ elevation |
| `ThirdPerson_HolsterCleanup` | `0x1406f5183` | `0x6f4583` | 6 B | `8bfe400f94c7` | `bf0100000090` | Hides unowned socket weapons on Ethan's mesh |

---

## 4. Verification Checksums

- **Vanilla Binary MD5:** `0326ea202fcd7ceb3760d14bc8d07f63`
- **Patched Binary MD5:** `c3402bd8800ec626ee65abc3ae87032c`
- **Patched Binary SHA256:** `d970b57684e83bb4446b419783e47fc37a87585625015d25319ea1e60ef10ea5`
