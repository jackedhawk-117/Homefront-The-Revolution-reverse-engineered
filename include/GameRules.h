#pragma once
#include <cstdint>

/**
 * @file GameRules.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution Damage Multiplier Pipeline
 * 
 * Reconstructed from Homefront2_Release.exe at VA 0x1405d7654 (File Offset 0x5d6a54).
 * Handles cross-faction damage arbitration, friendly fire filtering, and companion scaling.
 */

namespace CryEngine {
namespace GameRules {

enum class EHitType : uint32_t {
    Bullet      = 0,
    Explosive   = 1,
    Melee       = 2,
    Fire        = 3,
    Vehicle     = 4,
    Fall        = 5,
};

enum class EFaction : uint32_t {
    Player      = 0,
    Resistance  = 1,
    KPA         = 2,
    Civilian    = 3,
    Wildlife    = 4,
};

/**
 * @brief Hit Information Structure passed to CGameRules::GetDamageMultiplier
 */
struct HitInfo {
    uint32_t    targetEntityId;     // +0x00: Entity ID receiving damage
    uint32_t    shooterEntityId;    // +0x04: Entity ID delivering damage
    uint32_t    weaponEntityId;     // +0x08: Weapon entity used
    float       damage;             // +0x0C: Raw base damage value
    float       impactDistance;     // +0x10: Distance between shooter and target
    uint32_t    hitType;            // +0x14: EHitType enum
    uint32_t    materialId;         // +0x18: Surface material index
    int32_t     hitPartId;          // +0x1C: Body part hit (head, torso, limbs)
    uint8_t     pad_20[0x08];       // +0x20 - +0x27
    uint8_t     isTargetCompanion;  // +0x28: 1 if target is a recruited Resistance companion
};

/**
 * @brief Damage Multiplier Evaluation (0x1405d7654)
 * 
 * Evaluates faction-versus-faction damage matrices.
 * 
 * Vanilla Behavior:
 * - If target is companion (hitInfo.isTargetCompanion == 1):
 *   Falls through to standard 1.0f (100% full damage), causing followers
 *   to die in 2–3 assault rifle bullets.
 * 
 * Patched Behavior (Patch #19):
 * - Intercepts check at 0x1405d76ba (offset 0x5d6aba):
 *   ```assembly
 *   cmp byte ptr [rsp + 0x28], 0  ; Is target a recruited companion?
 *   je standard_calculation       ; If not, evaluate normal multiplier
 *   movss xmm0, [0x141fac3d4]     ; Load native 0.25f constant
 *   ret                           ; Return 25% damage (75% mitigation / 4x HP)
 *   ```
 */
inline float GetCompanionDamageMultiplier(const HitInfo& hit) {
    if (hit.isTargetCompanion) {
        return 0.25f; // Freedom Fighters-style durability: surviving 12-15 rounds
    }
    return 1.0f;
}

} // namespace GameRules
} // namespace CryEngine
