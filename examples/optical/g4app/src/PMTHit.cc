// PMTHit.cc
#include "PMTHit.hh"
#include "G4SystemOfUnits.hh"
#include <iostream>

G4ThreadLocal G4Allocator<PMTHit>* PMTHitAllocator = nullptr;

PMTHit::PMTHit() = default;

void PMTHit::Print()
{
    std::cout << "  PMTHit  pmt=" << fPMTName
              << "  copy="        << fCopyNo
              << "  track="       << fTrackID
              << "  E="           << fEnergy / eV  << " eV"
              << "  t="           << fTime   / ns  << " ns"
              << "  pos=("        << fPosition.x() / cm << ","
                                  << fPosition.y() / cm << ","
                                  << fPosition.z() / cm << ") cm\n";
}
