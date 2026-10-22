# Homefront: The Revolution (PC / Steam) - Reverse Engineering Notes

## Target Binary Information
- **Original Path:** `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
- **Original / Vanilla MD5:** `0326ea202fcd7ceb3760d14bc8d07f63`
- **Original / Vanilla SHA256:** `c81fc8d6d61195a8f99d303926bcf32f6ca6638d8fa2deac9fc2d10c9ae4133c`
- **Vanilla Backup Path:** `/home/jackedhawk117/rework/Homefront2_Release.exe.vanilla`
- **Working Patched Copy Path:** `/home/jackedhawk117/rework/Homefront2_Release.exe`
- **Working Patched Copy MD5:** `bd8e59ab17bf837152d23bea97f84239`
- **Working Patched Copy SHA256:** `1e269b14371da098ece2ca09fad6a29c0e4b836f8ca31fc41e3f9384ce97d9e9`
- **Architecture:** PE32+ (x86-64 / AMD64), GUI subsystem
- **Default Image Base:** `0x140000000`
- **Entry Point RVA:** `0x1c512bc` (VA: `0x141c512bc`)

## Save Games Backup
- **Backup Directory:** `/home/jackedhawk117/rework/saves-backup/SaveGames/`
- **Original Directory:** `/home/jackedhawk117/.local/share/Steam/steamapps/compatdata/223100/pfx/drive_c/users/steamuser/Saved Games/homefront2/SaveGames/`
- **Status:** Backed up successfully (slots 1 through 4 including `*.csf`, `*.bmm`, `*.meta`, and `*.bmc`).

---

## Phase 4: Overwhelming KPA Guerrilla Presence Patch Suite

All 9 patches use **In-Binary Native Redirection / Instruction Immediates** inside `.text` (0 bytes modified in `.rdata` or `.data`), ensuring 100% stability.

| Patch # | Parameter Name | Instruction VA | File Offset | Original Value / Instruction | New Value / Instruction | Gameplay Impact |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| **#1** | `emd_softAgentLimit` | `0x14036ab29` | `0x369f29` | `24.0f` (`[rip+0x1ca388b]`) | **`96.0f`** (`[rip+0x1e6f5cf]`) | 4x baseline active AI population cap |
| **#2** | `emd_spreadSoftAgentLimit` | `0x14036ab62` | `0x369f62` | `60.0f` (`[rip+0x1d6d91a]`) | **`150.0f`** (`[rip+0x1c7de4e]`) | 2.5x spatial grid density ceiling |
| **#3** | `emd_hardAgentLimit` | `0x14036ab9b` | `0x369f9b` | `64.0f` (`[rip+0x1ca3719]`) | **`150.0f`** (`[rip+0x1c7de15]`) | 2.3x absolute world hard cap |
| **#4** | `emd_repopulateDelay` | `0x14036ac75` | `0x36a075` | `100.0f` (`[rip+0x1c6368b]`) | **`5.0f`** (`[rip+0x1c42bfb]`) | Waves respawn in 5s instead of 100s |
| **#5** | `emd_escortReinforcements_retry` | `0x14036a29d` | `0x36969d` | `5.0f` (`[rip+0x1c435d2]`) | **`2.5f`** (`[rip+0x1c592f6]`) | Halves failed reinforcement retry delay |
| **#6** | `emd_gridActiveRadius` | `0x14036a664` | `0x369a64` | `40.0f` (`[rip+0x1cbe65c]`) | **`80.0f`** (`[rip+0x1c44950]`) | 4x active area around player; pulls multi-block patrols |
| **#7** | `emd_perFrameSpawnLimit` | `0x14036a4f5` | `0x3698f5` | `1` (`lea ebp, [r12 + 1]`) | **`4`** (`lea ebp, [r12 + 4]`) | Spawns full 4-man fireteams instantaneously |
| **#8** | `g_dynamicPatrol_maxPatrols` | `0x1408449f0` | `0x843df0` | `2` (`mov edi, 2`) | **`8`** (`mov edi, 8`) | 4x more roaming patrols concurrently in the sector |
| **#9** | `g_dynamicPatrol_SoldierPresence` | `0x140844a26` | `0x843e26` | `2.22f` (`[rip+0x177810a]`) | **`5.0f`** (`[rip+0x1768e4a]`) | More than doubles the troop count per patrol squad |
| **#10** | `dtp_maxAgents` | `0x140886f8d` | `0x88638d` | `4` (`mov r9d, 4`) | **`12`** (`mov r9d, 12`) | Increases maximum Resistance follower recruitment cap from 4 to 12 |
| **#11** | `formation_minRadius` | `0x1405caf68` | `0x5ca368` | `2.0f` (`[rip+0x1a9002f]`) | **`5.0f`** (`[rip+0x1a9004f]`) | Expands inner follower buffer from 2m to 5m, clearing doorways and corridors |
| **#12** | `formation_spacingScalar` | `0x1405cb005` | `0x5ca405` | `3.0f` (`[rip+0x1a8ff96]`) | **`5.0f`** (`[rip+0x1a8ffb2]`) | Expands outer squad perimeter from ~12.4m to ~22.3m so 12 members fan out into cover |


---

## Ghidra Symbol Registry
| Address | Identifier | Description |
| :--- | :--- | :--- |
| `0x141c512bc` | `entry` | CRT Entry point (`WinMainCRTStartup`) |
| `0x14000fb10` | `htr_WinMain` | WinMain entry function (parses cmdline, initializes engine & Steam) |
| `0x140002c20` | `htr_SteamAPI_Init` | Calls `SteamAPI_RestartAppIfNecessary(223100)` and `SteamAPI_Init()` |
| `0x140d9e270` | `htr_CSystem_InitConsoleVariables` | Registers engine system console variables (including `sys_PakPriority`) |
| `0x140da4770` | `htr_CAISystem_InitConsoleVariables` | Registers AI system console variables |
| `0x14036a260` | `htr_EMD_InitConsoleVariables` | Registers Emergent Manager Dynamic CVars (`emd_*`) |
| `0x140365590` | `htr_EMD_UpdateDynamicAgentLimit` | Evaluates runtime soft agent limits and performance thresholds |
| `0x140371c00` | `htr_EMD_CalculateCellPopulationQuota` | Computes active population allocations per grid cell |
| `0x1404530c8` | `htr_FlowNode_DynamicPatrolPresence_ProcessEvent` | FlowGraph node managing dynamic soldier/drone/vehicle presence |
| `0x1404522d8` | `htr_FlowNode_RequestReinforcements_Init` | FlowGraph node initializing reinforcement wave distance properties |
| `0x140452770` | `htr_FlowNode_RequestReinforcements_SpawnSquad` | Spawns reinforcement squad from archetype pool |
| `0x1406f2e8c` | `htr_CDifficultyManager_LoadDifficultyCVarCfg` | Executes difficulty config script (`difficulty/hard.cfg`, etc.) |
| `0x140d6b8e0` | `htr_MountCDRArchive` | Mounts `cdr.pak` Central Directory Record archive |
| `0x140d2f400` | `htr_DecryptBuffer_AES_CTR` | LibTomCrypt AES-128 CTR archive decryptor worker |
| `0x140d31920` | `htr_ZipDir_Cache_DecompressFile` | Decompresses archive entries (Deflate method 8, LZ method 11) |

---

## Recruit cap

### Phase 1: Locating the Recruit Cap and Squad Mechanism

#### 1. Recruitment Subsystem: DefendThePlayer (`dtp_*`)
Investigation of strings and xrefs confirmed that Resistance recruitment in single-player is managed by the **DefendThePlayer** system (AI goal `DefendThePlayerGoal`, component logic in `HumanPlayerComponent.cpp`).

Console variables for this subsystem are initialized in `CDefendThePlayerManager::InitConsoleVariables` at **VA `0x140886e68`** (file offset `0x886268`):
- **`dtp_maxAgents`** (VA `0x1420d8ec8`, offset `0x20d70c8`):
  - Description: `"DefendThePlayer: Max Agents. Set to 0 to disable."`
  - Registered at **VA `0x140886f86`** (offset `0x886386`) into struct offset `+0xc` (`gEnv + 0x90c`).
  - Default value registered: **`4`** via immediate operand `mov r9d, 4` at **VA `0x140886f8d`** (offset `0x88638d`).
- **`dtp_canRecruit`** (VA `0x1420d8e60`, offset `0x20d7060`):
  - Description: `"DefendThePlayer: Allows the player to press E on a Resistance member to recruit them."`
  - Default value registered: `1` via `mov r9d, 1` at **VA `0x140886fca`**.
- **`dtp_joinRange`** (VA `0x1420d8f98`, offset `0x20d7198`):
  - Description: `"DefendThePlayer: Join Range"` (default float: `15.0f`).
- **`dtp_leaveRange`** (VA `0x1420d8f68`, offset `0x20d7168`):
  - Description: `"DefendThePlayer: Leave Range"` (default float: `40.0f`).
- **`dtp_joinLeaveDelay`** (VA `0x1420d8f10`, offset `0x20d7110`):
  - Description: `"DefendThePlayer: Time Between allowing leave and join prompts"` (default float: `2.0f`).

UI Localization keys:
- **`@ui_interaction_recruitResistance`** (VA `0x14201cbe0`, offset `0x201ade0`): Player prompt "Recruit".
- **`@ui_interaction_dismissResistance`** (VA `0x14201cbb8`, offset `0x201adb8`): Player prompt "Dismiss".
- There is **no** "Squad Full" or "Max Capacity" text prompt; when capacity is reached, the game simply suppresses the recruit prompt.

---

#### 2. Decision Logic and Enforcement Checks
An exhaustive assembly scan of the entire `.text` section for references to `[reg + 0x90c]` (`dtp_maxAgents`) revealed exactly three enforcement points:

1. **Check #1: `CanRecruit` (`FUN_1406e5c74`, VA `0x1406e5c74` - `0x1406e5d6c`):**
   - Called by `CPlayerInteractionManager::UpdateInteraction` (**VA `0x1403cae46`**) to decide whether to display `@ui_interaction_recruitResistance`.
   - Disassembly at **VA `0x1406e5ce1`–`0x1406e5cf5`** (file offset `0x6e50e8`–`0x6e50f5`):
     ```assembly
     0x1406e5ce1: 4c 8b 05 18 8e f4 01  mov  r8, qword ptr [rip + 0x1f48e18]  ; gEnv (0x14262eb00)
     0x1406e5ce8: 41 8b 88 0c 09 00 00  mov  ecx, dword ptr [r8 + 0x90c]      ; ecx = dtp_maxAgents
     0x1406e5cef: 39 8f 90 00 00 00     cmp  dword ptr [rdi + 0x90], ecx      ; compare current recruits vs max
     0x1406e5cf5: 0f 83 51 00 00 00     jae  0x1406e5d4c                      ; if current >= max: fail (return 0)
     ```

2. **Check #2: `CanToggleRecruit` (`FUN_1406e5e1c`, VA `0x1406e5e1c` - `0x1406e5f38`):**
   - Validates whether an agent interaction toggle can proceed to recruitment.
   - Disassembly at **VA `0x1406e5ed3`–`0x1406e5ee6`** (file offset `0x6e52d3`–`0x6e52e6`):
     ```assembly
     0x1406e5ed3: 48 8b 0d 26 8c f4 01  mov  rcx, qword ptr [rip + 0x1f48c26]  ; gEnv (0x14262eb00)
     0x1406e5eda: 8b 81 0c 09 00 00     mov  eax, dword ptr [rcx + 0x90c]      ; eax = dtp_maxAgents
     0x1406e5ee0: 39 87 90 00 00 00     cmp  dword ptr [rdi + 0x90], eax      ; compare current recruits vs max
     0x1406e5ee6: 73 d8                 jae  0x1406e5ec0                      ; if current >= max: fail (return 0)
     ```

3. **Check #3: Player DTP Initialization (`FUN_1406fffb4` -> `FUN_1406f07b4`):**
   - Initializes the player's DefendThePlayer controller and passes max agent capacity.
   - Disassembly at **VA `0x1406fffe5`–`0x1406fffec`** (file offset `0x6ff3e5`–`0x6ff3ec`):
     ```assembly
     0x1406fffe5: 48 8b 05 14 eb f2 01  mov  rax, qword ptr [rip + 0x1f2eb14]  ; gEnv (0x14262eb00)
     0x1406fffec: 8b 98 0c 09 00 00     mov  ebx, dword ptr [rax + 0x90c]      ; ebx = dtp_maxAgents
     0x1406ffff5: 8b d3                 mov  edx, ebx                         ; pass maxAgents to 0x1406f07b4
     0x140700009: e9 a6 07 ff ff        jmp  0x1406f07b4                      ; sets player->m_maxRecruitedAgents
     ```

---

#### 3. Data Structure & Memory Topology for Recruited Followers
Decompilation of the recruitment and dismissal routines confirmed:
- **Storage Type:** Follower agents are stored in an **intrusive circular doubly linked list** (`head` at `leader + 0x80`, `tail` at `leader + 0x88`, node links at `agent + 0x18` and `agent + 0x20`).
- **Capacity Constraint:** There is **NO** fixed-size array (e.g. `EntityId followers[4]`). Memory for followers is neither allocated as a fixed array nor hardcoded in struct sizes.
- **Active Counter:** The count of currently recruited agents is maintained at `[leader + 0x90]`:
  - Incremented in `FUN_1405b87b0` at **VA `0x1405b87ba`**: `inc dword ptr [rcx + 0x90]`
  - Decremented in `FUN_1405c5d20` at **VA `0x1405c5d20`**: `dec dword ptr [param_1 + 0x90]`
- **Save / Load Serialization:** Handled in `FUN_140440b74` (`CGameAI::Serialize`). Each follower AI saves its own `leaderId` / `goalId`. Upon reading a save file, each agent independently reattaches to its leader via `FUN_14043d4d0`.

---

#### 4. Hardcoded vs. Config: Summary
- **Hardcoded Default:** The value `4` is hardcoded as an immediate 32-bit constant in instruction `mov r9d, 4` at **VA `0x140886f8d`** (file offset `0x88638d`).
- **Runtime Variable:** At engine startup, this constant is registered into the CVar `dtp_maxAgents` and stored at memory offset `[gEnv + 0x90c]`.
- **Enforcement:** All recruitment check functions read dynamically from `[gEnv + 0x90c]`. No check hardcodes `4`.
- **Configuration:** Because `dtp_maxAgents` is registered without `VF_READONLY` or `VF_CONST_CVAR`, it can accept runtime overrides. However, vanilla game packages and scripts contain no overrides for it, leaving the hardcoded default `4` in full effect.

---

### Phase 2: Mapping All Dependencies on the Follower Count (4 -> 12)

#### 1. Follower Storage & Array Bounds
- **Data Structure:** Followers are stored in a circular intrusive doubly-linked list (`[leader + 0x80]`), not a fixed-size array.
- **Node Allocation:** Nodes are part of each NPC's entity component. No fixed-stride array (such as `EntityId followers[4]`) exists in memory.
- **Count Tracking:** The active follower count is stored as a 32-bit signed integer (`int32_t`) at `[leader + 0x90]`. It can safely accommodate 12 (or higher) without integer overflow.
- **Formation Slot Vector:** Formation positions are stored in a `std::vector<FormationSlot>` at `[leader + 0xc8]`:
  - Dynamically cleared and regenerated in `FUN_1405cf700` / `FUN_1405ca308` via `std::vector::push_back` (`FUN_14080458c`).
  - Spatial positioning query `FUN_1405bb844` includes bounds checking: if `slotIndex >= numSlots`, it safely falls back to `GetEntityPos(leader)` with zero out-of-bounds memory access.

#### 2. Follower Iteration Loops
Exhaustive decompilation of all follower iteration routines showed:
- **Center-of-Mass & Formation Updates (`FUN_1405cfe24`):** Traverses `while (node != head)`. Squad center-of-mass divides sum by active count `*(uint *)(param_1 + 0x90)`.
- **Assignment Buffer Allocation (`FUN_1405cf700`):** Resizes its internal assignment buffer dynamically via `FUN_1405c87e4` to match `current_count`.
- **Follower Release / Cleanup (`FUN_1405b8844`):** Traverses `while (tail != head)` until the linked list is empty.
- **Command Dispatch (`CAICommandFollower::SendCommand`, `FUN_140de8960`):** Traverses dynamic `std::vector` command queues.
- **Conclusion:** Zero loops in the executable are bounded by a hardcoded constant `4`. All loops iterate until list termination.

#### 3. Tethering, Teleportation & Distance Bounds
- **Disengage / Tether Radius:** Governed by `dtp_leaveRange` (`40.0f` at `gEnv + 0x904`).
- **Evaluation:** Distance is calculated independently per follower in `FUN_1405cff38`:
  `FUN_1405bbcf8(leader, agentId, pos, leaveRange * leaveRange)`
  If an individual follower gets separated beyond 40 meters, that specific follower disengages from the squad. Raising the recruit cap to 12 has zero conflict with this per-agent calculation.

#### 4. UI & HUD Elements
- **Multiplayer Co-op UI:** Flash interface elements (`Root.PlayerInfoBar.Info.SquadList.SquadMember%d`, `Squaddie%d`) belong exclusively to the 4-player Co-op lobby (`CFrontEndPlayerInfoBar`).
- **Single-Player Campaign HUD:** Single-player Resistance followers do **not** use a fixed 4-slot HUD portrait widget. Instead, followers are marked in the 3D game world and on the minimap/compass via overhead icons.
- **Icon Rendering (`CHUD::Update`, `0x1403e6778`):** Dynamically iterates all active entities bearing the friendly/squaddie tag. There is no hardcoded 4-icon limit.

#### 5. Save / Load Serialization
- **Serialization Routine (`CGameAI::Serialize`, `FUN_140440b74`):**
  - Follower relationships are serialized **per follower entity**, which stores its assigned leader Entity ID (`goalId`).
  - Upon deserialization (`ser.IsReading()`), each follower looks up its leader and reattaches via `FUN_14043d4d0`.
  - The player entity does not serialize a fixed 4-element array. Raising follower capacity will not break save game format or cause corruption.

#### 6. Summary of Required Modifications for 12 Followers
Because all three engine checks (`CanRecruit`, `CanToggleRecruit`, `SetupPlayerDTP`) read dynamically from `[gEnv + 0x90c]`, modifying the default registration value of `dtp_maxAgents` from `4` to `12` at **VA `0x140886f8d`** (file offset `0x88638d`) cleanly updates all downstream subsystems:
1. `dtp_maxAgents` runtime storage (`gEnv + 0x90c`) initializes to 12.
2. `CanRecruit` allows recruitment while `current < 12`.
3. `CanToggleRecruit` allows recruitment toggle while `current < 12`.
4. `SetupPlayerDTP` passes `12` to player controller (`m_maxRecruitedAgents = 12`).
5. Intrusive circular doubly linked list accommodates 12 nodes without any memory reallocation or struct expansion.

---

### Phase 3: Patch Proposal (4 -> 12 Resistance Recruit Cap)

#### 1. Proposed Binary Patch Diff
Only a single 6-byte instruction patch inside `.text` is required. No struct resizing, code caves, or runtime hooks are needed.

| Parameter | Details |
| :--- | :--- |
| **Target Subsystem** | DefendThePlayer (`dtp_*`) CVar Registration |
| **Function** | `CDefendThePlayerManager::InitConsoleVariables` (`FUN_140886e68`) |
| **Instruction VA** | `0x140886f8d` |
| **File Offset** | `0x88638d` |
| **Original Instruction** | `mov r9d, 4` |
| **Original Machine Code** | `41 b9 04 00 00 00` |
| **New Instruction** | `mov r9d, 12` |
| **New Machine Code** | `41 b9 0c 00 00 00` |
| **Scope & Safety** | Single-player offline only. 0 bytes modified in `.rdata` or `.data`. |

#### 2. Risk Assessment
- **Memory Corruption:** **Zero.** Followers are held in an intrusive circular doubly linked list where node pointers reside inside each agent NPC entity. No fixed-size array exists.
- **Save Incompatibility:** **Zero.** Serialization stores `goalId` (leader entity ID) per follower entity (`CGameAI::Serialize`). The player entity does not save a fixed 4-member list.
- **AI Pool Headroom:** **Safe.** Active AI pool limits were previously increased to 96 (soft) and 150 (hard). 12 followers utilize only ~8–12% of the active budget, leaving ample room for combat encounters.
- **UI Overflow:** **Zero.** Single-player uses dynamic 3D world overhead markers and minimap blips (`CHUD::Update`), not a fixed 4-portrait Flash widget.

#### 3. Verification & Testing Procedure
1. **Sequential Recruitment Test:** Recruit followers 1 through 4, then verify `@ui_interaction_recruitResistance` remains active for members 5 through 12. Confirm prompt disappears once 12 are following.
2. **Dismissal & Replacement Test:** Dismiss 1 follower; confirm prompt reappears on nearby Resistance fighters and allows recruiting back up to 12.
3. **Combat Engagement:** Engage a KPA patrol or strike point with all 12 followers to verify behavior, AI pathfinding, and casualty replenishment.
4. **Save & Reload Persistence:** Save at a safehouse with 12 followers, exit, and reload to confirm all 12 reattach cleanly to the player.

#### 4. Rollback Plan
- Revert file offset `0x88638d` from `41 b9 0c 00 00 00` back to `41 b9 04 00 00 00`.
- Alternatively, restore from backup: `cp ~/rework/Homefront2_Release.exe.vanilla ~/rework/Homefront2_Release.exe`.

#### 5. In-Game Verification Status
- **Status:** **VERIFIED IN-GAME BY USER (100% SUCCESS)**
- **Observations:**
  - Player successfully recruited 12 concurrent Resistance members.
  - Interaction prompt `[E] Recruit` appeared cleanly for all members from 1 up to 12.
  - All 12 recruited followers received active markers in the 3D world and on the minimap/compass.
  - Squad formation and follow behavior functioned without engine crashes or UI degradation.

---

## Squad Formation & Spatial Spread Tuning

### 1. Formation Architecture Analysis
When followers are recruited or dismissed, `FUN_1405cf700` dynamically calculates squad spatial distribution and generates slot coordinates in `FUN_1405ca308`.

For generic follow behavior, `FUN_1405ca308` evaluates concentric rings around the player using:
- Number of concentric rings: `rings = ((numUnits - 1) / 7) + 1` (1 ring for $\le 4$ units, 2 rings for 12 units).
- Formation radius formula:
  $$\text{maxRadius} = \sqrt{\text{numUnits}} \times \text{spacingScalar} + \text{minRadius}$$
- Per-ring radius:
  $$\text{ringRadius} = \text{ringIndex} \times \frac{\text{maxRadius} - \text{minRadius}}{\text{rings} + 1} + \text{minRadius}$$
- Slot coordinates are computed via polynomial $\cos(\theta)$ and $\sin(\theta)$ evaluation and rotated by the player's orientation matrix before being clamped to the navigation mesh in `FUN_1405b8870`.

### 2. Bottlenecks with 12 Followers in Vanilla Spacing
In vanilla:
- `minRadius` = **`2.0f`** (VA `0x14205afa0`): Followers try to stand within 2.0 to 5.4 meters of the player.
- `spacingScalar` = **`3.0f`** (VA `0x14205afa4`): Outermost radius is only $\approx 12.4$ meters.
- **Problem:** When navigating tight interiors, doorways, or narrow streets, 12 followers collapse into a dense cluster around the player, obstructing movement and crowding entrances.

### 3. Native Zero-Data Redirection Patches (Applied)
By redirecting the instruction displacements in `.text` to read existing native float constants in `.rdata` (Zero-Data Modification), squad spacing is expanded with zero side effects:

| Patch # | Parameter | Instruction VA | File Offset | Original Bytes / Assembly | Applied Bytes / Assembly | Value Impact |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| **#11** | `formation_minRadius` | `0x1405caf68` | `0x5ca368` | `f3 44 0f 10 2d 2f 00 a9 01`<br>`movss xmm13, [rip+0x1a9002f]` (`2.0f`) | `f3 44 0f 10 2d 4f 00 a9 01`<br>`movss xmm13, [rip+0x1a9004f]` (**`5.0f`**) | Increases inner buffer distance from 2m to 5m, preventing doorway crowding |
| **#12** | `formation_spacingScalar` | `0x1405cb005` | `0x5ca405` | `f3 44 0f 59 0d 96 ff a8 01`<br>`mulss xmm9, [rip+0x1a8ff96]` (`3.0f`) | `f3 44 0f 59 0d b2 ff a8 01`<br>`mulss xmm9, [rip+0x1a8ffb2]` (**`5.0f`**) | Expands tactical squad perimeter to ~22m so followers spread out in cover |

### 4. Status & In-Game Testing
- **Status:** **APPLIED & DEPLOYED TO STEAM**
  - Applied to working binary: `/home/jackedhawk117/rework/Homefront2_Release.exe`
  - Deployed to Steam directory: `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
  - Binary MD5: `c938b96cfc8c8675443b5393d6912366`
  - Binary SHA256: `7d7aaa42093d04fb104be7f201c1f026e5b67743e1ca424343058d1d59add267`
