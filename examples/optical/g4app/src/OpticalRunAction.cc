// OpticalRunAction.cc
#include "OpticalRunAction.hh"

#include "G4Run.hh"
#include "G4SystemOfUnits.hh"

#include <cstdlib>
#include <filesystem>
#include <iostream>

OpticalRunAction::OpticalRunAction() = default;

void OpticalRunAction::BeginOfRunAction(const G4Run*)
{
    fNHits   = 0;
    fNPoints = 0;

    // Output directory from environment; default to cwd.
    std::string outDir = ".";
    if (const char* env = std::getenv("OPTICAL_OUT_DIR"))
        outDir = env;

    auto hitsPath = outDir + "/hits.csv";
    auto trajPath = outDir + "/trajectories.csv";

    fHitsFile.open(hitsPath);
    if (!fHitsFile)
        G4Exception("OpticalRunAction::BeginOfRunAction",
                    "FileOpen", FatalException,
                    ("Cannot open " + hitsPath).c_str());
    fHitsFile << "event_id,hit_id,pmt_name,copyno,"
                 "x_cm,y_cm,z_cm,t_ns,energy_eV,wavelength_nm\n";

    fTrajFile.open(trajPath);
    if (!fTrajFile)
        G4Exception("OpticalRunAction::BeginOfRunAction",
                    "FileOpen", FatalException,
                    ("Cannot open " + trajPath).c_str());
    fTrajFile << "event_id,track_id,parent_id,pdg,"
                 "point_idx,x_cm,y_cm,z_cm,energy_eV,wavelength_nm\n";
}

void OpticalRunAction::EndOfRunAction(const G4Run* run)
{
    fHitsFile.close();
    fTrajFile.close();

    std::cout << "\n--- Run summary ---\n"
              << "  Events  : " << run->GetNumberOfEvent() << "\n"
              << "  PMT hits: " << fNHits   << "\n"
              << "  Traj pts: " << fNPoints << "\n"
              << "  Output  : hits.csv, trajectories.csv\n";
}

void OpticalRunAction::writeHit(int eventID, int hitID,
                                const std::string& pmtName, int copyNo,
                                double x_cm, double y_cm, double z_cm,
                                double t_ns, double energy_eV,
                                double wavelength_nm)
{
    fHitsFile << eventID     << ','
              << hitID       << ','
              << pmtName     << ','
              << copyNo      << ','
              << x_cm        << ','
              << y_cm        << ','
              << z_cm        << ','
              << t_ns        << ','
              << energy_eV   << ','
              << wavelength_nm << '\n';
    ++fNHits;
}

void OpticalRunAction::writePoint(int eventID, int trackID, int parentID,
                                  int pdg, int pointIdx,
                                  double x_cm, double y_cm, double z_cm,
                                  double energy_eV, double wavelength_nm)
{
    fTrajFile << eventID       << ','
              << trackID       << ','
              << parentID      << ','
              << pdg           << ','
              << pointIdx      << ','
              << x_cm          << ','
              << y_cm          << ','
              << z_cm          << ','
              << energy_eV     << ','
              << wavelength_nm << '\n';
    ++fNPoints;
}
