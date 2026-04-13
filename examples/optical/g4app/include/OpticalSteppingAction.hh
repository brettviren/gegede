// OpticalSteppingAction.hh
//
// Detects optical photons that trigger G4OpBoundaryProcess::Detection
// when they reach a PMT surface.  This is the canonical Geant4 approach
// (used in the OpNovice2 example): because a dielectric_metal SkinSurface
// kills the photon AT the boundary step (PreStepPoint still in water), the
// SD on pmt_vol never fires — only a SteppingAction sees the event at the
// right moment.
#pragma once

#include "G4UserSteppingAction.hh"

class G4OpBoundaryProcess;
class OpticalRunAction;
class G4Step;

class OpticalSteppingAction : public G4UserSteppingAction
{
public:
    OpticalSteppingAction();
    ~OpticalSteppingAction() override = default;

    void UserSteppingAction(const G4Step*) override;

private:
    OpticalRunAction*    fRunAction    = nullptr;
    G4OpBoundaryProcess* fBoundaryProc = nullptr;
    int                  fCachedEvtID  = -1;
    int                  fHitID        = 0;

    OpticalRunAction*    getRunAction();
    G4OpBoundaryProcess* findBoundaryProcess();
};