- **Testing Checklist:**
  1. Recruit up to 12 Resistance fighters.
  2. Walk through standard doors, safehouse exits, and narrow alleyway choke points; verify followers stop ~5m back rather than crowding and trapping the player.
  3. Lead the squad into open streets / combat and verify they fan out broadly (up to ~22m perimeter) and take distinct cover positions.
- **Rollback Instructions (if needed):**
  - Offset `0x5ca368`: byte `4f` $\rightarrow$ `2f` (reverts `minRadius` to 2.0m)
  - Offset `0x5ca405`: byte `b2` $\rightarrow$ `96` (reverts `spacingScalar` to 3.0f)

---

## Travel Formation & Dynamic Collision Avoidance Tuning

### 1. Problem Identification
While Patches #11 and #12 resolved squad dispersion during combat (`PlayerInCombat` is active), followers still bunched up during generic non-combat travel and open-world transit.

Reverse engineering revealed three distinct mechanisms causing non-combat clumping:
1. **Per-Frame Follow Loop Leash Radius (`0x1405c29ff` in `FUN_1405c28b4`):**
   - Non-combat follower positions are calculated frame-by-frame in `FUN_1405c28b4` (`0x1405c2d9f`–`0x1405c2dce`).
   - At `0x1405c29ff`, it loads `movss xmm3, [rip + 0x1a98599]` (`0x14205afa0` = `2.0f`) and invokes `0x1405b72d8` to clamp follower movement destination to a 2.0-meter radius behind the player. All 12 followers converge on the identical 2-meter point behind the player while running.
