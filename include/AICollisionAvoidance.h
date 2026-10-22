#pragma once
#include <cstdint>

/**
 * @file AICollisionAvoidance.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution AI Collision Avoidance Solver
 * 
 * Reconstructed from Homefront2_Release.exe via Ghidra / REA.
 * Evaluates inter-agent steering, dynamic avoidance forces, and personal space bubbles.
 */

namespace CryEngine {
namespace AI {

/**
 * @brief Collision Avoidance Console Variables
 * 
 * Registered in CAISystem::InitConsoleVariables at 0x140dcbb90 - 0x140dcbc50.
 */
struct SCollisionAvoidanceCVars {
    // Cutoff distance squared under which avoidance solver shuts down
    // Vanilla: 3.0m (causes squad members to collapse into each other near the player)
    // Patched: 0.0m (solver stays active at all ranges)
    float ai_CollisionAvoidanceTargetCutoffRange; // +0x00 (0x140dcbb96)

    // Additional clearance radius added to agent physical cylinder
    // Vanilla: 0.025m (2.5 cm - followers collide on sidewalks and narrow streets)
    // Attempted: 1.0m (100 cm - created a 2.6m bubble that blocked narrow 1.2m outpost doors)
    // Patched: 0.25m (25 cm - perfect sweet spot: smooth door streaming + natural street fanning)
    float ai_CollisionAvoidanceAgentExtraFat;     // +0x04 (0x140dcbc25)

    // Range within which avoidance checks evaluate non-environmental obstacles
    float ai_CollisionAvoidanceRange;            // +0x08
};

/**
 * @brief Collision Avoidance Agent Representation (0x1416526cf, 0x140e56d3c)
 */
struct SAIAvoidanceAgent {
    float       currentPos[3];      // +0x00: Agent world position
    float       velocity[3];        // +0x0C: Agent current velocity vector
    float       radius;             // +0x18: Agent physical collision radius (typically ~0.4m)
    float       effectiveRadius;    // +0x1C: radius + ai_CollisionAvoidanceAgentExtraFat
    uint32_t    entityId;           // +0x20: CryEngine Entity ID
};

} // namespace AI
} // namespace CryEngine
