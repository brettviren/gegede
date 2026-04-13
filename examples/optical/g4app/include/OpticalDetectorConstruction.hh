// OpticalDetectorConstruction.hh
//
// Reads the GDML geometry and wires up the PMT sensitive detector.
//
// The G4GDMLParser member (fParser) MUST remain alive past Construct()
// because ConstructSDandField() queries GetVolumeAuxiliaryInformation()
// to find volumes tagged with auxtype="SensDet".  This is the same
// lifetime pattern used in the official Geant4 persistency/gdml/G01 example.
#pragma once

#include "G4VUserDetectorConstruction.hh"
#include "G4GDMLParser.hh"
#include <string>

class G4VPhysicalVolume;

class OpticalDetectorConstruction : public G4VUserDetectorConstruction
{
public:
    explicit OpticalDetectorConstruction(std::string gdmlPath);
    ~OpticalDetectorConstruction() override = default;

    G4VPhysicalVolume* Construct()          override;
    void               ConstructSDandField() override;

private:
    std::string    fGDMLPath;
    G4GDMLParser   fParser;   // must outlive Construct()

    // Print the volume tree / material / surface inspector banner.
    void printInspection(const G4VPhysicalVolume* world) const;
};