2. **Dynamic Collision Avoidance Lateral Buffer (`ai_CollisionAvoidanceAgentExtraFat` at `0x140dcbc25`):**
   - CryEngine's collision avoidance solver checks inter-agent distance against `radius + ExtraFat` (`0x1416526cf`, `0x140e56d3c`).
   - Vanilla registers this cvar at `0x140dcbc25` with `0.025f` (2.5 cm buffer).
   - Because 2.5 cm is negligible, followers do not yield lateral space on sidewalks and streets, following in single file or running into each other.
3. **Collision Avoidance Target Cutoff (`ai_CollisionAvoidanceTargetCutoffRange` at `0x140dcbb96`):**
   - In `0x140e58100`–`0x140e5810f`, CryEngine evaluates `distanceSquared < cutoffRangeSquared`. If true, `jb 0x140e58491` skips the entire collision avoidance update function (`call 0x140e56d10`).
   - Vanilla registers this cutoff as `3.0f` (3 meters).
   - When followers get within 3 meters of the player or halt point, collision avoidance shuts down entirely, causing all 12 followers to walk directly into each other.

### 2. Native Zero-Data Redirection Patches (Applied)

| Patch # | Parameter | Instruction VA | File Offset | Original Bytes / Assembly | Applied Bytes / Assembly | Value Impact |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| **#13** | `travel_follow_radius` | `0x1405c29ff` | `0x5c1dff` | `f3 0f 10 1d 99 85 a9 01`<br>`movss xmm3, [rip+0x1a98599]` (`2.0f`) | `f3 0f 10 1d b9 85 a9 01`<br>`movss xmm3, [rip+0x1a985b9]` (**`5.0f`**) | Expands travel follow radius from 2m to 5m, matching combat inner radius |
| **#14** | `ai_CollisionAvoidanceAgentExtraFat` | `0x140dcbc25` | `0xdcb025` | `f3 0f 10 1d 77 c2 1e 01`<br>`movss xmm3, [rip+0x11ec277]` (`0.025f`) | `f3 0f 10 1d 03 2a 1c 01`<br>`movss xmm3, [rip+0x11c2a03]` (**`1.0f`**) | Enforces 1.0m dynamic personal space buffer so agents fan out laterally across paths |
| **#15** | `ai_CollisionAvoidanceTargetCutoffRange` | `0x140dcbb96` | `0xdcaf96` | `f3 0f 10 1d d6 12 22 01`<br>`movss xmm3, [rip+0x12212d6]` (`3.0f`) | `f3 0f 10 1d 52 08 1e 01`<br>`movss xmm3, [rip+0x11e0852]` (**`0.0f`**) | Avoidance never shuts down when approaching player, preventing halt collapse |

