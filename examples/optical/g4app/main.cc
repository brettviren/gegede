// main.cc — Minimal Geant4 application for the optical_prism GDML example.
//
// Reads the GDML file produced by the gegede optical builder, prints the
// volume tree, lists materials with their optical property tables, and
// reports the border/skin surfaces that drive Geant4 optical-photon tracking.
//
// Usage:
//   ./optical_g4 [path/to/optical_prism.gdml]
//
// Generate the GDML first:
//   cd ..
//   ./run.sh          # or: python optical.py
//
// To extend this into a full optical simulation, see the comments marked
// "TODO(optical-sim)" below.

#include <iostream>
#include <string>

#include "G4GDMLParser.hh"
#include "G4VPhysicalVolume.hh"
#include "G4LogicalVolume.hh"
#include "G4Material.hh"
#include "G4MaterialPropertiesTable.hh"
#include "G4LogicalBorderSurface.hh"
#include "G4LogicalSkinSurface.hh"
#include "G4OpticalSurface.hh"
#include "G4SystemOfUnits.hh"

// ---------------------------------------------------------------------------
// Recursively print the physical-volume tree.
// ---------------------------------------------------------------------------
static void printTree(const G4VPhysicalVolume* pv, int depth = 0)
{
    std::string pad(depth * 2, ' ');
    const G4LogicalVolume* lv = pv->GetLogicalVolume();
    std::cout << pad << pv->GetName()
              << "  [" << lv->GetMaterial()->GetName() << "]\n";
    for (std::size_t i = 0; i < lv->GetNoDaughters(); ++i)
        printTree(lv->GetDaughter(static_cast<int>(i)), depth + 1);
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------
int main(int argc, char** argv)
{
    // Default path assumes the executable was built in g4app/build/ and the
    // GDML was written to examples/optical/.
    const std::string gdml_path =
        (argc > 1) ? argv[1] : "../../optical_prism.gdml";

    std::cout << "Reading GDML: " << gdml_path << "\n";

    // Parse the GDML file.
    // Pass validate=false so the parser does not attempt to fetch the
    // GDML XSD from the network; schema validation was already performed
    // by gegede during export.
    G4GDMLParser parser;
    parser.Read(gdml_path, /*validate=*/false);

    G4VPhysicalVolume* world = parser.GetWorldVolume();
    if (!world) {
        std::cerr << "ERROR: no world volume found in " << gdml_path << "\n";
        return 1;
    }

    // ------------------------------------------------------------------
    // Volume tree
    // ------------------------------------------------------------------
    std::cout << "\n=== Volume tree ===\n";
    printTree(world);

    // ------------------------------------------------------------------
    // Materials
    // ------------------------------------------------------------------
    std::cout << "\n=== Materials ===\n";
    for (const G4Material* mat : *G4Material::GetMaterialTable()) {
        std::cout << "  " << mat->GetName()
                  << "  density=" << mat->GetDensity() / (g / cm3)
                  << " g/cm3";
        const G4MaterialPropertiesTable* mpt =
            mat->GetMaterialPropertiesTable();
        if (mpt) {
            // Check for the properties that were set in optical.py.
            std::cout << "  optical-props:";
            for (const char* key : {"RINDEX", "ABSLENGTH", "SCINTILLATIONYIELD"})
                if (mpt->GetProperty(key))
                    std::cout << " " << key;
        }
        std::cout << "\n";
    }

    // ------------------------------------------------------------------
    // Border surfaces (air↔steel boundary)
    // ------------------------------------------------------------------
    std::cout << "\n=== Border surfaces ===\n";
    const auto* borders = G4LogicalBorderSurface::GetSurfaceTable();
    if (borders && !borders->empty()) {
        for (const G4LogicalBorderSurface* bs : *borders) {
            std::cout << "  " << bs->GetName() << "\n";
            std::cout << "    pv1: " << bs->GetVolume1()->GetName() << "\n";
            std::cout << "    pv2: " << bs->GetVolume2()->GetName() << "\n";
            const G4OpticalSurface* os =
                dynamic_cast<const G4OpticalSurface*>(
                    bs->GetSurfaceProperty());
            if (os) {
                const G4MaterialPropertiesTable* smpt =
                    os->GetMaterialPropertiesTable();
                if (smpt) {
                    std::cout << "    surface-props:";
                    for (const char* key : {"REFLECTIVITY", "EFFICIENCY",
                                            "SPECULARLOBECONSTANT"})
                        if (smpt->GetProperty(key))
                            std::cout << " " << key;
                    std::cout << "\n";
                }
            }
        }
    } else {
        std::cout << "  (none)\n";
    }

    // ------------------------------------------------------------------
    // Skin surfaces (volume-wide coating)
    // ------------------------------------------------------------------
    std::cout << "\n=== Skin surfaces ===\n";
    const auto* skins = G4LogicalSkinSurface::GetSurfaceTable();
    if (skins && !skins->empty()) {
        for (const G4LogicalSkinSurface* ss : *skins)
            std::cout << "  " << ss->GetName()
                      << "  lv: " << ss->GetLogicalVolume()->GetName()
                      << "\n";
    } else {
        std::cout << "  (none)\n";
    }

    // ------------------------------------------------------------------
    // TODO(optical-sim): To run an optical photon simulation, add:
    //
    //   1. A G4RunManager (or G4MTRunManager for multi-threading):
    //        auto* rm = new G4RunManager;
    //
    //   2. A detector construction that wraps the GDML world:
    //        rm->SetUserInitialization(new GDMLDetectorConstruction(world));
    //
    //   3. A physics list that includes optical processes, e.g.:
    //        #include "FTFP_BERT.hh"
    //        #include "G4OpticalPhysics.hh"
    //        auto* pl = new FTFP_BERT;
    //        pl->RegisterPhysics(new G4OpticalPhysics);
    //        rm->SetUserInitialization(pl);
    //
    //   4. An action initialisation providing a primary generator that
    //      shoots G4OpticalPhoton particles into the prism.
    //
    //   5. rm->Initialize();
    //      rm->BeamOn(N);
    //
    // ------------------------------------------------------------------

    std::cout << "\nDone.\n";
    return 0;
}
