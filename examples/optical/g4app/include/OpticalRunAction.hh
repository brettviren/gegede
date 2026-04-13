// OpticalRunAction.hh
//
// Opens/closes the CSV output files and provides write helpers used by
// OpticalEventAction to record hits and trajectory points.
//
// Output directory is taken from $OPTICAL_OUT_DIR (default: cwd).
#pragma once

#include "G4UserRunAction.hh"
#include <fstream>
#include <string>
#include <cstdint>

class G4Run;

class OpticalRunAction : public G4UserRunAction
{
public:
    OpticalRunAction();
    ~OpticalRunAction() override = default;

    void BeginOfRunAction(const G4Run*) override;
    void EndOfRunAction  (const G4Run*) override;

    // Called once per detected photon.
    void writeHit(int eventID, int hitID,
                  const std::string& pmtName, int copyNo,
                  double x_cm, double y_cm, double z_cm,
                  double t_ns, double energy_eV, double wavelength_nm);

    // Called once per trajectory point when trajectory storage is on.
    // energy_eV / wavelength_nm are the track's initial values (constant
    // across all points of an optical photon track).
    void writePoint(int eventID, int trackID, int parentID, int pdg,
                    int pointIdx,
                    double x_cm, double y_cm, double z_cm,
                    double energy_eV, double wavelength_nm);

private:
    std::ofstream fHitsFile;
    std::ofstream fTrajFile;
    std::uint64_t fNHits  = 0;
    std::uint64_t fNPoints = 0;
};