### 3. Status & In-Game Testing
- **Status:** **APPLIED & DEPLOYED TO STEAM**
  - Working copy: `/home/jackedhawk117/rework/Homefront2_Release.exe`
  - Steam copy: `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
  - Binary MD5: `3d54b928ac39dd4c73db1561112fda37`
  - Binary SHA256: `74f2cc8ebd5b3b14858812701d125ee1b5e170002aee7ab4220862678158f8b7`
- **Testing Checklist:**
  1. Recruit up to 12 Resistance followers.
  2. Sprint and jog through streets and alleyways outside of combat: verify followers trail at ~5m distance and fan out laterally across the width of the roadway rather than queuing in a single-file line or clipping through each other.
  3. Stop moving abruptly: verify followers maintain their 1.0m personal space bubbles around each other and the player rather than sliding together into a clump.
---

## Phase 5: Squad Combat Behavior, Durability & Urban Navigation Tuning

### 1. Problem Identification & Root Cause Analysis

Following in-game combat testing with a 12-member Resistance squad, three critical issues were identified:
1. **Outpost Doorway Abandonment / Immobility:**
   - When exiting an outpost/safehouse, 7 followers exited but 5 became stuck behind a door/obstacle and remained completely immobile.
   - **Root Cause #1:** Patch #14 set `ai_CollisionAvoidanceAgentExtraFat` to 1.0m. In narrow (1.2m) interior doorways, the 2.6m avoidance bubble made agents treat the doorway as completely blocked, halting movement.
   - **Root Cause #2:** `dtp_leaveRange` default was 100.0m (`0x140886ee9`). When delayed followers fell more than 100m behind the player, `FUN_1405cff38` dismissed them back to neutral civilians (immobile).
2. **Elevated / Rooftop Enemy Targeting Freeze:**
   - In combat against a 3-man KPA squad, followers killed 2 ground enemies, but completely ignored the 3rd KPA firing from an elevated rooftop.
   - **Root Cause #1:** In `CoordinatedCombatTarget::Update` (`0x1405c5275`), line-of-sight loss is checked against a 2.0-second timeout (`[rip + 0x1ee7774] = 2.0f`). If an elevated enemy ducks or steps back for 2 seconds, the target is marked INVALID (`m_isValidTarget = 0`), causing the squad to exit combat and ignore the enemy.
   - **Root Cause #2:** In `htr_CAISystem_InitConsoleVariables` (`0x140dcb7e5`), `ai_InfiniteSightWhenAlerted` defaulted to 0 (`xor r9d, r9d`), enforcing standard vertical pitch/elevation vision cone cutoffs that blinded ground followers to rooftop enemies.
3. **Rapid Squad Casualties (Fodder Health):**
   - Followers died in 2–3 bullets (squad dropped from 12 to 5 fast).
   - **Root Cause:** In `CGameRules::GetDamageMultiplier` (`0x1405d7654`), enemy AI damage against Resistance followers branched to default 1.0f (100% full unmitigated damage). With 100 HP and zero armor/regeneration, followers were wiped out by 35–40 damage assault rifle rounds.

---

### 2. Applied Binary Patches

| Patch # | Parameter | Instruction VA | File Offset | Original Bytes / Assembly | Applied Bytes / Assembly | Gameplay Impact |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| **#14 (Refine)** | `ai_CollisionAvoidanceAgentExtraFat` | `0x140dcbc25` | `0xdcb025` | `f3 0f 10 1d 03 2a 1c 01`<br>`movss xmm3, [rip+0x11c2a03]` (`1.0f`) | `f3 0f 10 1d f9 b4 1d 01`<br>`movss xmm3, [rip+0x11db4f9]` (**`0.25f`**) | Squeezes personal clearance to 25cm so all 12 followers stream through narrow doorways |
| **#16** | `dtp_leaveRange` | `0x140886ee9` | `0x8862e9` | `f3 0f 10 1d 33 11 84 01`<br>`movss xmm3, [rip+0x1841133]` (`100.0f`) | `f3 0f 10 1d 3f 69 83 01`<br>`movss xmm3, [rip+0x183693f]` (**`250.0f`**) | Expands follower leash from 100m to 250m so delayed followers are never auto-dismissed |
| **#17** | `CoordinatedCombatTarget` Timeout | `0x1405c5275` | `0x5c4675` | `0f 2f 05 74 77 ee 01`<br>`comiss xmm0, [rip+0x1ee7774]` (`2.0f`) | `0f 2f 05 78 77 ee 01`<br>`comiss xmm0, [rip+0x1ee7778]` (**`30.0f`**) | Extends target memory from 2s to 30s so squad keeps attacking rooftop enemies who duck |
| **#18** | `ai_InfiniteSightWhenAlerted` | `0x140dcb7e5` | `0xdcabe5` | `45 33 c9 c7 44 24 20 02 00 00 00`<br>`xor r9d, r9d; mov [rsp+0x20], 2` (`0`) | `41 b9 01 00 00 00 c6 44 24 20 02`<br>`mov r9d, 1; mov [rsp+0x20], 2` (**`1`**) | Eliminates pitch/elevation vision cone cutoffs in combat so followers acquire elevated enemies |
| **#19** | Friendly Squad Damage Resistance | `0x1405d76ba` | `0x5d6aba` | `84 c9 74 63 45 84 c0 74 5e ...` (original unmitigated logic) | `38 44 24 28 74 32 f3 0f 10 05 0c 4d 9d 01 c3` + 41 NOPs | Gives Resistance followers 75% damage resistance (4x effective HP, *Freedom Fighters* durability) |

---

### 3. Status & Deployment
- **Status:** **SUPERSEDED BY PHASE 6**
  - Working binary: `/home/jackedhawk117/rework/Homefront2_Release.exe`
  - Steam binary: `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
  - Previous Phase 5 MD5: `bd8e59ab17bf837152d23bea97f84239`

