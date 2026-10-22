# Third-Person Over-the-Shoulder (OTS) Camera Feasibility Study

## Target Vision
Transform *Homefront: The Revolution* from a pure first-person shooter into an over-the-shoulder tactical squad shooter inspired by *Gears of War* and *Freedom Fighters* (2003).

---

## 1. Engine Infrastructure Findings

Reverse engineering of `Homefront2_Release.exe` confirmed that CryEngine 3.8 natively incorporates comprehensive third-person systems:

1. **Player Third-Person State (`0x141fc4398`):**
   - `SPlayerStats::isThirdPerson` exists at offset `+0x15D` in the player runtime statistics structure.
   - Initialized and serialized as a native engine property.
2. **Actor View Mode API (`0x140dc9c00`):**
   - `CActor::SetThirdPerson(int mode)` is compiled into the executable:
     - `mode = 1`: Enables third-person mode (`m_isThirdPerson = 1`).
     - `mode = 2`: Reverts to first-person mode (`m_isThirdPerson = 0`).
3. **ActionMap Binding (`0x141c05375`):**
   - `ActionThirdPerson` is a native action registered in CryEngine's `IPlayerInput` action table (Action ID at `0x143c9ede8`).
4. **Third-Person Console Variables in `SCVars` (`0x1408a4833`):**
   - `cl_tpvDist` (default `3.5f` meters, stored at `[rsi + 0x08]`).
   - `cl_tpvYaw` (default `0.0f` degrees, stored at `[rsi + 0x0C]`).
5. **Assets & Animation Rigging:**
   - Resistance Mode (4-player co-op multiplayer) utilizes complete third-person models for other players.
   - Ethan Brady's full 3D body mesh, clothing, gear, weapon holsters, and animations are already present in game archives (`animations.pak`, `gamehf2/content`).
   - Full animation sets exist for third-person sprint, slide, crouch, vault, ladder climbing, and cover maneuvers.
   - `AimIK` (aim inverse kinematics) and `LookIK` (head tracking) rigs are fully compiled into the engine.

---

## 2. Technical Comparison: Vanilla vs. Gears of War OTS

| Parameter | CryEngine Default 3P | *Gears of War* Style OTS | Purpose |
| :--- | :--- | :--- | :--- |
| **Camera Distance ($Y$)** | `3.5m` behind | `1.85m` behind | Keeps the player character prominent without obstructing forward view |
| **Lateral Offset ($X$)** | `0.0m` (centered) | `+0.42m` (over right shoulder) | Unblocks crosshair view past Ethan Brady's head/torso |
| **Height Offset ($Z$)** | Pelvis/Root height | `+0.12m` above shoulder | Aligns camera eye-level with head/neck bone |
| **Model Visibility** | `eDrawFilter_ShadowsOnly` (FP) | `eDrawFilter_All` / `CS_FLAG_DRAW_MODEL` | Unhides 3D player body mesh; hides detached 1P arms |
| **Crosshair Alignment** | Gun muzzle center | Screen center $\to$ World ray | `AimIK` rotates torso/arms so gun barrel points at target ray |

---

## 3. Implementation Phases & Roadmap

### Phase A: View Mode Activation (Proof of Concept)
1. Hook `CPlayer::UpdateView` or enable `m_isThirdPerson = 1` permanently upon level spawn.
2. Unhide the third-person character body mesh by updating the draw filter flags from `eDrawFilter_ShadowsOnly` to `eDrawFilter_All`.
3. Hide the floating first-person arm mesh (`VIEW_FIRST_PERSON`).

### Phase B: Over-the-Shoulder Position Calibration
1. Override `cl_tpvDist` to `1.85f`.
2. Apply lateral displacement matrix (`+0.42m` on local $X$, `+0.12m` on local $Z$).
3. Maintain CryEngine's native camera raycast occlusion check (`pPhysicalWorld->RayWorldIntersection`) to prevent wall and geometry clipping.

### Phase C: Aiming & Weapon Parallax Compensation
1. When player presses Aim-Down-Sights (ADS):
   - Smoothly interpolate camera from standard OTS position to tight over-shoulder zoom ($Y = 1.35\text{m}$, $X = +0.35\text{m}$, $\text{FOV} = 55^\circ$).
2. Crosshair raycast: trace camera forward ray $\to$ impact point $\to$ feed coordinates to `AimIK` solver.
