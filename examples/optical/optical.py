"""
GeGeDe builder for a simple optical detector geometry.

Geometry
--------
  world_vol  : 1 m cube of stainless steel
    water_vol  : 90 cm cube of water (centered)
      prism_vol : equilateral triangular glass prism (centered)
      pmt_vol   : 384 PMT hemispheres (8×8 grid on each of 6 faces)

Optical surfaces
----------------
  steel_air_surface  : OpticalSurface (dielectric_metal, unified, polished)
  air_steel_border   : BorderSurface  from water placement to steel world
  pmt_surface        : OpticalSurface (dielectric_metal) with EFFICIENCY
  pmt_skin           : SkinSurface    applied to pmt_vol

Material optical properties
---------------------------
  Water     RINDEX, ABSLENGTH, RAYLEIGH  (water Cherenkov detector quality)
  Glass     RINDEX = 1.60  (flat; real glass has dispersion)
  pmt_glass RINDEX = 1.50  (borosilicate PMT window glass)

PMT placement
-------------
  Each PMT is a hemisphere (rmax=5 cm, dtheta=90°).  PMTs are placed on a
  square grid with 10 cm spacing on all six inner faces of the air volume.
  Grid positions run from -35 cm to +35 cm in each transverse direction
  (8 positions per axis, 64 per face, 384 total).

  The ±35 cm limit avoids volume-overlap errors near the 8 corners of the
  air box: a PMT at ±40 cm on one face would overlap with the PMT at ±40 cm
  on an adjacent face because the hemisphere radius (5 cm) causes the two
  domes to intersect in the corner region.  At ±35 cm the nearest two
  cross-face PMT centres are sqrt(2)×10 cm ≈ 14.1 cm apart — comfortably
  greater than the sum of radii (10 cm).

  Each PMT hemisphere is oriented so its dome faces inward (toward the
  centre of the air volume).  The flat face (equatorial disc) is flush with
  the inner surface of the air box.

  All 384 PMTs share a single logical volume (pmt_vol) marked as a
  sensitive detector via the GDML <auxiliary> tag.

Usage
-----
Via the gegede CLI (recommended)::

    gegede -o optical_prism.gdml optical.cfg

Or directly::

    python optical.py            # writes optical_prism.gdml in cwd
"""

import math
import gegede.builder
from gegede import construct as con
from gegede.export import gdml as gdml_mod

# ---------------------------------------------------------------------------
# Photon energy range used for two-point optical property tables.
#
# Geant4 11+ reads GDML <matrix> values as bare numbers in Geant4 internal
# units (MeV for energy, mm for length).  There is NO automatic eV→MeV
# conversion.  So optical photon energies that are physically 1.77–4.14 eV
# must be written as 1.77e-6 – 4.14e-6 (MeV) in the GDML matrix.
# ---------------------------------------------------------------------------
_ELO   = 2.034e-6  # MeV  (~610 nm, red edge of visible)
_EHI   = 4.136e-6  # MeV  (~300 nm, near-UV edge)

# Peak bialkali response (~405 nm): used for the 3-point PMT QE table.
_EPEAK = 3.06e-6   # MeV  (~405 nm, blue/violet, near bialkali peak)

# ---------------------------------------------------------------------------
# Glass (prism) dispersive RINDEX — dense flint glass profile.
#
# Real glass separates colours because n varies with wavelength (Cauchy /
# Sellmeier dispersion).  For the prism these values are chosen to mimic a
# dense flint glass (Abbe number Vd ≈ 26) so that the rainbow separation is
# clearly visible in simulation.  Red bends least, violet bends most.
#
# Seven sample points: 700, 620, 580, 530, 490, 450, 400 nm.
# Energies in MeV (Geant4 internal units = eV × 1e-6).
# ---------------------------------------------------------------------------
_GLASS_RINDEX = [
    # (energy_MeV,  n)        wavelength
    (1.771e-6,  1.570),   # 700 nm  red
    (2.000e-6,  1.579),   # 620 nm  orange
    (2.138e-6,  1.585),   # 580 nm  yellow
    (2.340e-6,  1.596),   # 530 nm  green
    (2.530e-6,  1.609),   # 490 nm  cyan
    (2.755e-6,  1.626),   # 450 nm  blue
    (3.100e-6,  1.655),   # 400 nm  violet
]