### 4. Rollback Instructions
- Offset `0xdcb025`: `f3 0f 10 1d f9 b4 1d 01` $\rightarrow$ `f3 0f 10 1d 03 2a 1c 01` (reverts ExtraFat to 1.0m)
- Offset `0x8862e9`: `f3 0f 10 1d 3f 69 83 01` $\rightarrow$ `f3 0f 10 1d 33 11 84 01` (reverts leaveRange to 100m)
- Offset `0x5c4675`: `0f 2f 05 78 77 ee 01` $\rightarrow$ `0f 2f 05 74 77 ee 01` (reverts target timeout to 2.0s)
- Offset `0xdcabe5`: `41 b9 01 00 00 00 c6 44 24 20 02` $\rightarrow$ `45 33 c9 c7 44 24 20 02 00 00 00` (reverts infinite sight to 0)
- Offset `0x5d6aba`: revert 56 bytes back to `84 c9 74 63 45 84 c0 74 5e 38 44 24 28 74 29 38 05 f2 1b ea 01 48 8b 0d 3a c5 04 02 0f 95 c0 48 8d 14 40 48 63 41 58 48 03 d0 48 c1 e2 05 f3 0f 10 84 0a 98 00 00 00 c3`

---

## Phase 6: Combat Hesitation Elimination & Resistance Squad Marksmanship (October 22, 2026)

