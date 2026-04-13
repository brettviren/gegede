// OpticalPrimaryGenerator.cc
#include "OpticalPrimaryGenerator.hh"
#include "G4GeneralParticleSource.hh"
#include "G4Event.hh"

OpticalPrimaryGenerator::OpticalPrimaryGenerator()
    : fGPS(std::make_unique<G4GeneralParticleSource>())
{}

void OpticalPrimaryGenerator::GeneratePrimaries(G4Event* event)
{
    fGPS->GeneratePrimaryVertex(event);
}
