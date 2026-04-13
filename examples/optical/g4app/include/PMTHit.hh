// PMTHit.hh — hit object for a detected optical photon in a PMT.
#pragma once

#include "G4VHit.hh"
#include "G4THitsCollection.hh"
#include "G4ThreeVector.hh"
#include "G4String.hh"
#include "G4Allocator.hh"

class PMTHit : public G4VHit
{
public:
    PMTHit();
    ~PMTHit() override = default;

    // Fast pool allocation.
    void* operator new(size_t);
    void  operator delete(void*);

    void Draw()  override {}   // no vis dependency
    void Print() override;

    // Setters
    void SetPosition(const G4ThreeVector& v) { fPosition = v; }
    void SetTime    (G4double t)             { fTime     = t; }
    void SetEnergy  (G4double e)             { fEnergy   = e; }
    void SetPMTName (const G4String& s)      { fPMTName  = s; }
    void SetCopyNo  (G4int n)                { fCopyNo   = n; }
    void SetTrackID (G4int id)               { fTrackID  = id; }

    // Getters
    const G4ThreeVector& GetPosition() const { return fPosition; }
    G4double             GetTime()     const { return fTime; }
    G4double             GetEnergy()   const { return fEnergy; }
    const G4String&      GetPMTName()  const { return fPMTName; }
    G4int                GetCopyNo()   const { return fCopyNo; }
    G4int                GetTrackID()  const { return fTrackID; }

private:
    G4ThreeVector fPosition;
    G4double      fTime    = 0.0;
    G4double      fEnergy  = 0.0;
    G4String      fPMTName;
    G4int         fCopyNo  = -1;
    G4int         fTrackID = -1;
};

using PMTHitsCollection = G4THitsCollection<PMTHit>;

extern G4ThreadLocal G4Allocator<PMTHit>* PMTHitAllocator;

inline void* PMTHit::operator new(size_t)
{
    if (!PMTHitAllocator)
        PMTHitAllocator = new G4Allocator<PMTHit>;
    return PMTHitAllocator->MallocSingle();
}

inline void PMTHit::operator delete(void* hit)
{
    PMTHitAllocator->FreeSingle(static_cast<PMTHit*>(hit));
}