### 1. Problem Analysis & In-Game Verification
- **Issue 1 (2-Second Combat Hesitation Outside Cover):** Both Resistance followers and KPA soldiers outside cover faced each other for ~2 seconds before firing.
  - *Root Cause:* In `CoordinatedCombatGroup`, `cc_isHostileCheckTime` (1.0s window), `cc_reSeeTargetTime` (1.0s line-of-sight acquisition delay), and `cc_checkFrequency` (5.0s state evaluation throttle) delayed target confirmation.
- **Issue 2 (Resistance Squad Weapon Accuracy):** Followers missed too many shots during sustained firefights.
  - *Root Cause:* At `0x140706309` (`0x705709`), the engine checked if the shooter was a companion (`call [rax + 0x240] ; IsCompanion`). If true, `0x1406e6f60` was called to calculate an artificial companion miss dispersion and added to the bullet miss vector (`addss xmm0, [rdi + 8]`), causing companions to intentionally spray around the target.

### 2. Applied Binary Patches

| Patch # | Parameter / Logic | Instruction / Target VA | File Offset | Original Bytes / Assembly | Applied Bytes / Assembly | Gameplay Impact |
| :---: | :--- | :---: | :---: | :--- | :--- | :--- |
| **#20A** | `cc_isHostileCheckTime` | `0x1424aca00` | `0x24aa400` | `00 00 80 3f` (`1.0f`) | `cd cc cc 3d` (**`0.1f`**) | Cuts hostility confirmation delay from 1.0s to 100ms |
| **#20B** | `cc_checkFrequency` | `0x1424aca10` | `0x24aa410` | `00 00 a0 40` (`5.0f`) | `cd cc 4c 3e` (**`0.2f`**) | Increases target state evaluation from once per 5s to 5 times per second (200ms) |
| **#20C** | `cc_reSeeTargetTime` | `0x1424aca20` | `0x24aa420` | `00 00 80 3f` (`1.0f`) | `cd cc cc 3d` (**`0.1f`**) | Cuts exposed re-acquisition delay from 1.0s to 100ms |
| **#21** | Companion Aim Spread Neutralization | `0x140706327` | `0x705727` | `e8 34 0c fe ff f3 0f 58 47 08 f3 0f 11 47 08`<br>`call 0x1406e6f60; addss xmm0, [rdi+8]; movss [rdi+8], xmm0` | `83 67 04 00 83 67 08 00 90 90 90 90 90 90 90`<br>`and dword ptr [rdi+4], 0; and dword ptr [rdi+8], 0; 7 NOPs` | Clears artificial angular pitch & yaw miss offsets for followers; squad shoots true to aim |

