// OpticalPhysicsList.cc
#include "OpticalPhysicsList.hh"
#include "G4EmStandardPhysics.hh"
#include "G4OpticalPhysics.hh"

OpticalPhysicsList::OpticalPhysicsList()
    : G4VModularPhysicsList()
{
    SetVerboseLevel(0);
    RegisterPhysics(new G4EmStandardPhysics);
    RegisterPhysics(new G4OpticalPhysics);
}
