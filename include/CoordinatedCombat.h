#pragma once
#include <cstdint>

/**
 * @file CoordinatedCombat.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution Coordinated Combat Group
 * 
 * Reconstructed from Homefront2_Release.exe via Ghidra / REA.
 * Manages squad coordination, target threat matrices, line-of-sight tracking,
 * and state evaluation timers across AI fireteams.
 */

namespace CryEngine {
namespace AI {

/**
 * @brief Coordinated Combat Global Parameters & CVars
 * 
 * Located at memory address VA 0x1424ac9f0 (File Offset 0x24aa3f0).
 * Initialized in CoordinatedCombatGroup::InitConsoleVariables at 0x1405b54ac.
 */
struct SCoordinatedCombatCVars {
    float cc_lostTargetTime;                    // +0x00 (0x1424ac9f0): Sight loss timeout before status warning (2.0s)
    float cc_abandonTargetTime;                 // +0x04 (0x1424ac9f4): Timeout before abandoning target (Vanilla: 2.0s / Patched: 30.0s)
    float cc_forgetTargetTime;                  // +0x08 (0x1424ac9f8): Hard forget timer for target history (60.0s)
    float cc_proxyUpdateDistanceSquared;        // +0x0C (0x1424ac9fc): Distance squared for proxy position updates (16.0f = 4.0m)
    float cc_isHostileCheckTime;                // +0x10 (0x1424aca00): Hostility verification window (Vanilla: 1.0s / Patched: 0.1s)
    float cc_blinkTime;                         // +0x14 (0x1424aca04): Micro-glance delay (1.0s)
    float cc_damageThreshold;                   // +0x18 (0x1424aca08): Damage sustained before forcing state re-evaluation (2.5f)
    float cc_moveThreshold;                     // +0x1C (0x1424aca0c): Target movement distance before position refresh (2.5m)
    float cc_checkFrequency;                    // +0x20 (0x1424aca10): Target state evaluation interval (Vanilla: 5.0s / Patched: 0.2s)
    float cc_mustEngageIfWithinDistance;        // +0x24 (0x1424aca14): Forced engagement range without line-of-sight (20.0m)
    float cc_mustEngageIfWithinWithLosDistance;  // +0x28 (0x1424aca18): Forced engagement range with line-of-sight (40.0m)
    float cc_combatExitTime;                    // +0x2C (0x1424aca1c): Timeout before exiting combat stance (10.0s)
    float cc_reSeeTargetTime;                   // +0x30 (0x1424aca20): Target re-acquisition verification lag (Vanilla: 1.0s / Patched: 0.1s)
    float cc_awareOfPlayerRzRadarTime;          // +0x34 (0x1424aca24): Radar awareness time constant (5.85s)
    float cc_underFireSustain;                  // +0x38 (0x1424aca28): Duration under-fire state is maintained (5.0s)
    float cc_underFireDecayRate;                // +0x3C (0x1424aca2c): Rate at which under-fire level decays per second (0.2s^-1)
};

/**
 * @brief Coordinated Combat Target Representation
 * 
 * Allocated per active target tracked by the squad (0x1405c5250).
 */
struct SCoordinatedCombatTarget {
    void*     vtable;                   // +0x00: Virtual function table
    uint32_t  targetEntityId;           // +0x08: Target CryEngine Entity ID
    uint8_t   pad_0C[0x14];             // +0x0C - +0x1F
    int64_t   lastSpottedTimestamp;     // +0x20: Tick count when target was last visible
    uint8_t   pad_28[0x20];             // +0x28 - +0x47
    int64_t   sightLostTimestamp;       // +0x48: Tick count when line-of-sight was lost
    uint8_t   pad_50[0x10];             // +0x50 - +0x5F
    float     targetWorldPos[3];        // +0x60: Target last known X, Y, Z world coordinates
    uint8_t   pad_6C[0x30];             // +0x6C - +0x9B
    uint16_t  targetStateFlags;         // +0x9C: Bitfield tracking active engagement status
    uint8_t   pad_9E[0x02];             // +0x9E - +0x9F
    uint8_t   m_isEngaged;              // +0xA0: 1 if currently engaged by squad, 0 otherwise
    uint8_t   pad_A1[0x07];             // +0xA1 - +0xA7
    int64_t   lastStateCheckTimestamp;  // +0xA8: Tick count of last cc_checkFrequency evaluation
    uint8_t   pad_B0[0x20];             // +0xB0 - +0xCF
    uint8_t   m_isHostile;              // +0xD0: 1 if verified hostile
    uint8_t   pad_D1[0x04];             // +0xD1 - +0xD4
    uint8_t   m_hasValidTarget;         // +0xD5: 1 if target is valid, 0 if abandoned
};

/**
 * @brief Weapon Dispersion Vector (Returned by 0x140706140)
 */
struct SAimDispersion {
    float rollError;                    // +0x00: Roll angular dispersion (0.0)
    float pitchError;                   // +0x04: Pitch angular dispersion offset (up/down)
    float yawError;                     // +0x08: Yaw angular dispersion offset (left/right)
};

} // namespace AI
} // namespace CryEngine