### 3. Status & Deployment
- **Status:** **APPLIED & DEPLOYED TO STEAM**
  - Working binary: `/home/jackedhawk117/rework/Homefront2_Release.exe`
  - Steam binary: `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
  - **New Patched MD5:** `96f593ff3c734855066daced924e6521`
  - **New Patched SHA256:** `f9766b5340eb5edf84e3441c6b51be86e2316156db1137d07176a294867d074e`

### 4. Rollback Instructions
- Offset `0x24aa400`: `cd cc cc 3d` $\rightarrow$ `00 00 80 3f` (reverts `cc_isHostileCheckTime` to 1.0s)
- Offset `0x24aa410`: `cd cc 4c 3e` $\rightarrow$ `00 00 a0 40` (reverts `cc_checkFrequency` to 5.0s)
- Offset `0x24aa420`: `cd cc cc 3d` $\rightarrow$ `00 00 80 3f` (reverts `cc_reSeeTargetTime` to 1.0s)
- Offset `0x705727`: `83 67 04 00 83 67 08 00 90 90 90 90 90 90 90` $\rightarrow$ `e8 34 0c fe ff f3 0f 58 47 08 f3 0f 11 47 08` (reverts companion aim spread injection)










---

## Phase 7: Over-The-Shoulder (OTS) Third-Person Camera & Dynamic Aiming System (October 22, 2026)

### 1. Problem Analysis & Gameplay Requirements
1. **Aiming & Laser Pointer Parallax:**
   - In third-person perspective, weapon raycast fired towards the center of the screen, misaligning with the in-game weapon laser pointer.
   - *Requirement:* Aiming Down Sights (ADS / Right-Click) must switch dynamically to the default first-person iron sights / scope view (zero parallax, laser precision), snapping back to OTS 3rd person on release.
2. **Interactive Minigames & Smartphone Hacking:**
   - Hacking doors/drones and smartphone puzzles broke when forced into 3rd person because the phone view was positioned off-camera.
   - *Requirement:* Hacking and interactions must dynamically switch into first person to allow full visibility and functionality of interactive puzzles.
3. **Camera Perspective Calibration (*Gears of War* OTS):**
   - The initial third-person camera was placed too high (looking down at Ethan's scalp) and centered directly behind his spine.
   - *Requirement:* Lower camera elevation to shoulder height and offset laterally over the right shoulder.
4. **Player Model Extra Weapons Cleanup:**
   - Ethan Brady's 3D mesh displayed default multiplayer socket attachments (shotgun on back, pistol on holster) even when not in inventory.
   - *Requirement:* Hide static unowned socket attachments while preserving the active equipped weapon.

### 2. Applied Binary Patches

| Patch # | Parameter / Component | Instruction VA | File Offset | Size | Original Bytes / Assembly | Applied Bytes / Assembly | Gameplay Impact |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **#22A** | ADS/Hack Hook | `0x1406e1e0c` | `0x6e120c` | 24 B | `33 c0 38 81 9c 02 00 00 ...` (vanilla leaf check) | `e9 bf 7c 89 01 90 ...` (`jmp 0x141f79ad0; 19 NOPs`) | Redirects `CPlayer::IsThirdPerson` to dynamic state evaluator |
| **#22B** | ADS/Hack Evaluator Stub | `0x141f79ad0` | `0x1f78ed0` | 48 B | `00` $\times 48$ (zero padding cave in `.text`) | `31 c0 38 81 9c 02 00 00 74 1d 48 8b 81 60 11 00 00 48 85 c0 74 11 48 83 ec 28 48 89 c1 e8 96 a3 76 fe 48 83 c4 28 c3 b8 01 00 00 00 c3 cc cc cc` | Evaluates `0x1406e3e88`: returns 0 (1st person) if zoomed (ADS) or hacking; returns 1 (3rd person) during traversal/hipfire |
| **#23** | `cl_tpvDist` (Camera Distance) | `0x1408a481a` | `0x8a3c1a` | 8 B | `f3 0f 10 1d 86 f3 75 01` (`3.5f`) | `f3 0f 10 1d 0a fb 94 01` (**`1.85f`**) | Tightens camera distance from 3.5m to 1.85m action perspective |
| **#24A** | OTS Camera Hook | `0x14093f469` | `0x93e869` | 16 B | `8b 03 89 07 8b 43 04 89 47 04 8b 43 08 89 47 08` | `e9 92 a6 63 01 90 90 90 90 90 90 90 90 90 90 90` (`jmp 0x141f79b00; 11 NOPs`) | Intercepts view position commit in `CPlayerView::UpdateView` |
| **#24B** | OTS Calibration Stub & Constants | `0x141f79b00` | `0x1f78f00` | 172 B | `00` $\times 172$ (zero padding cave in `.text`) | Full SSE basis-vector calibration stub (`+0.38m` Right-vector offset, `-0.18m` elevation) + float constants (`1.0f`, `0.38f`, `0.18f`) | Positions camera over the right shoulder with Ethan on the left side of the screen across 360° rotation; lowers viewpoint to upper shoulder level |
| **#25** | Holster Attachment Cleanup | `0x1406f5183` | `0x6f4583` | 6 B | `8b fe 40 0f 94 c7` (`mov edi, esi; sete dil`) | `bf 01 00 00 00 90` (`mov edi, 1; nop`) | Forces `IAttachment::HideAttachment(1)` for default body sockets, removing unowned weapons on Ethan's back/hips |

### 3. Status & Deployment
- **Status:** **APPLIED & DEPLOYED TO STEAM**
  - Working binary: `/home/jackedhawk117/rework/Homefront2_Release.exe`
  - Steam binary: `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
  - **New Patched MD5:** `c3402bd8800ec626ee65abc3ae87032c`
  - **New Patched SHA256:** `d970b57684e83bb4446b419783e47fc37a87585625015d25319ea1e60ef10ea5`

