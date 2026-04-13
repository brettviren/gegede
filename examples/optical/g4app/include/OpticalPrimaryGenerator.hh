// OpticalPrimaryGenerator.hh
//
// Thin wrapper around G4GeneralParticleSource.
// The beam is entirely configured by the Geant4 macro; no hard-coded values.
#pragma once

#include "G4VUserPrimaryGeneratorAction.hh"
#include <memory>

class G4GeneralParticleSource;
class G4Event;

class OpticalPrimaryGenerator : public G4VUserPrimaryGeneratorAction
{
public:
    OpticalPrimaryGenerator();
    ~OpticalPrimaryGenerator() override = default;

    void GeneratePrimaries(G4Event* event) override;

private:
    std::unique_ptr<G4GeneralParticleSource> fGPS;
};
