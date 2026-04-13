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
#   cmake -S g4app -B g4app/build -DGeant4_DIR=/path/to/geant4/lib/cmake/Geant4
#
# The "gdml" component ensures the build fails loudly if Xerces-C was not
# enabled when Geant4 was compiled.
# ---------------------------------------------------------------------------
find_package(Geant4 REQUIRED gdml)
include(${Geant4_USE_FILE})

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

file(GLOB sources CONFIGURE_DEPENDS src/*.cc)
file(GLOB headers CONFIGURE_DEPENDS include/*.hh)

add_executable(optical_g4 main.cc ${sources} ${headers})
target_link_libraries(optical_g4 PRIVATE ${Geant4_LIBRARIES})

# ---------------------------------------------------------------------------
# Stage macros next to the build directory so the default paths in main.cc
# resolve correctly when running ./optical_g4 from g4app/build/.
# ---------------------------------------------------------------------------
file(COPY macros DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

# ---------------------------------------------------------------------------
# Helpful reminders
# ---------------------------------------------------------------------------
message(STATUS "")
message(STATUS "Build:  cmake --build ${CMAKE_BINARY_DIR}")
message(STATUS "Run (default):  ${CMAKE_BINARY_DIR}/optical_g4")
message(STATUS "Run (custom):   ${CMAKE_BINARY_DIR}/optical_g4 macros/run_traj.mac ../../optical_prism.gdml")
message(STATUS "  (generate optical_prism.gdml first with ../run.sh)")
message(STATUS "")
