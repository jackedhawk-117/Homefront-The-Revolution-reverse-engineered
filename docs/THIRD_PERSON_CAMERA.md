# Third-Person Over-the-Shoulder Camera & Native Dynamic Aiming System

## Overview
This document details the reverse engineering, disassembly, and implementation of the Over-The-Shoulder (OTS) Third-Person Camera, DirectInput Keyboard Hotkey Toggle, and unified dynamic perspective transitions in *Homefront: The Revolution* (CryEngine 3.8 x86-64 PE).

---

## 1. Architecture & Call Hierarchy

```mermaid
flowchart TD
    subgraph DirectInput Keyboard Pipeline [CKeyboard::ProcessKey 0x140f99220]
        K1["Physical Key Press: F1 / F2 / F3"] --> K2["DirectInput8 GetDeviceData"]
        K2 --> K3["CKeyboard::Update -> ProcessKey (0x140f99220)"]
        K3 --> K4["Keyboard Hook (Patch #25A at 0x140f99220)"]
        K4 --> K5["Keyboard Stub (Patch #25B at 0x141f79ad0 in .text)"]
        K5 --> K6{"r8b == 1?<br>(Key Pressed, not Released?)"}
        K6 -->|No: Key Released| K10["Execute Replaced Prologue"]
        K6 -->|Yes: Key Down| K7{"edx == DIK_F1 (0x3B)<br>or DIK_F2 (0x3C)<br>or DIK_F3 (0x3D)?"}
        K7 -->|No: Other Key| K10
        K7 -->|Yes: Match| K8["xor byte ptr [0x1425b1d40], 1<br>(Atomic Toggle g_bThirdPersonMode)"]
        K8 --> K10
        K10 --> K11["Resume Native CKeyboard::ProcessKey (0x140f9922f)"]
    end

    subgraph Dynamic Perspective Pipeline [CPlayerView::UpdateView 0x14093f357]
        A["Render Frame: CPlayerView::UpdateView"] --> B["Dynamic Transition Hook (0x14093f357)"]
        B --> C["Unified Evaluator Stub (0x141f7c148 in PSFD00)"]
        C --> D{"g_bThirdPersonMode == 1?<br>(F1/F2/F3 Hotkey Active?)"}
        D -->|No: Hotkey OFF| E["Desired = 0 (Vanilla 1st Person Default)"]
        D -->|Yes: Hotkey ON| F{"[pPlayer + 0xaec] < 0.99f?<br>(Right-Click ADS Zoom Active?)"}
        F -->|Yes: In ADS| E
        F -->|No| G{"[pPlayer + 0x1cd] & 2?<br>(Sprint Sliding Active?)"}
        G -->|Yes: Sliding| E
        G -->|No| H{"[pPlayer + 0x198] != 0?<br>(Hacking Minigame Entity?)"}
        H -->|Yes: Minigame| E
        H -->|No| I{"Interactive Action Flag 0x4000?<br>(Terminal / Lockpick / Takedown)"}
        I -->|Yes: Action| E
        I -->|No| J{"CSmartPhoneOS + 0x78c != 0?<br>(Phone 'V' or Map 'M' Open)"}
        J -->|Yes: Phone/Map| E
        J -->|No| K{"CMenuManager + 0x17d4 == 6 or 7?<br>(Weapon Customize 'X' / Merchant Shop)"}
        K -->|Yes: Customizing| E
        K -->|No: Traversal / Hipfire| L["Desired = 1 (OTS 3rd Person)"]
        
        E --> M{"[pPlayer + 0x1bd] == Desired?"}
        L --> M
        M -->|Yes: State Unchanged| N["Return al = Desired"]
        M -->|No: State Changed| O["Call Native CPlayer::SetThirdPerson(pPlayer, Desired) (0x14070e35c)"]
        
        O --> P["Engine Transition Dispatcher (0x140704fd8)<br>• CPlayer::SetCharacterVisibility (0x1406f5068)<br>• CWeapon::SetFirstPerson (0x140826318) -> Toggles Slot 0 (1P) vs Slot 1 (3P)<br>• Updates Firing Muzzle Helper to muzzle_flash_fp<br>• Notifies Weapon & Animation Listeners"]
        P --> N
    end

    subgraph Camera Calibration Pipeline [CPlayerView::UpdateView 0x14093f469]
        N --> Q{"al == 1?<br>(Third Person Active?)"}
        Q -->|Yes: Hipfire OTS| R["ProcessThirdPersonView (0x140937478)"]
        R --> S["OTS Calibration Stub (0x141f79b50)<br>• Shifts camera +0.38m along quaternion Right-basis vector<br>• Lowers elevation by -0.18m<br>• Preserves 360° rotational tracking"]
        Q -->|No: 1st Person Context| T["Execute 1st-Person Camera<br>• Snaps directly down 3D iron sights / optic center / phone / customize<br>• Zero parallax<br>• Wall bullet impacts register accurately"]
    end
```

