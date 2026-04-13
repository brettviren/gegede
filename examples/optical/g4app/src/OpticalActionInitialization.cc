// OpticalActionInitialization.cc
#include "OpticalActionInitialization.hh"
#include "OpticalPrimaryGenerator.hh"
#include "OpticalRunAction.hh"
#include "OpticalEventAction.hh"
#include "OpticalSteppingAction.hh"

void OpticalActionInitialization::Build() const
{
    SetUserAction(new OpticalPrimaryGenerator);
    SetUserAction(new OpticalRunAction);
    SetUserAction(new OpticalEventAction);
    SetUserAction(new OpticalSteppingAction);
}
