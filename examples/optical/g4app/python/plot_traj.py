"""plot_traj.py — draw optical-photon trajectories coloured by wavelength.

Each track in trajectories.csv is drawn as a poly-line through the detector.
The line colour matches the perceived colour of the photon's wavelength:
  ~700 nm → red, ~580 nm → yellow, ~520 nm → green,
  ~450 nm → blue, ~400 nm → violet.
Photons outside the visible range (< 380 nm or > 700 nm) are clamped to the
nearest visible colour.

Detector wireframes (water box, glass prism) are drawn in grey / gold for
spatial context.

Views
-----
  3d    : interactive 3-D scene (default)
  dsotm : 2-D XY projection with black background — recreates the
          "Dark Side Of The Moon" (Pink Floyd) album-cover aesthetic.
          Use with dsotm.mac output.

Usage
-----
    python plot_traj.py [--traj trajectories.csv] [--gdml optical_prism.gdml]
                        [--out traj.png] [--show] [--max-tracks N]
                        [--view {3d,dsotm}]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   # noqa: F401 — registers 3-D projection
from lxml import etree


# ---------------------------------------------------------------------------
# Wavelength → RGB colour
# ---------------------------------------------------------------------------

def _wl_to_rgb(wl_nm: float) -> tuple[float, float, float]:
    """Approximate sRGB colour for a monochromatic wavelength in nm.

    Based on the algorithm by Dan Bruton (physics.sfasu.edu/astro/color).
    Returns (r, g, b) each in [0, 1].  Wavelengths outside [380, 700] are
    clamped gracefully rather than returning black.
    """
    wl = float(wl_nm)
    wl = max(380.0, min(700.0, wl))   # clamp to visible

    if 380 <= wl < 440:
        r = -(wl - 440) / 60.0
        g = 0.0
        b = 1.0
    elif 440 <= wl < 490:
        r = 0.0
        g = (wl - 440) / 50.0
        b = 1.0
    elif 490 <= wl < 510:
        r = 0.0
        g = 1.0
        b = -(wl - 510) / 20.0
    elif 510 <= wl < 580:
        r = (wl - 510) / 70.0
        g = 1.0
        b = 0.0
    elif 580 <= wl < 645:
        r = 1.0
        g = -(wl - 645) / 65.0
        b = 0.0
    else:  # 645 <= wl <= 700
        r = 1.0
        g = 0.0
        b = 0.0

    # Intensity roll-off at the edges of the visible range.
    if 380 <= wl < 420:
        factor = 0.3 + 0.7 * (wl - 380) / 40.0
    elif 700 >= wl > 645:
        factor = 0.3 + 0.7 * (700 - wl) / 55.0
    else:
        factor = 1.0

    return (r * factor, g * factor, b * factor)


# ---------------------------------------------------------------------------
# GDML geometry helpers (copied from plot_hits.py so this script is standalone)
# ---------------------------------------------------------------------------

def _parse_box(gdml_path: str, name: str) -> tuple[float, float, float]:
    """Return (hx, hy, hz) half-sizes in cm from a GDML <box> solid."""
    tree = etree.parse(gdml_path)
    for box in tree.findall(".//box"):
        if box.get("name", "").split("0x")[0] == name:
            lunit = box.get("lunit", "mm")
            scale = 10.0 if lunit == "cm" else 1.0   # → mm, then /10 → cm
            scale = 1.0 if lunit == "cm" else 0.1    # keep cm
            hx = float(box.get("x", "0")) * scale / 2.0
            hy = float(box.get("y", "0")) * scale / 2.0
            hz = float(box.get("z", "0")) * scale / 2.0
            return hx, hy, hz
    raise ValueError(f"<box name='{name}'> not found in {gdml_path}")


def _box_wireframe(ax, half: tuple[float, float, float],
                   color: str = "grey", alpha: float = 0.5, lw: float = 0.8):
    """Draw a wireframe box centred on the origin."""
    hx, hy, hz = half
    corners = [
        [-hx, -hy, -hz], [ hx, -hy, -hz], [ hx,  hy, -hz], [-hx,  hy, -hz],
        [-hx, -hy,  hz], [ hx, -hy,  hz], [ hx,  hy,  hz], [-hx,  hy,  hz],
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),   # bottom face
        (4,5),(5,6),(6,7),(7,4),   # top face
        (0,4),(1,5),(2,6),(3,7),   # verticals
    ]
    for i, j in edges:
        xs = [corners[i][0], corners[j][0]]
        ys = [corners[i][1], corners[j][1]]
        zs = [corners[i][2], corners[j][2]]
        ax.plot(xs, ys, zs, color=color, alpha=alpha, lw=lw)


def _parse_xtru(gdml_path: str, name: str
                ) -> tuple[list[tuple[float, float]], list[float]]:
    """Return (vertices_cm, z_extents_cm) for a GDML <xtru> solid."""
    tree = etree.parse(gdml_path)
    for xtru in tree.findall(".//xtru"):
        if xtru.get("name", "").split("0x")[0] == name:
            lunit = xtru.get("lunit", "mm")
            scale = 1.0 if lunit == "cm" else 0.1
            verts = []
            for tv in xtru.findall("twoDimVertex"):
                x = float(tv.get("x", "0")) * scale
                y = float(tv.get("y", "0")) * scale
                verts.append((x, y))
            zs = []
            for sec in xtru.findall("section"):
                zpos = float(sec.get("zPosition", "0")) * scale
                zs.append(zpos)
            return verts, zs
    raise ValueError(f"<xtru name='{name}'> not found in {gdml_path}")


def _prism_wireframe(ax, gdml_path: str,
                     color: str = "goldenrod", alpha: float = 0.9,
                     lw: float = 1.0):
    """Draw the glass prism edges."""
    try:
        verts, zs = _parse_xtru(gdml_path, "glass_prism")
    except ValueError:
        return
    if len(zs) < 2:
        return
    z0, z1 = zs[0], zs[-1]
    n = len(verts)
    # Bottom and top polygon outlines
    for z in (z0, z1):
        xs = [v[0] for v in verts] + [verts[0][0]]
        ys = [v[1] for v in verts] + [verts[0][1]]
        zz = [z] * (n + 1)
        ax.plot(xs, ys, zz, color=color, alpha=alpha, lw=lw)
    # Vertical edges
    for vx, vy in verts:
        ax.plot([vx, vx], [vy, vy], [z0, z1], color=color, alpha=alpha, lw=lw)


# ---------------------------------------------------------------------------
# 3-D view
# ---------------------------------------------------------------------------

def plot_3d(ax, groups, gdml_path: str, alpha: float = 0.55, lw: float = 0.6):
    """Draw trajectories on a 3-D axes."""
    try:
        _box_wireframe(ax, _parse_box(gdml_path, "air_box"),
                       color="steelblue", alpha=0.25, lw=0.7)
    except ValueError:
        pass
    _prism_wireframe(ax, gdml_path, color="goldenrod", alpha=0.8, lw=1.2)

    for (evtID, trkID), grp in groups:
        grp = grp.sort_values("point_idx")
        if len(grp) < 2:
            continue
        wl = float(grp["wavelength_nm"].iloc[0])
        ax.plot(grp["x_cm"].values, grp["y_cm"].values, grp["z_cm"].values,
                color=_wl_to_rgb(wl), lw=lw, alpha=alpha)

    ax.set_xlabel("x [cm]")
    ax.set_ylabel("y [cm]")
    ax.set_zlabel("z [cm]")


# ---------------------------------------------------------------------------
# DSOTM view — 2-D XY projection, black background
# ---------------------------------------------------------------------------

def _prism_outline_2d(ax, gdml_path: str,
                      color: str = "#cccccc", alpha: float = 0.7,
                      lw: float = 1.5):
    """Draw the prism outline (XY projection) on a 2-D axes."""
    try:
        verts, _ = _parse_xtru(gdml_path, "glass_prism")
    except ValueError:
        return
    xs = [v[0] for v in verts] + [verts[0][0]]
    ys = [v[1] for v in verts] + [verts[0][1]]
    ax.plot(xs, ys, color=color, alpha=alpha, lw=lw, zorder=5)


def plot_dsotm(ax, groups, gdml_path: str):
    """Dark-background 2-D XY projection — 'Dark Side Of The Moon' style."""
    # Project every trajectory onto the XY plane (collapse z).
    # Each photon colour should be slightly transparent so overlapping
    # tracks blend naturally into a smooth rainbow band.
    for (evtID, trkID), grp in groups:
        grp = grp.sort_values("point_idx")
        if len(grp) < 2:
            continue
        wl = float(grp["wavelength_nm"].iloc[0])
        color = _wl_to_rgb(wl)
        ax.plot(grp["x_cm"].values, grp["y_cm"].values,
                color=color, lw=1.1, alpha=0.7, zorder=3)

    # Draw the prism outline on top
    _prism_outline_2d(ax, gdml_path)

    ax.set_facecolor("black")
    ax.set_xlabel("x [cm]", color="white")
    ax.set_ylabel("y [cm]", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444444")

    # Zoom in on the prism region; the detector box extends to ±45 cm
    # but the interesting physics (beam + rainbow) is tighter.
    ax.set_xlim(-40, 45)
    ax.set_ylim(-5, 35)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _wavelength_legend(ax, text_color: str = "white"):
    from matplotlib.patches import Patch
    legend_wls = [
        (700, "700 nm  red"),
        (620, "620 nm  orange"),
        (580, "580 nm  yellow"),
        (530, "530 nm  green"),
        (490, "490 nm  cyan"),
        (450, "450 nm  blue"),
        (410, "410 nm  violet"),
    ]
    handles = [Patch(color=_wl_to_rgb(wl), label=lbl)
               for wl, lbl in legend_wls]
    leg = ax.legend(handles=handles, title="wavelength",
                    fontsize=7, title_fontsize=7,
                    facecolor="#111111" if text_color == "white" else "white",
                    labelcolor=text_color,
                    edgecolor="#444444")
    leg.get_title().set_color(text_color)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def plot(traj_csv: str, gdml_path: str, out: str | None,
         show: bool, max_tracks: int | None, view: str):

    trajs = pd.read_csv(traj_csv)
    n_tracks = trajs.groupby(["event_id", "track_id"]).ngroups
    print(f"Loaded {len(trajs)} trajectory points ({n_tracks} tracks) "
          f"from {traj_csv}")

    groups = list(trajs.groupby(["event_id", "track_id"]))
    if max_tracks is not None:
        groups = groups[:max_tracks]

    if view == "dsotm":
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor("black")
        plot_dsotm(ax, groups, gdml_path)
        _wavelength_legend(ax, text_color="white")
        ax.set_title("Dark Side Of The Moon — optical dispersion",
                     color="white", fontsize=11)
        ax.set_aspect("equal")
    else:
        fig = plt.figure(figsize=(11, 9))
        ax = fig.add_subplot(111, projection="3d")
        plot_3d(ax, groups, gdml_path)
        _wavelength_legend(ax)
        ax.set_title(f"{len(groups)} optical photon trajectories")

    plt.tight_layout()
    if out:
        plt.savefig(out, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"Saved {out}")
    if show:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--traj",       default="trajectories.csv",
                    help="trajectory CSV (default: trajectories.csv)")
    ap.add_argument("--gdml",       default="../optical_prism.gdml",
                    help="GDML geometry file (default: ../optical_prism.gdml)")
    ap.add_argument("--out",        default=None,
                    help="output PNG path; if omitted and --show not given, "
                         "saves based on --view")
    ap.add_argument("--show",       action="store_true",
                    help="open interactive matplotlib window")
    ap.add_argument("--max-tracks", type=int, default=None,
                    help="limit to first N tracks (for quick previews)")
    ap.add_argument("--view",       default="3d",
                    choices=["3d", "dsotm"],
                    help="3d: standard 3-D scene; "
                         "dsotm: 2-D XY projection on black background "
                         "(Pink Floyd album-cover style)")
    args = ap.parse_args()

    out = args.out
    if out is None and not args.show:
        out = "dsotm.png" if args.view == "dsotm" else "traj.png"

    plot(args.traj, args.gdml, out=out, show=args.show,
         max_tracks=args.max_tracks, view=args.view)


if __name__ == "__main__":
    main()
