#pragma once
#include <cstdint>

/**
 * @file VisionMap.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution VisionMap & AI Perception
 * 
 * Reconstructed from Homefront2_Release.exe via Ghidra / REA.
 * Evaluates line-of-sight checks, vertical elevation sight cones, and perception limits.
 */

namespace CryEngine {
namespace AI {

/**
 * @brief AI Perception Configuration Parameters (0x140e62be6)
 */
struct SPerceptionParams {
    float   fov;                    // +0x00: Field of view in degrees
    float   sightRange;             // +0x04: Maximum line-of-sight distance
    float   sightRangeDarkness;     // +0x08: Sight range under nighttime / unlit conditions
    uint8_t pad_0C[0x268];          // +0x0C - +0x273
    float   reactionTime;           // +0x274: Base perception reaction time constant
    float   visualPerceptionScale;  // +0x278: Visual perception multiplier
    float   audioPerceptionScale;   // +0x27C: Acoustic perception multiplier
};

/**
 * @brief Perception System Console Variables
 */
struct SPerceptionCVars {
    // When enabled (1), removes artificial pitch/elevation vision cutoffs when alerted
    // Vanilla: 0 (ground followers were blind to enemies on elevated rooftops)
    // Patched: 1 (ground followers immediately acquire and return fire on elevated targets)
    int32_t ai_InfiniteSightWhenAlerted; // +0x00 (0x140dcb7e5)
};

} // namespace AI
} // namespace CryEngine
