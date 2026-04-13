// OpticalEventAction.hh
//
// At end-of-event: writes optional trajectory points to CSV via
// OpticalRunAction.  PMT hit recording is handled by OpticalSteppingAction.
#pragma once

#include "G4UserEventAction.hh"

class G4Event;
class OpticalRunAction;

class OpticalEventAction : public G4UserEventAction
{
public:
    OpticalEventAction();
    ~OpticalEventAction() override = default;

    void BeginOfEventAction(const G4Event*) override {}
    void EndOfEventAction  (const G4Event* event) override;

private:
    OpticalRunAction* fRunAction = nullptr;   // resolved lazily on first event

    OpticalRunAction* getRunAction();
};
