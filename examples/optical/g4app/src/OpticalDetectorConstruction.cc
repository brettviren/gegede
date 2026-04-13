// OpticalDetectorConstruction.cc
#include "OpticalDetectorConstruction.hh"
#include "PMTSensitiveDetector.hh"

#include "G4VPhysicalVolume.hh"
#include "G4LogicalVolume.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4Material.hh"
#include "G4MaterialPropertiesTable.hh"
#include "G4LogicalBorderSurface.hh"
#include "G4LogicalSkinSurface.hh"
#include "G4OpticalSurface.hh"
#include "G4SDManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4GDMLAuxStructType.hh"

#include <iostream>
#include <string>

// ---------------------------------------------------------------------------
// Recursively print the physical-volume tree (same helper as original main.cc)
// ---------------------------------------------------------------------------
static void printTree(const G4VPhysicalVolume* pv, int depth = 0,
                      int max_depth = 3)
{
    std::string pad(depth * 2, ' ');
    const G4LogicalVolume* lv = pv->GetLogicalVolume();
    std::cout << pad << pv->GetName()
              << "  [" << lv->GetMaterial()->GetName() << "]\n";
    if (max_depth >= 0 && depth >= max_depth)
        return;
    std::size_t ndau = lv->GetNoDaughters();
    constexpr std::size_t kShowMax = 4;
    std::size_t show = (ndau <= kShowMax) ? ndau : kShowMax;
    for (std::size_t i = 0; i < show; ++i)
        printTree(lv->GetDaughter(static_cast<int>(i)), depth + 1, max_depth);
    if (ndau > kShowMax)
        std::cout << pad << "  ... (" << ndau - kShowMax
                  << " more daughters not shown)\n";
}

// ---------------------------------------------------------------------------

OpticalDetectorConstruction::OpticalDetectorConstruction(std::string gdmlPath)
    : fGDMLPath(std::move(gdmlPath))
{}

G4VPhysicalVolume* OpticalDetectorConstruction::Construct()
{
    fParser.Read(fGDMLPath, /*validate=*/false);

    G4VPhysicalVolume* world = fParser.GetWorldVolume();
    if (!world) {
        G4Exception("OpticalDetectorConstruction::Construct",
                    "NoWorld", FatalException,
                    ("No world volume found in " + fGDMLPath).c_str());
    }

    printInspection(world);
    return world;
}

void OpticalDetectorConstruction::ConstructSDandField()
{
    auto* pmtSD = new PMTSensitiveDetector("PMTDetector");
    G4SDManager::GetSDMpointer()->AddNewDetector(pmtSD);

    // Walk every logical volume and attach the SD to those tagged SensDet.
    const G4LogicalVolumeStore* lvs = G4LogicalVolumeStore::GetInstance();
    for (G4LogicalVolume* lv : *lvs) {
        const G4GDMLAuxListType& auxList =
            fParser.GetVolumeAuxiliaryInformation(lv);
        for (const auto& aux : auxList) {
            if (aux.type == "SensDet" && aux.value == "PMTDetector") {
                lv->SetSensitiveDetector(pmtSD);
                std::cout << "  [SD] attached PMTDetector to "
                          << lv->GetName() << "\n";
            }
        }
    }
}

void OpticalDetectorConstruction::printInspection(
    const G4VPhysicalVolume* world) const
{
    std::cout << "\n=== Volume tree ===\n";
    printTree(world);

    std::cout << "\n=== Materials ===\n";
    for (const G4Material* mat : *G4Material::GetMaterialTable()) {
        std::cout << "  " << mat->GetName()
                  << "  density=" << mat->GetDensity() / (g / cm3)
                  << " g/cm3";
        const G4MaterialPropertiesTable* mpt =
            mat->GetMaterialPropertiesTable();
        if (mpt) {
            std::cout << "  optical-props:";
            for (const char* key : {"RINDEX", "ABSLENGTH", "SCINTILLATIONYIELD"})
                if (mpt->GetProperty(key))
                    std::cout << " " << key;
        }
        std::cout << "\n";
    }

    std::cout << "\n=== Border surfaces ===\n";
    const auto* borders = G4LogicalBorderSurface::GetSurfaceTable();
    if (borders && !borders->empty()) {
        for (const auto& [key, bs] : *borders) {
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
                    for (const char* prop : {"REFLECTIVITY", "EFFICIENCY",
                                             "SPECULARLOBECONSTANT"})
                        if (smpt->GetProperty(prop))
                            std::cout << " " << prop;
                    std::cout << "\n";
                }
            }
        }
    } else {
        std::cout << "  (none)\n";
    }

    std::cout << "\n=== Skin surfaces ===\n";
    const auto* skins = G4LogicalSkinSurface::GetSurfaceTable();
    if (skins && !skins->empty()) {
        for (const auto& [key, ss] : *skins)
            std::cout << "  " << ss->GetName()
                      << "  lv: " << ss->GetLogicalVolume()->GetName()
                      << "\n";
    } else {
        std::cout << "  (none)\n";
    }
    std::cout << "\n";
}