# ---------------------------------------------------------------------------
# Water optical properties — representative of a water Cherenkov detector
# (e.g. Super-Kamiokande quality ultra-pure water).
#
# Five energy sample points: 700, 600, 500, 400, 300 nm.
# Energies in MeV (Geant4 internal units); physically 1.77–4.14 eV.
#
# RINDEX: Sellmeier dispersion for liquid water at room temperature.
#   n varies from ~1.331 (700 nm) to ~1.353 (300 nm).
#
# ABSLENGTH (absorption mean free path) in mm — Geant4 internal length unit.
#   Ultra-pure water is nearly transparent in the blue-green window (400-500 nm)
#   with typical attenuation lengths of 50-100 m; much shorter in the red and UV.
#   Values representative of SK-quality water measurements.
#
# RAYLEIGH (Rayleigh scattering mean free path) in mm.
#   Scales approximately as λ^4; at 400 nm ~34 m for pure water.
# ---------------------------------------------------------------------------
_WATER_PROPS = {
    # energy in MeV (= eV × 1e-6); 700 nm  600 nm  500 nm  400 nm  300 nm
    "energies": [1.77e-6,  2.07e-6,  2.48e-6,  3.10e-6,  4.14e-6],
    "rindex":   [1.3312,   1.3330,   1.3354,   1.3400,   1.3529],
    # Absorption mean free path in mm; poor in red and UV, excellent in blue-green
    "abslength":[1_000,    5_000,    50_000,   70_000,   1_000],  # mm
    # Rayleigh mean free path in mm; λ^4 dependence
    "rayleigh": [750_000,  200_000,  60_000,   15_000,   3_000],  # mm
}

def _water_table(key):
    """Return list of (energy_MeV, value) tuples for a water property."""
    return list(zip(_WATER_PROPS["energies"], _WATER_PROPS[key]))

# PMT grid: transverse positions on each face (cm).
# Runs from -35 to +35 in steps of 10 → 8 positions per axis, 64 per face.
# See module docstring for the rationale for stopping at ±35 cm.
_GRID_CM = list(range(-35, 36, 10))   # [-35, -25, ..., 25, 35]