---

## Phase 8: F1 Perspective Hotkey Toggle & Right-Click Instant ADS Snap (October 22, 2026)

### 1. Architectural Concept
- Direct hardware input evaluation using `USER32.dll!GetAsyncKeyState` (imported in IAT at `0x141f7e240`).
  1. **F1 Hotkey:** Edge-triggered latch flips `g_thirdPersonEnabled` between 0 and 1. By default, the game starts in 1st person (`0`).
  2. **Right Mouse Button (`VK_RBUTTON` = 0x02):** While in 3rd person, holding Right-Click dynamically snaps to `0` (First Person), allowing `CWeapon` to execute full vanilla iron sights / scope aiming with zero parallax. Releasing RMB instantly snaps back to OTS 3rd person.

---

## Phase 9: Loading Crash Resolution & Thread-Safe Architecture (October 22, 2026)

### 1. Root Cause of Loading Screen Crash
- In Phase 8, mutable state flags (`g_f1WasDown`, `g_thirdPersonEnabled`) were written directly into the code cave at `0x141f79ad0` located inside `.text`.
- `.text` section flags are `0x60000020` (`IMAGE_SCN_MEM_EXECUTE | IMAGE_SCN_MEM_READ`, `Write = False`). Writing to `.text` triggered a hardware MMU `STATUS_ACCESS_VIOLATION` (0xC0000005) during level loading precache.
- Furthermore, calling `GetAsyncKeyState` on worker threads (`<Thread #500>`) caused thread contention under Wine.

### 2. Decoupled Thread-Safe Redesign
1. **Thread-Safe Read-Only State Check (Patch #22A at `0x1406e1e0c`):**
   - Replaces `CPlayer::IsThirdPerson()` in-place (24 bytes).
   - If AI or remote entity (`[rcx + 0x29c] == 0`), returns `1` immediately.
   - If local player, loads `g_isCurrentlyThirdPerson` from `.data` (`0x1425b1d02`) into `eax`.
   - 100% read-only, 0 writes, 0 API calls, completely safe across all threads.
2. **Main-Thread Frame Tick Hook (Patch #22B at `0x14093f357`):**
   - Hooks camera update inside `CPlayerView::UpdateView()`, which executes strictly once per frame on the main GUI thread when playing in-game (never during level load).
3. **Input Poll & Perspective Evaluator Stub (Patch #22C at `0x141f79ad0`):**
   - Polls `VK_F1` with edge detection and updates `g_thirdPersonEnabled` in `.data` (`0x1425b1d00`).
   - Polls `VK_RBUTTON` (RMB) when 3P is active; holding RMB sets `g_isCurrentlyThirdPerson = 0` (instant 1P ADS snap).
   - All state flags reside in `.data` (`0xc0000040`, `PAGE_READWRITE`).
   - Adheres 100% to the Zero-Data Modification Principle (memory is zero-initialized on disk).

### 3. Applied Binary Patches

| Patch # | Parameter / Component | Instruction VA | File Offset | Size | Original Bytes / Assembly | Applied Bytes / Assembly | Gameplay Impact |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **#22A** | `ThirdPerson_ReadonlyState_Check` | `0x1406e1e0c` | `0x6e120c` | 24 B | `33c038819c02000074083881bd0100007405b801000000c3` | `b80100000080b99c0200000074090fb605e1feec019090c3` | Thread-safe read-only `IsThirdPerson`: AI returns 1, local player reads `.data` |
| **#22B** | `ThirdPerson_ViewUpdate_Hook` | `0x14093f357` | `0x93e757` | 9 B | `488b02ff9028020000` | `e874a7630190909090` | Hooks `CPlayerView::UpdateView` to poll input once per frame on main thread |
| **#22C** | `ThirdPerson_Input_Poll_Stub` | `0x141f79ad0` | `0x1f78ed0` | 128 B | `00` $\times 128$ | `4883ec28b970000000ff1561470000...` | F1 toggles 1P/3P (1P default); holding RMB switches to 1P iron sights/scopes; writes flags to `.data` |
| **#23** | `cl_tpvDist` | `0x1408a481a` | `0x8a3c1a` | 8 B | `f30f101d86f37501` | `f30f101d0afb9401` | Tightens camera distance from 3.5m to 1.85m |
| **#24A** | `ThirdPerson_CameraOTS_Hook` | `0x14093f469` | `0x93e869` | 16 B | `8b0389078b430489...` | `e9e2a6630190...` | Intercepts view commit in `CPlayerView::UpdateView` |
| **#24B** | `ThirdPerson_CameraOTS_Stub` | `0x141f79b50` | `0x1f78f50` | 164 B | `00` $\times 164$ | `f30f104308f3...` | Applies $+0.38\text{m}$ Right-vector offset and $-0.18\text{m}$ elevation |
| **#25** | `ThirdPerson_HolsterCleanup` | `0x1406f5183` | `0x6f4583` | 6 B | `8bfe400f94c7` | `bf0100000090` | Hides unowned socket weapons on Ethan's mesh |

### 4. Status & Deployment
- **Status:** **APPLIED & DEPLOYED TO STEAM**
  - Working binary: `/home/jackedhawk117/rework/Homefront2_Release.exe`
  - Steam binary: `/home/jackedhawk117/.steam/steam/steamapps/common/Homefront_The_Revolution/Bin64/Homefront2_Release.exe`
  - **New Patched MD5:** `877fec6416a93a007693d4e79384c883`
  - **New Patched SHA256:** `ee957425fd57414ebb92af6ae1b07e4893dc4fe9d99315e18d7fbed667a31e9f`
