// OpticalSteppingAction.cc
#include "OpticalSteppingAction.hh"
#include "OpticalRunAction.hh"

#include "G4Step.hh"
#include "G4Track.hh"
#include "G4StepPoint.hh"
#include "G4VPhysicalVolume.hh"
#include "G4LogicalVolume.hh"
#include "G4OpticalPhoton.hh"
#include "G4OpBoundaryProcess.hh"
#include "G4ProcessManager.hh"
#include "G4ProcessVector.hh"
#include "G4RunManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"

OpticalSteppingAction::OpticalSteppingAction() = default;

OpticalRunAction* OpticalSteppingAction::getRunAction()
{
    if (!fRunAction) {
        fRunAction = const_cast<OpticalRunAction*>(
            static_cast<const OpticalRunAction*>(
                G4RunManager::GetRunManager()->GetUserRunAction()));
    }
    return fRunAction;
}

G4OpBoundaryProcess* OpticalSteppingAction::findBoundaryProcess()
{
    G4ProcessManager* pm =
        G4OpticalPhoton::OpticalPhotonDefinition()->GetProcessManager();
    if (!pm) return nullptr;
    G4ProcessVector* pv = pm->GetProcessList();
    for (std::size_t i = 0; i < static_cast<std::size_t>(pv->size()); ++i)
        if (auto* bp = dynamic_cast<G4OpBoundaryProcess*>((*pv)[i]))
            return bp;
    return nullptr;
}

void OpticalSteppingAction::UserSteppingAction(const G4Step* step)
{
    // Only optical photons.
    if (step->GetTrack()->GetDefinition()
            != G4OpticalPhoton::OpticalPhotonDefinition())
        return;

    // Only steps that end at a geometry boundary.
    const G4StepPoint* post = step->GetPostStepPoint();
    if (post->GetStepStatus() != fGeomBoundary) return;

    // Post-step volume must be a PMT volume.
    const G4VPhysicalVolume* postPV = post->GetPhysicalVolume();
    if (!postPV) return;
    if (postPV->GetLogicalVolume()->GetName() != "pmt_vol") return;

    // Locate the OpBoundary process once; cache it.
    if (!fBoundaryProc) fBoundaryProc = findBoundaryProcess();
    if (!fBoundaryProc) return;

    // Only count photons that passed the quantum-efficiency roll.
    if (fBoundaryProc->GetStatus() != Detection) return;

    // Track hit index, reset when event changes.
    const int evtID =
        G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();
    if (evtID != fCachedEvtID) { fHitID = 0; fCachedEvtID = evtID; }

    const G4Track* track = step->GetTrack();
    const double energy_eV = track->GetKineticEnergy() / eV;
    // λ [nm] = hc / E  (hc ≈ 1239.84 eV·nm)
    const double wl_nm = (energy_eV > 0.0) ? 1239.84193 / energy_eV : 0.0;

    getRunAction()->writeHit(
        evtID,
        fHitID++,
        postPV->GetLogicalVolume()->GetName(),
        post->GetTouchableHandle()->GetCopyNumber(),
        post->GetPosition().x() / cm,
        post->GetPosition().y() / cm,
        post->GetPosition().z() / cm,
        post->GetGlobalTime() / ns,
        energy_eV,
        wl_nm);
}
