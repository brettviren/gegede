"""
GeGeDe builder for a simple optical detector geometry.

Geometry
--------
  world_vol  : 1 m cube of stainless steel
    air_vol  : 90 cm cube of dry air (centered)
      prism_vol : equilateral triangular glass prism (centered)

Optical surfaces
----------------
  steel_air_surface  : OpticalSurface (dielectric_metal, unified, polished)
  air_steel_border   : BorderSurface  from air placement to steel world

Material optical properties
---------------------------
  Air   RINDEX = 1.00  (flat across optical range)
  Glass RINDEX = 1.60  (flat; real glass has dispersion)

Usage
-----
Via the gegede CLI (recommended)::

    gegede -o optical_prism.gdml optical.cfg

Or directly::

    python optical.py            # writes optical_prism.gdml in cwd
"""

import gegede.builder
from gegede import construct as con
from gegede.export import gdml as gdml_mod

# ---------------------------------------------------------------------------
# Photon energy range used for all two-point optical property tables.
# Values are in eV expressed as plain floats; Geant4 interprets the numbers
# in whatever unit the GDML file declares (here: no unit on matrix values,
# so the calling code must supply eV-scale floats if the property is
# RINDEX/REFLECTIVITY).  Two bracketing points are sufficient for a flat
# (wavelength-independent) property.
# ---------------------------------------------------------------------------
_ELO = 2.034   # ~610 nm  (red edge of visible)
_EHI = 4.136   # ~300 nm  (near-UV edge)


class OpticalPrismBuilder(gegede.builder.Builder):
    """
    Build the optical prism geometry.

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
        geom.matter.Element("Iron",     "Fe", 26, "55.845 g/mole")
        geom.matter.Element("Chromium", "Cr", 24, "51.996 g/mole")
        geom.matter.Element("Nickel",   "Ni", 28, "58.693 g/mole")
        geom.matter.Element("Nitrogen", "N",   7, "14.007 g/mole")
        geom.matter.Element("Oxygen",   "O",   8, "15.999 g/mole")
        geom.matter.Element("Silicon",  "Si", 14, "28.086 g/mole")

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

        # Dry air.  RINDEX=1.0 (flat) is required by Geant4 optical physics
        # for any medium through which optical photons will propagate.
        # Property rows are (energy_eV, value) 2-tuples → coldim=2.
        geom.matter.Mixture(
            "Air",
            symbol  = "Air",
            density = "1.29 mg/cc",
            components = [
                ("Nitrogen", 0.78),
                ("Oxygen",   0.22),
            ],
            properties = [
                ("RINDEX", [(_ELO, 1.00), (_EHI, 1.00)]),
            ])

        # Fused silica / glass (SiO2).  RINDEX=1.6 (flat approximation).
        # Real borosilicate glass has modest dispersion, but 1.6 suffices for
        # a demonstration.
        geom.matter.Molecule(
            "Glass",
            symbol   = "SiO2",
            density  = "2.2 g/cc",
            elements = [
                ("Silicon", 1),
                ("Oxygen",  2),
            ],
            properties = [
                ("RINDEX", [(_ELO, 1.60), (_EHI, 1.60)]),
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
        # The centroid of the triangle (at y ≈ 6.67 cm) is close enough to
        # the air-cube centre for a demonstration.
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

        # ------------------------------------------------------------------
        # Volumes and placements
        # ------------------------------------------------------------------

        prism_vol = geom.structure.Volume(
            "prism_vol",
            material = "Glass",
            shape    = "glass_prism")

        # Centre the prism in the air cube (default Position is the origin).
        prism_pos   = geom.structure.Position("prism_pos")
        prism_place = geom.structure.Placement(
            "prism_in_air", volume = prism_vol, pos = prism_pos)

        air_vol = geom.structure.Volume(
            "air_vol",
            material   = "Air",
            shape      = "air_box",
            placements = [prism_place])

        # Centre the air cube in the steel world.
        air_pos   = geom.structure.Position("air_pos")
        air_place = geom.structure.Placement(
            "air_in_steel", volume = air_vol, pos = air_pos)

        world_vol = geom.structure.Volume(
            "world_vol",
            material   = "StainlessSteel",
            shape      = "steel_box",
            placements = [air_place])

        # Register this as the single output volume of the builder.
        # main.py calls geom.set_world() on it after construction.
        self.add_volume(world_vol)

        # ------------------------------------------------------------------
        # Optical surfaces
        # ------------------------------------------------------------------

        # Surface property set for the stainless-steel inner walls.
        # model='unified'           : unified micro-facet model
        # finish='polished'         : smooth polished metal surface
        # type='dielectric_metal'   : one side dielectric (air), one metal
        # REFLECTIVITY drops gently toward UV (eV ↑ → wavelength ↓).
        geom.surfaces.OpticalSurface(
            "steel_air_surface",
            model  = "unified",
            finish = "polished",
            type   = "dielectric_metal",
            value  = 1.0,
            properties = [
                ("REFLECTIVITY", [(_ELO, 0.90), (_EHI, 0.85)]),
            ])

        # Border surface between the air placement and the steel world.
        # physvol1 / physvol2 are the names of the two Placement objects that
        # bound this surface.  For a single placement (air inside steel) the
        # same name is given twice, which is the standard Geant4 idiom for a
        # 1-sided border.
        geom.surfaces.BorderSurface(
            "air_steel_border",
            surface  = "steel_air_surface",
            physvol1 = "air_in_steel",
            physvol2 = "air_in_steel")


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
