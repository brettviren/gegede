cmake_minimum_required(VERSION 3.16)
project(optical_g4app VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---------------------------------------------------------------------------
# Geant4
#
# Requires Geant4 built with GDML support (Xerces-C).  Point CMake at the
# installation with -DGeant4_DIR or the environment variable Geant4_DIR:
#
#   cmake -S . -B build -DGeant4_DIR=/path/to/geant4/lib/Geant4-XX.Y
#
# Typical Geant4 install layout:
#   /opt/geant4/lib/Geant4-11.2.0/Geant4Config.cmake
#   /opt/geant4/lib/Geant4-11.2.0/Geant4ConfigVersion.cmake
#
# The "gdml" component ensures the build fails loudly if Xerces-C was not
# enabled when Geant4 was compiled.
# ---------------------------------------------------------------------------
find_package(Geant4 REQUIRED gdml)
include(${Geant4_USE_FILE})

# ---------------------------------------------------------------------------
# Executable
# ---------------------------------------------------------------------------
add_executable(optical_g4 main.cc)
target_link_libraries(optical_g4 PRIVATE ${Geant4_LIBRARIES})

# ---------------------------------------------------------------------------
# Helpful reminder
# ---------------------------------------------------------------------------
message(STATUS "")
message(STATUS "Build:  cmake --build build")
message(STATUS "Run:    ./build/optical_g4 ../optical_prism.gdml")
message(STATUS "  (generate optical_prism.gdml first with ../run.sh)")
message(STATUS "")
