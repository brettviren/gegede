// PMTSensitiveDetector.cc
#include "PMTSensitiveDetector.hh"

#include "G4Step.hh"
#include "G4Track.hh"
#include "G4StepPoint.hh"
#include "G4HCofThisEvent.hh"
#include "G4SDManager.hh"
#include "G4OpticalPhoton.hh"
#include "G4OpBoundaryProcess.hh"
#include "G4ProcessManager.hh"
#include "G4ProcessVector.hh"
#include "G4SystemOfUnits.hh"

PMTSensitiveDetector::PMTSensitiveDetector(const G4String& name)
    : G4VSensitiveDetector(name)
{
    collectionName.insert("PMTHitsCollection");
}

void PMTSensitiveDetector::Initialize(G4HCofThisEvent* hce)
{
    fHitsCollection = new PMTHitsCollection(SensitiveDetectorName,
                                            collectionName[0]);
    if (fHCID < 0)
        fHCID = G4SDManager::GetSDMpointer()
                    ->GetCollectionID(fHitsCollection);
    hce->AddHitsCollection(fHCID, fHitsCollection);
}

G4bool PMTSensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    // Only optical photons.
    if (step->GetTrack()->GetDefinition()
            != G4OpticalPhoton::OpticalPhotonDefinition())
        return false;

    // Only boundary steps (photon has just hit a surface).
    if (step->GetPostStepPoint()->GetStepStatus() != fGeomBoundary)
        return false;

    // Locate the OpBoundary process once; cache it.
    if (!fBoundaryProc)
        fBoundaryProc = FindBoundaryProcess();
    if (!fBoundaryProc)
        return false;

    // Only photons that were "detected" (absorbed + passed QE roll).
    if (fBoundaryProc->GetStatus() != Detection)
        return false;

    // Build and store the hit.
    auto* hit = new PMTHit;
    const G4StepPoint* post = step->GetPostStepPoint();
    const G4Track*     track = step->GetTrack();

    hit->SetPosition(post->GetPosition());
    hit->SetTime    (post->GetGlobalTime());
    hit->SetEnergy  (track->GetKineticEnergy());

    // LV name and copy number from the touchable.
    const G4TouchableHandle& th = post->GetTouchableHandle();
    hit->SetPMTName(th->GetVolume()->GetLogicalVolume()->GetName());
    hit->SetCopyNo (th->GetCopyNumber());
    hit->SetTrackID(track->GetTrackID());

    fHitsCollection->insert(hit);
    return true;
}

G4OpBoundaryProcess* PMTSensitiveDetector::FindBoundaryProcess()
{
    G4ProcessManager* pm =
        G4OpticalPhoton::OpticalPhotonDefinition()->GetProcessManager();
    if (!pm) return nullptr;

    G4ProcessVector* pv = pm->GetProcessList();
    for (std::size_t i = 0; i < static_cast<std::size_t>(pv->size()); ++i) {
        if (auto* bp = dynamic_cast<G4OpBoundaryProcess*>((*pv)[i]))
            return bp;
    }
    return nullptr;
}
