// OpticalActionInitialization.hh
#pragma once

#include "G4VUserActionInitialization.hh"

class OpticalActionInitialization : public G4VUserActionInitialization
{
public:
    OpticalActionInitialization()  = default;
    ~OpticalActionInitialization() override = default;

    void Build() const override;
};
