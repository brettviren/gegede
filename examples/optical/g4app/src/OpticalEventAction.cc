// OpticalEventAction.cc
//
// PMT hit recording is handled by OpticalSteppingAction (which fires at
// the exact boundary step where G4OpBoundaryProcess sets status=Detection).
// This class only handles optional trajectory recording.
#include "OpticalEventAction.hh"
#include "OpticalRunAction.hh"

#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4VTrajectory.hh"
#include "G4VTrajectoryPoint.hh"
#include "G4TrajectoryContainer.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"

OpticalEventAction::OpticalEventAction() = default;

OpticalRunAction* OpticalEventAction::getRunAction()
{
    if (!fRunAction) {
        fRunAction = const_cast<OpticalRunAction*>(
            static_cast<const OpticalRunAction*>(
                G4RunManager::GetRunManager()->GetUserRunAction()));
    }
    return fRunAction;
}

void OpticalEventAction::EndOfEventAction(const G4Event* event)
{
    // ------------------------------------------------------------------
    // Trajectory points (only written when /tracking/storeTrajectory > 0)
    // ------------------------------------------------------------------
    G4TrajectoryContainer* trajCont = event->GetTrajectoryContainer();
    if (!trajCont) return;

    OpticalRunAction* runAction = getRunAction();
    const int evtID = event->GetEventID();

    for (std::size_t t = 0; t < trajCont->size(); ++t) {
        G4VTrajectory* traj = (*trajCont)[t];
        if (!traj) continue;

        int trackID  = traj->GetTrackID();
        int parentID = traj->GetParentID();
        int pdg      = traj->GetPDGEncoding();

        // Energy is constant for optical photons (massless, elastic scattering).
        // |p| = KE in G4 natural units; initial momentum magnitude gives the
        // creation energy.  λ [nm] = hc / E  (hc ≈ 1239.84 eV·nm).
        const double energy_eV = traj->GetInitialMomentum().mag() / eV;
        const double wl_nm = (energy_eV > 0.0) ? 1239.84193 / energy_eV : 0.0;

        for (int p = 0; p < traj->GetPointEntries(); ++p) {
            G4VTrajectoryPoint* pt = traj->GetPoint(p);
            if (!pt) continue;
            const G4ThreeVector& pos3 = pt->GetPosition();
            runAction->writePoint(
                evtID, trackID, parentID, pdg, p,
                pos3.x() / cm,
                pos3.y() / cm,
                pos3.z() / cm,
                energy_eV,
                wl_nm);
        }
    }
}
