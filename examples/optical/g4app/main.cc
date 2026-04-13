// main.cc — Optical photon simulation for the gegede optical_prism example.
//
// Reads the GDML geometry produced by optical.py, runs a Geant4 batch
// simulation driven by a macro file, and writes PMT hits and (optionally)
// optical-photon trajectories to CSV files.
//
// Usage:
//   ./optical_g4 [macro.mac] [path/to/optical_prism.gdml]
//
// Defaults (when run from g4app/build/):
//   macro : macros/run.mac          (copied here by CMake)
//   GDML  : ../../optical_prism.gdml
//
// Environment overrides:
//   OPTICAL_MACRO  — path to macro file
//   OPTICAL_GDML   — path to GDML file
//   OPTICAL_OUT_DIR — directory for hits.csv / trajectories.csv (default: cwd)
//
// Generate the GDML first:
//   cd examples/optical && ./run.sh
//
// Build:
//   cmake -S g4app -B g4app/build -DGeant4_DIR=/path/to/Geant4
//   cmake --build g4app/build
//
// Run (no trajectories, 1000 photons):
//   ./g4app/build/optical_g4
//
// Run with trajectories (50 photons):
//   ./g4app/build/optical_g4 macros/run_traj.mac optical_prism.gdml

#include "OpticalDetectorConstruction.hh"
#include "OpticalActionInitialization.hh"
#include "OpticalPhysicsList.hh"

#include "G4RunManager.hh"
#include "G4UImanager.hh"

#include <iostream>
#include <string>
#include <cstdlib>

int main(int argc, char** argv)
{
    // ------------------------------------------------------------------
    // Resolve macro and GDML paths.
    // Priority: command-line argument > environment variable > default.
    // ------------------------------------------------------------------
    const char* macro_env = std::getenv("OPTICAL_MACRO");
    const char* gdml_env  = std::getenv("OPTICAL_GDML");

    std::string macro_path = (argc > 1) ? argv[1]
                           : (macro_env ? macro_env : "macros/run.mac");
    std::string gdml_path  = (argc > 2) ? argv[2]
                           : (gdml_env  ? gdml_env  : "../../optical_prism.gdml");

    std::cout << "Macro: " << macro_path << "\n";
    std::cout << "GDML : " << gdml_path  << "\n";

    // ------------------------------------------------------------------
    // Run manager + detector construction
    // ------------------------------------------------------------------
    auto* rm = new G4RunManager;
    rm->SetUserInitialization(new OpticalDetectorConstruction(gdml_path));

    // Minimal physics list: EM + optical only (avoids slow hadronic init).
    rm->SetUserInitialization(new OpticalPhysicsList);

    // User actions: generator, run action, event action.
    rm->SetUserInitialization(new OpticalActionInitialization);

    rm->Initialize();

    // ------------------------------------------------------------------
    // Execute the macro
    // ------------------------------------------------------------------
    G4UImanager::GetUIpointer()
        ->ApplyCommand("/control/execute " + macro_path);

    delete rm;
    return 0;
}
