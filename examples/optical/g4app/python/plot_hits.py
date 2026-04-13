"""
plot_hits.py — Visualize PMT hits and optical-photon trajectories.

Reads:
  hits.csv          (required) — one row per PMT detection from optical_g4
  trajectories.csv  (optional) — one row per trajectory point

Reads geometry from a GDML file to draw detector wireframes.

Usage:
  python plot_hits.py [options]

  --hits PATH   path to hits.csv           (default: hits.csv)
  --traj PATH   path to trajectories.csv   (default: trajectories.csv)
  --gdml PATH   path to optical_prism.gdml (default: ../../optical_prism.gdml)
  --out  PATH   save to PNG instead of displaying interactively

Example:
  # From g4app/build/ after running ./optical_g4:
  python ../python/plot_hits.py --out hits.png

  # With trajectories:
  python ../python/plot_hits.py --traj trajectories.csv --out traj.png
"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend; overridden below if --show
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3d projection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from lxml import etree


# ---------------------------------------------------------------------------
# GDML geometry helpers
# ---------------------------------------------------------------------------

def _parse_unit_scale(lunit: str) -> float:
    """Return a scale factor to convert lunit values to cm."""
    lunit = lunit.lower()
    if lunit == "cm":  return 1.0
    if lunit == "mm":  return 0.1
    if lunit == "m":   return 100.0
    return 1.0  # fallback


def parse_box(gdml_path: str, name: str) -> tuple[float, float, float]:
    """Return (hx, hy, hz) half-sizes in cm for the named <box> solid.

    GDML x/y/z attributes are *full* sizes; we divide by 2.
    """
    tree = etree.parse(gdml_path)
    for box in tree.iterfind(".//solids/box"):
        if box.get("name") == name:
            scale = _parse_unit_scale(box.get("lunit", "cm"))
            hx = float(box.get("x")) * scale / 2.0
            hy = float(box.get("y")) * scale / 2.0
            hz = float(box.get("z")) * scale / 2.0
            return hx, hy, hz
    raise KeyError(f"Box solid '{name}' not found in {gdml_path}")


def parse_xtru(gdml_path: str, name: str):
    """Return (vertices_xy, z_min_cm, z_max_cm) for the named <xtru> solid.

    vertices_xy : list of (x_cm, y_cm) pairs — the 2-D polygon cross-section.
    """
    tree = etree.parse(gdml_path)
    for xtru in tree.iterfind(".//solids/xtru"):
        if xtru.get("name") != name:
            continue
        scale = _parse_unit_scale(xtru.get("lunit", "cm"))
        verts = []
        for v in xtru.findall("twoDimVertex"):
            verts.append((float(v.get("x")) * scale,
                          float(v.get("y")) * scale))
        sections = xtru.findall("section")
        z_vals = [float(s.get("zPosition")) * scale for s in sections]
        return verts, min(z_vals), max(z_vals)
    raise KeyError(f"Xtru solid '{name}' not found in {gdml_path}")


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _box_edges(hx: float, hy: float, hz: float):
    """Yield (p1, p2) line segments for the 12 edges of a box."""
    corners = [(sx * hx, sy * hy, sz * hz)
               for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    # Edges along each axis
    for i in range(8):
        x, y, z = corners[i]
        for dx, dy, dz in [(2*hx, 0, 0), (0, 2*hy, 0), (0, 0, 2*hz)]:
            j_xyz = (x + dx, y + dy, z + dz)
            # Only yield if j_xyz is also a corner (avoids duplicates)
            if tuple(j_xyz) in set(corners):
                yield corners[i], j_xyz


def box_wireframe(ax, hx: float, hy: float, hz: float,
                  color='grey', alpha=0.5, linewidth=0.8):
    """Draw a box wireframe centred at origin."""
    # Build all 12 edges explicitly:
    pts = [(-hx,-hy,-hz), ( hx,-hy,-hz), ( hx, hy,-hz), (-hx, hy,-hz),
           (-hx,-hy, hz), ( hx,-hy, hz), ( hx, hy, hz), (-hx, hy, hz)]
    edges = [(0,1),(1,2),(2,3),(3,0),   # bottom face
             (4,5),(5,6),(6,7),(7,4),   # top face
             (0,4),(1,5),(2,6),(3,7)]   # verticals
    segs = [(pts[a], pts[b]) for a, b in edges]
    lc = Line3DCollection(segs, colors=color, alpha=alpha, linewidths=linewidth)
    ax.add_collection3d(lc)


def prism_wireframe(ax, gdml_path: str, name: str = "glass_prism",
                    color='goldenrod', alpha=0.9, linewidth=1.2):
    """Draw the triangular prism read from the GDML <xtru> solid."""
    verts, z_min, z_max = parse_xtru(gdml_path, name)
    n = len(verts)

    # Bottom and top polygons
    for z in (z_min, z_max):
        for i in range(n):
            x0, y0 = verts[i]
            x1, y1 = verts[(i + 1) % n]
            ax.plot([x0, x1], [y0, y1], [z, z],
                    color=color, alpha=alpha, linewidth=linewidth)

    # Vertical edges
    for x, y in verts:
        ax.plot([x, x], [y, y], [z_min, z_max],
                color=color, alpha=alpha, linewidth=linewidth)


# ---------------------------------------------------------------------------
# Main plotting function
# ---------------------------------------------------------------------------

def plot(hits_csv: str, traj_csv: str | None,
         gdml_path: str, out: str | None, show: bool):

    hits = pd.read_csv(hits_csv)
    print(f"Loaded {len(hits)} hits from {hits_csv}")

    traj_path = Path(traj_csv) if traj_csv else None
    trajs = None
    if traj_path and traj_path.exists() and traj_path.stat().st_size > 0:
        trajs = pd.read_csv(traj_path)
        # Drop the header-only case (0 data rows)
        if len(trajs) == 0:
            trajs = None
        else:
            print(f"Loaded {len(trajs)} trajectory points from {traj_path}")

    # ------------------------------------------------------------------
    # Geometry dimensions from GDML
    # ------------------------------------------------------------------
    steel_half = parse_box(gdml_path, "steel_box")
    air_half   = parse_box(gdml_path, "air_box")

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(10, 8))
    ax  = fig.add_subplot(111, projection='3d')

    box_wireframe(ax, *steel_half, color='#888888', alpha=0.25, linewidth=0.6)
    box_wireframe(ax, *air_half,   color='steelblue', alpha=0.45, linewidth=0.8)
    prism_wireframe(ax, gdml_path)

    # ------------------------------------------------------------------
    # Trajectories (faint poly-lines, one per track)
    # ------------------------------------------------------------------
    if trajs is not None:
        rng = np.random.default_rng(42)
        for (evid, tid), grp in trajs.groupby(["event_id", "track_id"]):
            grp = grp.sort_values("point_idx")
            c = rng.random(3) * 0.6 + 0.2   # avoid very dark/light colours
            ax.plot(grp.x_cm.values,
                    grp.y_cm.values,
                    grp.z_cm.values,
                    color=c, lw=0.4, alpha=0.25)

    # ------------------------------------------------------------------
    # PMT hits — scatter coloured by arrival time
    # ------------------------------------------------------------------
    sc = ax.scatter(hits.x_cm, hits.y_cm, hits.z_cm,
                    c=hits.t_ns, cmap='viridis',
                    s=10, depthshade=True, zorder=5)
    cbar = fig.colorbar(sc, ax=ax, shrink=0.6, pad=0.1)
    cbar.set_label("arrival time [ns]")

    # ------------------------------------------------------------------
    # Labels
    # ------------------------------------------------------------------
    ax.set_xlabel("x [cm]")
    ax.set_ylabel("y [cm]")
    ax.set_zlabel("z [cm]")
    ax.set_title(f"{len(hits)} PMT hits"
                 + (f", {len(trajs)} traj. points" if trajs is not None else ""))

    # Equal-ish aspect ratio
    hmax = max(steel_half)
    ax.set_xlim(-hmax, hmax)
    ax.set_ylim(-hmax, hmax)
    ax.set_zlim(-hmax, hmax)

    plt.tight_layout()

    if out:
        plt.savefig(out, dpi=150, bbox_inches='tight')
        print(f"Saved {out}")
    if show:
        matplotlib.use("TkAgg")   # switch to interactive
        plt.show()

    plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Plot PMT hits and optical-photon trajectories in 3D.")
    ap.add_argument("--hits", default="hits.csv",
                    help="CSV file produced by optical_g4 (default: hits.csv)")
    ap.add_argument("--traj", default="trajectories.csv",
                    help="Trajectory CSV file (default: trajectories.csv; "
                         "skip if absent)")
    ap.add_argument("--gdml", default="../../optical_prism.gdml",
                    help="GDML file for geometry wireframes "
                         "(default: ../../optical_prism.gdml)")
    ap.add_argument("--out", default=None,
                    help="Save to PNG at this path (default: display "
                         "interactively)")
    ap.add_argument("--show", action="store_true",
                    help="Also show interactively even when --out is given")
    args = ap.parse_args()

    if not Path(args.hits).exists():
        ap.error(f"hits file not found: {args.hits}")

    plot(args.hits, args.traj, args.gdml,
         out=args.out, show=args.show)


if __name__ == "__main__":
    main()