class OpticalPrismBuilder(gegede.builder.Builder):
    """
    Build the optical prism geometry with PMTs.

    Configuration parameters
    ------------------------
    steel_dx : str
        Half-length of the cubic stainless-steel world (default "50cm").
    air_dx : str
        Half-length of the cubic air daughter volume (default "45cm").
    prism_dz : str
        Half-depth of the triangular glass prism along its extrusion axis
        (default "10cm").
    """

    defaults = dict(
        steel_dx = "50cm",   # 1 m cube
        air_dx   = "45cm",   # 90 cm cube
        prism_dz = "10cm",   # 20 cm deep prism
    )

    def configure(self, **kwargs):
        super().configure(**kwargs)

    def construct(self, geom):
        # ------------------------------------------------------------------
        # Elements
        # ------------------------------------------------------------------
        geom.matter.Element("Iron",     "Fe",  26, "55.845 g/mole")
        geom.matter.Element("Chromium", "Cr",  24, "51.996 g/mole")
        geom.matter.Element("Nickel",   "Ni",  28, "58.693 g/mole")
        geom.matter.Element("Hydrogen", "H",    1,  "1.008 g/mole")
        geom.matter.Element("Oxygen",   "O",    8, "15.999 g/mole")
        geom.matter.Element("Silicon",  "Si",  14, "28.086 g/mole")

        # ------------------------------------------------------------------
        # Materials
        # ------------------------------------------------------------------

        # Stainless steel 316L (simplified Fe/Cr/Ni by mass fraction).
        # No optical properties: opaque metal, handled via BorderSurface.
        geom.matter.Mixture(
            "StainlessSteel",
            symbol  = "SS316L",
            density = "8.0 g/cc",
            components = [
                ("Iron",     0.71),
                ("Chromium", 0.18),
                ("Nickel",   0.11),
            ])

        # Ultra-pure water — the active medium for a water Cherenkov detector.
        #
        # RINDEX: Sellmeier dispersion (~1.331 at 700 nm to ~1.353 at 300 nm).
        # ABSLENGTH: absorption mean free path in mm (Geant4 internal length
        #   unit).  Excellent in the 400-500 nm window (~50-70 m), strongly
        #   attenuated in the red and UV.
        # RAYLEIGH: Rayleigh scattering mean free path in mm.  Scales ~λ^4;
        #   ~15 m at 400 nm for pure water.
        #
        # All three properties are required by Geant4 optical physics for the
        # OpBoundary, OpAbsorption, and OpRayleigh processes to work correctly.
        geom.matter.Molecule(
            "Water",
            symbol   = "H2O",
            density  = "1.0 g/cc",
            elements = [
                ("Hydrogen", 2),
                ("Oxygen",   1),
            ],
            properties = [
                ("RINDEX",    _water_table("rindex")),
                ("ABSLENGTH", _water_table("abslength")),
                ("RAYLEIGH",  _water_table("rayleigh")),
            ])

        # Dense flint glass (SiO2-PbO).  Dispersive RINDEX: n ranges from
        # 1.570 (red 700 nm) to 1.655 (violet 400 nm), Abbe number Vd ≈ 26.
        # This material is used for the triangular prism.
        geom.matter.Molecule(
            "Glass",
            symbol   = "SiO2",
            density  = "2.2 g/cc",
            elements = [
                ("Silicon", 1),
                ("Oxygen",  2),
            ],
            properties = [
                ("RINDEX", _GLASS_RINDEX),
            ])

        # PMT window glass — borosilicate approximated as SiO2 with a
        # slightly lower refractive index (1.50) than the prism glass.
        # Geant4 uses this RINDEX to propagate photons across the
        # air-to-glass interface at the PMT entrance window.
        geom.matter.Molecule(
            "pmt_glass",
            symbol   = "SiO2",
            density  = "2.2 g/cc",
            elements = [
                ("Silicon", 1),
                ("Oxygen",  2),
            ],
            properties = [
                ("RINDEX", [(_ELO, 1.50), (_EHI, 1.50)]),
            ])

        # ------------------------------------------------------------------
        # Shapes
        # ------------------------------------------------------------------

        # Steel world cube
        geom.shapes.Box("steel_box",
                        self.steel_dx, self.steel_dx, self.steel_dx)

        # Air daughter cube
        geom.shapes.Box("air_box",
                        self.air_dx, self.air_dx, self.air_dx)

        # Triangular prism (ExtrudedOne with a 3-vertex polygon).
        # The cross-section is an equilateral-ish triangle:
        #   base = 30 cm  (from -15 cm to +15 cm along x)
        #   height = 20 cm (apex at y = +20 cm, base at y = 0)
        # The prism is extruded ±prism_dz along z.
        geom.shapes.ExtrudedOne(
            "glass_prism",
            polygon = [
                ("-15cm", "0cm"),
                ( "15cm", "0cm"),
                (  "0cm", "20cm"),
            ],
            dz      = self.prism_dz,
            offsetp = ["0cm", "0cm"],
            offsetm = ["0cm", "0cm"],
            scalep  = 1.0,
            scalem  = 1.0)

        # PMT hemisphere: northern-hemisphere sphere (stheta=0→90°).
        # Dome points toward +Z in local coordinates.  Placement rotations
        # (see below) orient the dome inward on each of the 6 faces.
        # rmax = 5 cm → 10 cm diameter.
        geom.shapes.Sphere(
            "pmt_hemi",
            rmax   = "5cm",
            dtheta = "90deg")

        # ------------------------------------------------------------------
        # Volumes
        # ------------------------------------------------------------------

        prism_vol = geom.structure.Volume(
            "prism_vol",
            material = "Glass",
            shape    = "glass_prism")

        # PMT logical volume — shared by all 384 placements.
        # The params list emits a GDML <auxiliary auxtype="SensDet"
        # auxvalue="PMTDetector"/> tag to mark this volume as the sensitive
        # detector for optical-photon hit collection.
        pmt_vol = geom.structure.Volume(
            "pmt_vol",
            material = "pmt_glass",
            shape    = "pmt_hemi",
            params   = [("SensDet", "PMTDetector")])

        # ------------------------------------------------------------------
        # Prism placement (centred in air)
        # ------------------------------------------------------------------
        prism_pos   = geom.structure.Position("prism_pos")
        prism_place = geom.structure.Placement(
            "prism_in_air", volume=prism_vol, pos=prism_pos)

        # ------------------------------------------------------------------
        # PMT rotations — one per face.
        # The PMT hemisphere solid has its dome at +Z (local).  To make the
        # dome face inward for each of the 6 air-box faces, we apply a
        # rotation that maps local +Z to the inward normal of that face.
        #
        # Convention (right-hand, active rotation around body axis):
        #
        #   Face   Inward normal   Rotation
        #   ----   -------------   ---------------------------
        #   +Z     -Z              Rx(180°)
        #   -Z     +Z              (identity — no rotation)
        #   +X     -X              Ry(-90°) maps +Z → -X
        #   -X     +X              Ry(+90°) maps +Z → +X
        #   +Y     -Y              Rx(+90°) maps +Z → -Y
        #   -Y     +Y              Rx(-90°) maps +Z → +Y
        # ------------------------------------------------------------------
        geom.structure.Rotation("pmt_rot_pz", x="180deg")
        # -Z face: identity (no named rotation needed)
        geom.structure.Rotation("pmt_rot_px", y="-90deg")
        geom.structure.Rotation("pmt_rot_mx", y="90deg")
        geom.structure.Rotation("pmt_rot_py", x="90deg")
        geom.structure.Rotation("pmt_rot_my", x="-90deg")

        # ------------------------------------------------------------------
        # PMT grid placements
        # Each face: 8 × 8 = 64 PMTs, 6 faces → 384 total.
        #
        # face_specs: (code, fixed_axis, fixed_val_cm, u_axis, v_axis, rot)
        #   code       : short label used in position/placement names
        #   fixed_axis : 'x', 'y', or 'z' — the axis perpendicular to the face
        #   fixed_val  : signed position in cm of the PMT centre on that axis
        #   u_axis     : first transverse axis
        #   v_axis     : second transverse axis
        #   rot        : name of the Rotation to use (None → identity)
        # ------------------------------------------------------------------
        face_specs = [
            ("pz", "z",  45, "x", "y", "pmt_rot_pz"),
            ("mz", "z", -45, "x", "y",  None),
            ("px", "x",  45, "y", "z", "pmt_rot_px"),
            ("mx", "x", -45, "y", "z", "pmt_rot_mx"),
            ("py", "y",  45, "x", "z", "pmt_rot_py"),
            ("my", "y", -45, "x", "z", "pmt_rot_my"),
        ]

        pmt_placements = []
        for fcode, fax, fval, uax, vax, rot_name in face_specs:
            for i, u in enumerate(_GRID_CM):
                for j, v in enumerate(_GRID_CM):
                    pos_name   = f"pmt_pos_{fcode}_{i}_{j}"
                    place_name = f"pmt_{fcode}_{i}_{j}"
                    coords = {fax: f"{fval}cm",
                              uax: f"{u}cm",
                              vax: f"{v}cm"}
                    pos = geom.structure.Position(pos_name, **coords)
                    place = geom.structure.Placement(
                        place_name,
                        volume = pmt_vol,
                        pos    = pos,
                        rot    = rot_name)
                    pmt_placements.append(place)

        # ------------------------------------------------------------------
        # Water volume: prism + all PMTs
        # ------------------------------------------------------------------
        air_vol = geom.structure.Volume(
            "air_vol",
            material   = "Water",
            shape      = "air_box",
            placements = [prism_place] + pmt_placements)

        # Centre the air cube in the steel world.
        air_pos   = geom.structure.Position("air_pos")
        air_place = geom.structure.Placement(
            "air_in_steel", volume=air_vol, pos=air_pos)

        world_vol = geom.structure.Volume(
            "world_vol",
            material   = "StainlessSteel",
            shape      = "steel_box",
            placements = [air_place])

        # Register the world volume so the CLI and build() can find it.
        self.add_volume(world_vol)

        # ------------------------------------------------------------------
        # Optical surfaces
        # ------------------------------------------------------------------

        # Steel–air boundary: polished metal reflector.
        geom.surfaces.OpticalSurface(
            "steel_air_surface",
            model  = "unified",
            finish = "polished",
            type   = "dielectric_metal",
            value  = 1.0,
            properties = [
                ("REFLECTIVITY", [(_ELO, 0.90), (_EHI, 0.85)]),
            ])

        geom.surfaces.BorderSurface(
            "air_steel_border",
            surface  = "steel_air_surface",
            physvol1 = "air_in_steel",
            physvol2 = "air_in_steel")

        # PMT photocathode surface.
        # model='unified', finish='polished', type='dielectric_metal':
        #   models a photocathode as an absorbing metal layer.
        #
        # REFLECTIVITY: fraction of photons reflected back into the water.
        #   Set to 0.0 so every photon that reaches the surface is absorbed.
        #   Geant4 defaults REFLECTIVITY to 1.0 when absent (fully reflective),
        #   which would suppress all detections — so this property is required.
        #
        # EFFICIENCY: quantum efficiency (probability that an absorbed photon
        #   generates a photoelectron).  Three-point table representative of a
        #   bialkali photocathode used in water Cherenkov detectors
        #   (e.g. Hamamatsu R7081 series):
        #     610 nm (2.03 eV): ~5 %   — red tail, low QE
        #     405 nm (3.06 eV): ~25%   — near peak
        #     300 nm (4.14 eV): ~8 %   — near-UV declining edge
        geom.surfaces.OpticalSurface(
            "pmt_surface",
            model  = "unified",
            finish = "polished",
            type   = "dielectric_metal",
            value  = 1.0,
            properties = [
                ("REFLECTIVITY", [(_ELO, 0.0), (_EHI, 0.0)]),
                ("EFFICIENCY",   [(_ELO, 0.05), (_EPEAK, 0.25), (_EHI, 0.08)]),
            ])

        # Apply pmt_surface to every physical instance of pmt_vol via a
        # SkinSurface.  A single SkinSurface covers all 384 placements
        # because they all share this logical volume.
        geom.surfaces.SkinSurface(
            "pmt_skin",
            surface = "pmt_surface",
            volume  = "pmt_vol")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def build(output="optical_prism.gdml", validate=True):
    """
    Build the geometry and write a GDML file.

    Parameters
    ----------
    output : str
        Output filename.
    validate : bool
        If True, validate the GDML against the schema before writing.
    """
    import gegede.builder as bld

    builder = OpticalPrismBuilder("OpticalPrism")
    builder.configure()

    geom = con.Geometry()
    bld.construct(builder, geom)
    geom.set_world(builder.get_volume(0))

    obj = gdml_mod.convert(geom)
    if validate:
        gdml_mod.validate_object(obj)
    gdml_mod.output(obj, output)
    print(f"Wrote {output}")
    return output


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "optical_prism.gdml"
    build(output=out)
