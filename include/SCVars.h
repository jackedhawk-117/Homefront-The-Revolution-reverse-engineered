#pragma once
#include <cstdint>

/**
 * @file SCVars.h
 * @brief Reconstructed CryEngine 3.8 / Homefront: The Revolution Engine & Game Console Variables
 * 
 * Reconstructed from Homefront2_Release.exe at SCVars::InitCVars (0x1408a4750 - 0x1408a5d00).
 */

namespace CryEngine {

struct SCVars {
    void*   vtable;                                     // +0x00
    int32_t cl_thirdPersonVehicles;                     // +0x04
    float   cl_tpvDist;                                 // +0x08 (0x1408a4833): Third-person camera distance (Default: 3.5m)
    float   cl_tpvYaw;                                  // +0x0C (0x1408a4871): Third-person camera yaw angle offset (Default: 0.0)
    float   cl_sensitivity;                             // +0x10
    uint8_t pad_14[0x80];                               // +0x14 - +0x93
    float   pl_cameraOffsetStandFirstPerson;            // +0x94 (0x1408a570f): Standing camera offset from head bone
    float   pl_cameraOffsetCrouchFirstPerson;           // +0x98 (0x1408a5759): Crouching camera offset from head bone
    float   pl_cameraOffsetProneFirstPerson;            // +0x9C: Prone camera offset from head bone
    uint8_t pad_A0[0x10];                               // +0xA0 - +0xAF
    float   pl_cameraTransitionTime;                    // +0xB0: Camera stance transition smoothing duration
};

} // namespace CryEngine
