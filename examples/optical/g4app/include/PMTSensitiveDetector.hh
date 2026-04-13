// PMTSensitiveDetector.hh — records optical photons that pass the QE cut.
//
// A photon is "detected" when G4OpBoundaryProcess leaves status Detection
// after the boundary step (i.e. it was absorbed by the photocathode AND
// passed the EFFICIENCY probability roll).
#pragma once

#include "PMTHit.hh"

#include "G4VSensitiveDetector.hh"

class G4Step;
class G4HCofThisEvent;
class G4TouchableHistory;
class G4OpBoundaryProcess;

class PMTSensitiveDetector : public G4VSensitiveDetector
{
public:
    explicit PMTSensitiveDetector(const G4String& name);
    ~PMTSensitiveDetector() override = default;

    void Initialize(G4HCofThisEvent* hce) override;
    G4bool ProcessHits(G4Step* step, G4TouchableHistory*) override;

private:
    PMTHitsCollection*   fHitsCollection = nullptr;
    G4int                fHCID           = -1;
    // Cached pointer to the OpBoundary process — located once, then reused.
    G4OpBoundaryProcess* fBoundaryProc   = nullptr;

    // Walk the optical-photon process list and return the OpBoundary process.
    static G4OpBoundaryProcess* FindBoundaryProcess();
};