---

## 2. Reverse Engineering Findings & Root Cause Analysis

### A. Root Cause of Missing 1P Weapon Model & Invisible Bullet Impacts
In earlier dynamic perspective builds, `CPlayer::IsThirdPerson()` (`0x1406e1e0c`) was hooked directly to evaluate `[CPlayer + 0xaec] < 0.99f`. While this successfully shifted the camera to first person during ADS, it produced two critical bugs:
1. **Weapon 3D Model Disappeared:** In CryEngine, weapons maintain separate geometry slots:
   - `eIGS_FirstPerson` (`Slot 0`): First-person animated weapon mesh and optics, attached to 1st-person arms.
   - `eIGS_ThirdPerson` (`Slot 1`): Third-person weapon model, attached to Ethan's 3rd-person body hand socket (`Bip01 R Hand`).
   Merely changing the return value of `IsThirdPerson()` in the camera calculation never called the weapon switch dispatcher (`0x140826318`), leaving `Slot 0` uninitialized and dormant.
2. **Invisible Bullet Impacts:** In weapon firing (`0x140411da0`), the engine verifies whether `IsThirdPerson()` is active. When it saw `0`, it called `IActor::GetCharacter(0)` (`0x140411f8c`) to query the weapon attachment in character slot 0. Because slot 0 was never equipped, the attachment pointer returned `NULL` (`0x140411fc4`), jumping to `0x140412995` which aborted the shot. **No bullet was ever spawned, no raycast was performed, and no bullet impact appeared on the wall.**

### B. Discovery of Native Engine Switch Method: `CPlayer::SetThirdPerson` (`0x14070e35c`)
Binary disassembly revealed that CryEngine already possesses an official, thread-safe function to transition a player between 1st person and 3rd person:
```assembly
; CPlayer::SetThirdPerson(CPlayer* this, bool bThirdPerson) at 0x14070e35c:
0x14070e35c: mov [rsp + 8], rbx
0x14070e361: push rdi
0x14070e362: sub rsp, 0x20
0x14070e366: mov rdi, rcx
0x14070e369: cmp byte ptr [rcx + 0x1bd], dl   ; Check if [CPlayer + 0x1bd] == dl
0x14070e36f: je 0x14070e3b5                  ; If already in target state, return immediately!
0x14070e371: mov byte ptr [rcx + 0x1bd], dl  ; Update internal state flag
0x14070e377: call 0x140704fd8                 ; Call engine transition dispatcher!
0x14070e37c: cmp qword ptr [rdi + 0x1078], 0
...                                          ; Notifies weapon and animation listeners
0x14070e3bf: ret
```

When `CPlayer::SetThirdPerson(pPlayer, 0)` is invoked on entering ADS or in-game 1P actions:
- It calls `0x140704fd8` $\to$ `0x140704ee0`.
- It executes `0x1406f5068` with `dl = 0` to configure 1st-person character arms and meshes.
- It calls `0x140826318` on the equipped weapon (`CWeapon*`) with `dl = 1`:
  - Activates `Slot 0` (1st-person weapon model, iron sights, optics).
  - Updates the firing muzzle helper to `muzzle_flash_fp`.
