// OpticalPhysicsList.hh
//
// Minimal physics list for optical-photon-only simulation.
// Registers only G4EmStandardPhysics (needed for particle definitions and
// basic EM) and G4OpticalPhysics (OpAbsorption, OpBoundary, etc.).
//
// Avoids loading the hadronic physics tables from FTFP_BERT, which makes
// startup > 2 minutes when those processes are never used by optical photons.
#pragma once

#include "G4VModularPhysicsList.hh"

class OpticalPhysicsList : public G4VModularPhysicsList
{
public:
    OpticalPhysicsList();
    ~OpticalPhysicsList() override = default;
};
