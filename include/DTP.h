#pragma once
#include <cstdint>

/**
 * @file DTP.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution DefendThePlayer (DTP) Subsystem
 * 
 * Reconstructed from Homefront2_Release.exe via Ghidra / REA.
 * DefendThePlayer manages dynamic squad recruitment, follower tracking,
 * tether leashes, and formation geometry for player companions.
 */

namespace CryEngine {
namespace DTP {

// Forward Declarations
struct SFormationSlot;
class CDefendThePlayerManager;

/**
 * @brief Circular Intrusive Doubly-Linked List Node
 * 
 * Resides inside each NPC entity component at offset +0x18 / +0x20.
 * Allows infinite dynamic scaling without fixed array limits.
 */
struct FollowerNode {
    FollowerNode* pNext;     // +0x00: Pointer to next follower in circular list
    FollowerNode* pPrev;     // +0x08: Pointer to previous follower in circular list
    uint32_t      entityId;  // +0x10: CryEngine Entity ID of the recruited follower
    uint32_t      padding;
};

/**
 * @brief Player Squad Leader Controller
 * 
 * Allocated per player instance to manage active follower capacity and formation.
 */
struct SPlayerDTPLeader {
    void*         vtable;                       // +0x00: Virtual function table
    uint8_t       pad_08[0x78];                 // +0x08 - +0x7F
    FollowerNode* pFollowersHead;               // +0x80: Head of circular doubly-linked follower list
    FollowerNode* pFollowersTail;               // +0x88: Tail of circular doubly-linked follower list
    int32_t       m_currentRecruitedAgents;     // +0x90: Active recruited squad counter (incremented in 0x1405b87ba)
    int32_t       m_maxRecruitedAgents;         // +0x94: Maximum allowed agents (set from dtp_maxAgents)
    uint8_t       pad_98[0x30];                 // +0x98 - +0xC7
    void*         pFormationSlotsVector;        // +0xC8: std::vector<SFormationSlot>
};

/**
 * @brief Formation Slot Definition
 */
struct SFormationSlot {
    float x;           // +0x00: Local X offset relative to leader
    float y;           // +0x04: Local Y offset relative to leader
    float z;           // +0x08: Local Z offset relative to leader
    uint32_t slotId;   // +0x0C: Unique formation slot index
    bool isOccupied;   // +0x10: Slot assignment status
};

/**
 * @brief DefendThePlayer Global Configuration CVars (Stored in gEnv + 0x90c)
 */
struct SDTPCVars {
    float   dtp_leaveRange;        // +0x00 (gEnv + 0x904): Distance before companion disengages (Vanilla: 40.0m / Patched: 250.0m)
    float   dtp_joinRange;         // +0x04 (gEnv + 0x908): Distance within which recruit prompt is active (15.0m)
    int32_t dtp_maxAgents;         // +0x08 (gEnv + 0x90c): Maximum recruit capacity (Vanilla: 4 / Patched: 12)
    int32_t dtp_canRecruit;        // +0x0C (gEnv + 0x910): Master toggle for recruitment prompt [E] (1)
    float   dtp_joinLeaveDelay;    // +0x10 (gEnv + 0x914): Cooldown between recruit/dismiss interactions (2.0s)
};

/**
 * @brief Concentric Formation Ring Geometry Calculation
 * 
 * Reconstructed from FUN_1405ca308 (0x1405ca308 - 0x1405cb120):
 * Evaluates tactical cover positions around the squad leader.
 * 
 * @param numUnits Current recruited squad size (e.g. 12)
 * @param minRadius Inner perimeter buffer (Vanilla: 2.0m / Patched: 5.0m)
 * @param spacingScalar Spatial dispersion multiplier (Vanilla: 3.0m / Patched: 5.0m)
 */
inline float CalculateMaxFormationRadius(int numUnits, float minRadius, float spacingScalar) {
    // Formula at 0x1405caf68 - 0x1405cb005
    return (float)__builtin_sqrtf((float)numUnits) * spacingScalar + minRadius;
}

} // namespace DTP
} // namespace CryEngine