- Firing raycasts find the weapon attachment in slot 0, bullet trajectories register directly along the iron sightline, and bullet impacts appear on the targeted wall.

When `CPlayer::SetThirdPerson(pPlayer, 1)` is invoked on returning to OTS 3P:
- It calls `0x140826318` with `dl = 0`:
  - Activates `Slot 1` (3rd-person weapon model attached to Ethan's hands).
- Restores 3rd-person full body rendering.
- Camera returns to the calibrated OTS position (+0.38m Right, -0.18m elevation, 1.85m distance).

### C. DirectInput Architecture vs Win32 Message Pump Failure
- In *Homefront: The Revolution* running under Wine/Proton on Linux, keyboard input is acquired exclusively through DirectInput 8 (`DINPUT8.dll!DirectInput8Create` called at `0x140fa442d`).
- The standard Win32 message pump (`PeekMessageW` / `GetMessageW` / `WndProc`) does **not** process gameplay keyboard strokes because DirectInput acquires buffered physical scan codes directly from the OS/driver.
- Hooking `PeekMessageW` failed because keyboard messages never passed through that loop during gameplay.
- **The Solution:** Intercept `CKeyboard::ProcessKey` (`0x140f99220`), which is called directly from `CKeyboard::Update` (`0x140f99390`) as DirectInput `GetDeviceData` flushes its buffered `DIDEVICEOBJECTDATA` array.
- In `CKeyboard::ProcessKey`:
  - `edx` holds the DirectInput scan code (`DIK_F1 = 0x3B`, `DIK_F2 = 0x3C`, `DIK_F3 = 0x3D`).
  - `r8b` holds the key state (`1` = key pressed, `0` = key released).
- DirectInput reports state transitions without OS autorepeat spam, allowing a clean, atomic toggle of `g_bThirdPersonMode` at VA `0x1425b1d40`.

### D. In-Game Contextual 1st-Person Actions
Certain in-game interactions in *Homefront: The Revolution* are hardcoded for first-person rendering. The unified dynamic evaluator at `0x141f7c148` natively detects them:
1. **Weapon Customization (X key):** Modular on-the-fly weapon customization inspects `gEnv` (`0x14262eaf8`) $\to$ `CMenuManager* [rax + 0x1d0]` $\to$ `[rax + 0x17d4]`. When menu ID is 6 (`WeaponCustomization`) or 7 (`MerchantShop`), it forces 1st person so attachments and modular barrel/optic conversions are fully visible.
2. **Sprint-Sliding (Ctrl while sprinting):** Native 3P Ethan mesh lacks a standalone 3P sliding animation. The evaluator reads `[CPlayer + 0x1cd] & 2` (sliding state bit 9 of `[CPlayer + 0x1cc]`). When sliding begins, it drops to 1st person, plays the complete camera sliding animation, and seamlessly snaps back to 3P upon completion.
3. **Smartphone (V key) & Map (M key):** Detected through `g_pGameFramework` (`0x14262ebf8`) $\to$ `CSmartPhoneOS* [rax + 0x420]` $\to$ `[rax + 0x78c] != 0`.
4. **Hacking Minigames & Terminal Interactions:** Strike terminals, lockpicking, and drone control are detected via `[CPlayer + 0x198] != 0` or interactive action flag `0x4000` at `[[[CPlayer + 0x1040] + 0x20] + 8]`.

---

## 3. Dynamic Transition Hook & Stub Specification

### A. DirectInput Keyboard Hook (`0x140f99220`, Patch #25A, 15 Bytes)
```assembly
; In CKeyboard::ProcessKey at 0x140f99220:
0x140f99220: jmp 0x141f79ad0              ; Jump to ThirdPerson_Keyboard_Stub
0x140f99225: nop (x10)
```

### B. DirectInput Keyboard Stub (`0x141f79ad0`, Patch #25B, 128 Bytes in `.text`)
```assembly
0x141f79ad0: test r8b, r8b                     ; Key pressed? (1 = down, 0 = up)
0x141f79ad3: jz .orig                          ; Ignore key release
0x141f79ad5: cmp edx, 0x3b                     ; DIK_F1?
0x141f79ad8: je .toggle
0x141f79ada: cmp edx, 0x3c                     ; DIK_F2?
0x141f79add: je .toggle
0x141f79adf: cmp edx, 0x3d                     ; DIK_F3?
0x141f79ae2: jne .orig
.toggle:
0x141f79ae4: xor byte ptr [rip + 0x638255], 1  ; Atomically toggle g_bThirdPersonMode at 0x1425b1d40
.orig:
0x141f79aeb: mov qword ptr [rsp + 0x18], rbx   ; Replaced original prologue
0x141f79af0: mov qword ptr [rsp + 0x20], rbp
0x141f79af5: push rsi
0x141f79af6: sub rsp, 0x60
0x141f79afa: jmp 0x140f9922f                   ; Resume native CKeyboard::ProcessKey
```

### C. Dynamic Transition Hook (`0x14093f357`, Patch #22A, 9 Bytes)
Replaces `mov rax, [rdx]; call [rax + 0x228]` with a direct jump to the unified evaluator stub in `PSFD00`:
```assembly
0x14093f357: jmp 0x141f7c148
0x14093f35c: nop
0x14093f35d: nop
0x14093f35e: nop
0x14093f35f: nop
```

### D. Unified Perspective Evaluator Stub (`0x141f7c148`, Patch #22B, 180 Bytes in `PSFD00`)
```assembly
0x141f7c148: xor ebx, ebx                      ; Desired = 0 (1st person default)
0x141f7c14a: cmp byte ptr [rip + 0x635bef], 1  ; g_bThirdPersonMode at 0x1425b1d40
0x141f7c151: jne .apply                        ; If hotkey mode is 0 -> force 1st person

0x141f7c157: mov eax, dword ptr [rdx + 0xaec]  ; Check ADS zoom FOV multiplier
0x141f7c15d: cmp eax, 0x3f7d70a4               ; 0.99f threshold
0x141f7c162: jb .apply                         ; ADS engaged -> force 1st person

0x141f7c164: test byte ptr [rdx + 0x1cd], 2    ; Check sprint sliding flag
0x141f7c16b: jne .apply                        ; Sliding -> force 1st person

0x141f7c16d: cmp dword ptr [rdx + 0x198], 0    ; Check hacking minigame entity
0x141f7c174: jne .apply                        ; Minigame active -> force 1st person

0x141f7c176: mov rax, qword ptr [rdx + 0x1040] ; Check interactive action flag
0x141f7c17d: test rax, rax
0x141f7c180: jz .check_phone
0x141f7c182: mov rax, qword ptr [rax + 0x20]
0x141f7c186: test rax, rax
0x141f7c189: jz .check_phone
0x141f7c18b: test dword ptr [rax + 8], 0x4000  ; Interactive action bit 14
0x141f7c193: jne .apply                        ; Terminal / lockpick -> force 1st person

.check_phone:
0x141f7c195: mov rax, qword ptr [rip + 0x6b2a5d] ; g_pGameFramework (0x14262ebf8)
0x141f7c19c: test rax, rax
0x141f7c19f: jz .check_menu
0x141f7c1a1: mov rax, qword ptr [rax + 0x420]    ; CSmartPhoneOS*
0x141f7c1a8: test rax, rax
0x141f7c1ab: jz .check_menu
0x141f7c1ad: cmp dword ptr [rax + 0x78c], 0      ; Phone/Map active
0x141f7c1b4: jne .apply                        ; Phone/Map open -> force 1st person

.check_menu:
0x141f7c1b6: mov rax, qword ptr [rip + 0x6b293c] ; gEnv (0x14262eaf8)
0x141f7c1bd: test rax, rax
0x141f7c1c0: jz .enable_tp
0x141f7c1c2: mov rax, qword ptr [rax + 0x1d0]    ; CMenuManager*
0x141f7c1c9: test rax, rax
0x141f7c1cc: jz .enable_tp
0x141f7c1ce: mov al, byte ptr [rax + 0x17d4]     ; Active menu ID
0x141f7c1d4: and al, 0xfe
0x141f7c1d6: cmp al, 6                           ; Menu 6 (Customize) or 7 (Shop)
0x141f7c1d8: je .apply

.enable_tp:
0x141f7c1da: mov bl, 1                           ; OTS 3rd person!

.apply:
0x141f7c1dc: cmp byte ptr [rdx + 0x1bd], bl      ; Check if state changed
0x141f7c1e2: je .done                            ; No change -> skip call
0x141f7c1e4: sub rsp, 0x28                       ; 16-byte aligned stack frame
0x141f7c1e8: mov dl, bl                          ; dl = desired
0x141f7c1ea: mov rcx, r12                        ; rcx = pPlayer
0x141f7c1ed: call 0x14070e35c                    ; Native CPlayer::SetThirdPerson!
0x141f7c1f2: add rsp, 0x28

.done:
0x141f7c1f6: mov al, bl                          ; Return value al = desired
0x141f7c1f8: jmp 0x14093f360                     ; Resume CPlayerView::UpdateView
```

---

## 4. Active Binary Patch Table (30 Patches Total)

| Patch Name | Virtual Address | File Offset | Size | Purpose |
| :--- | :--- | :--- | :---: | :--- |
| `ThirdPerson_DynamicTransition_Hook` (#22A) | `0x14093f357` | `0x93e757` | 9 B | Intercepts `CPlayerView::UpdateView` to jump to unified evaluator |
| `ThirdPerson_DynamicTransition_Stub` (#22B) | `0x141f7c148` | `0x1f7b148` | 180 B | Evaluates F1/F2/F3 mode, ADS zoom, sliding, weapon customize, phone/map, minigames |
| `ThirdPerson_CameraDistance` (#23) | `0x1408a481a` | `0x8a3c1a` | 8 B | Tightens camera distance from 3.5m to 1.85m action perspective |
| `ThirdPerson_CameraOTS_Hook` (#24A) | `0x14093f469` | `0x93e869` | 16 B | Intercepts view commit in `CPlayerView::UpdateView` |
| `ThirdPerson_CameraOTS_Stub` (#24B) | `0x141f79b50` | `0x1f78f50` | 164 B | Applies $+0.38\text{m}$ Right-vector offset and $-0.18\text{m}$ elevation (*Gears of War* OTS) |
| `ThirdPerson_Keyboard_Hook` (#25A) | `0x140f99220` | `0xf98620` | 15 B | Hooks `CKeyboard::ProcessKey` to intercept DirectInput F1/F2/F3 scan codes |
| `ThirdPerson_Keyboard_Stub` (#25B) | `0x141f79ad0` | `0x1f78ed0` | 128 B | Atomic F1/F2/F3 toggle stub in `.text` (toggles `g_bThirdPersonMode` at `0x1425b1d40`) |

---

## 5. Verification Checksums

- **Vanilla Binary MD5:** `0326ea202fcd7ceb3760d14bc8d07f63`
- **Vanilla Binary SHA256:** `c81fc8d6d61195a8f99d303926bcf32f6ca6638d8fa2deac9fc2d10c9ae4133c`
- **Fully Patched Binary MD5:** `ff60ce72d070935e4a068d812e2fb6df`
- **Fully Patched Binary SHA256:** `722c4af6c0662c76ed437a0ca932e0626ee669a3efa979d91aa9c911b76cf31f`
