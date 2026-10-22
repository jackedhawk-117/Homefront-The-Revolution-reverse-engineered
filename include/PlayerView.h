#pragma once
#include <cstdint>

/**
 * @file PlayerView.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution Player View & Camera Processing
 * 
 * Reconstructed from Homefront2_Release.exe via Ghidra / REA.
 * Contains SPlayerStats::isThirdPerson, CActor::SetThirdPerson, and SViewParams.
 */

namespace CryEngine {

struct SViewParams {
    float   position[3];            // +0x00: Camera world position (X, Y, Z)
    float   rotation[4];            // +0x0C: Camera orientation quaternion (x, y, z, w)
    float   fov;                    // +0x1C: Field of view (radians)
    float   nearClip;               // +0x20: Near clipping plane
    float   blendPosSpeed;          // +0x24: Position blending smoothing factor
    float   blendRotSpeed;          // +0x28: Rotation blending smoothing factor
    uint8_t viewFlags;              // +0x2C: View processing flags
};

/**
 * @brief Player Runtime Stats Structure (0x14019b4a0)
 */
struct SPlayerStats {
    uint8_t pad_00[0x15D];          // +0x000 - +0x15C
    uint8_t isThirdPerson;          // +0x15D: 1 if third-person camera is active, 0 for first-person
    uint8_t pad_15E[0x03];          // +0x15E - +0x160
    uint8_t bNoGasReaction;         // +0x161
    uint8_t bNoGasDamage;           // +0x162
};

/**
 * @brief CActor Third-Person Interface (0x140dc9c00)
 * 
 * Invoked by action mapping or vehicle transition:
 * @param mode 1 = Activate Third Person, 2 = Deactivate (First Person)
 */
typedef void (*PFN_SetThirdPerson)(void* pActor, int32_t mode);

} // namespace CryEngine
