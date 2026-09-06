#!/usr/bin/env python3
"""
DIAGNOSTICS for the Golden horizon calculation.

Answers the six review questions with measurements rather than assurances.
Run after goldensun.py, so the elevation tiles are already cached in ./dem.

    py diagnostics.py

Writes skyline_full.csv (720 rows) and skyline_fine.csv, and prints everything
else to the screen. Paste the screen output back.
"""

import hashlib
import math
import os
from pathlib import Path

import numpy as np

import horizon as hz
import goldensun as g
from solarpos import sun_position

LAT, LON = g.LAT, g.LON
R = hz.EARTH_R

# Write the CSVs beside this script, not into whatever folder the terminal is
# sitting in, for the same reason the tile cache is anchored.
OUT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------- 1. provenance
def provenance():
    print("=" * 72)
    print("1. DATASET PROVENANCE AND VOID TREATMENT")
    print("=" * 72)
    print(f"Source URL pattern: {hz.TILE_URL}")
    print("This is the AWS/Mapzen Terrain Tiles 'skadi' collection, NOT raw SRTM.")
    print()
    total_void = 0
    for name in sorted(os.listdir(hz.DEM_DIR)):
        if not name.endswith(".hgt"):
            continue
        path = os.path.join(hz.DEM_DIR, name)
        raw = open(path, "rb").read()
        side = int(round(math.sqrt(len(raw) / 2)))
        arr = np.frombuffer(raw, dtype=">i2").reshape(side, side)
        voids = int((arr <= -1000).sum())
        total_void += voids
        print(f"  {name:14s} {len(raw):>10,} bytes  {side} x {side}  "
              f"sha256 {hashlib.sha256(raw).hexdigest()[:16]}")
        print(f"  {'':14s} voids: {voids:,} of {arr.size:,} "
              f"({100*voids/arr.size:.4f}%)   "
              f"range {arr[arr>-1000].min()} to {arr.max()} m")
    print(f"\n  TOTAL VOIDS ACROSS MOSAIC: {total_void:,}")
    print("  Treatment: voids are set to NaN and then SKIPPED along each ray.")
    print("  They are NOT interpolated or filled. A void on a ridge therefore")
    print("  LOWERS the computed horizon, biasing the terrain effect DOWN.")


# ------------------------------------------------------------ 2. observer point
def observer(grid, lat0, lon0, step):
    print()
    print("=" * 72)
    print("2. OBSERVER GROUND ELEVATION")
    print("=" * 72)
    base = float(hz.sample(grid, lat0, lon0, step,
                           np.array([LAT]), np.array([LON]))[0])
    print(f"  Point: {LAT} N, {LON} E")
    print(f"  DEM elevation at that point (bilinear): {base:.1f} m")
    print(f"  Observer eye height added:              "
          f"{hz.OBSERVER_HEIGHT_M:.1f} m")
    print(f"  Sightline origin used:                  "
          f"{base + hz.OBSERVER_HEIGHT_M:.1f} m")
    print("  Source: the DEM itself. NOT a surveyed or published elevation.")

    # near-field spread, which is where canopy and buildings sit
    for rad_m in (50, 100, 250, 500):
        d = rad_m / 111_320.0
        las = np.linspace(LAT - d, LAT + d, 21)
        los = np.linspace(LON - d / math.cos(math.radians(LAT)),
                          LON + d / math.cos(math.radians(LAT)), 21)
        LA, LO = np.meshgrid(las, los)
        v = hz.sample(grid, lat0, lon0, step, LA.ravel(), LO.ravel())
        v = v[np.isfinite(v)]
        print(f"  Within {rad_m:4d} m: min {v.min():7.1f}  mean {v.mean():7.1f}  "
              f"max {v.max():7.1f}  spread {v.max()-v.min():5.1f} m")
    print("  A large near-field spread suggests canopy or structures in the")
    print("  surface model at or beside the observer, which raises the origin")
    print("  and makes ridges look LOWER than they are.")
    return base


# ------------------------------------------- 3. sampling geometry: flat vs geodesic
def ray_points(lat, lon, az_deg, dists, geodesic):
    """Return (lat, lon) arrays along a bearing, either planar or on a sphere."""
    if not geodesic:
        # the approximation used in horizon.py: fixed metres-per-degree,
        # longitude scale frozen at the OBSERVER's latitude
        rad = math.radians(az_deg)
        m_lat = 111_320.0
        m_lon = 111_320.0 * math.cos(math.radians(lat))
        return (lat + dists * math.cos(rad) / m_lat,
                lon + dists * math.sin(rad) / m_lon)
    # proper spherical forward geodesic
    th = math.radians(az_deg)
    p1, l1 = math.radians(lat), math.radians(lon)
    d = dists / R
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * math.cos(th))
    l2 = l1 + np.arctan2(math.sin(th) * np.sin(d) * np.cos(p1),
                         np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), np.degrees(l2)


def horizon_arc(grid, lat0, lon0, step, base, azimuths,
                radius_km=60.0, ray_step_m=40.0, geodesic=False):
    dists = np.arange(ray_step_m, radius_km * 1000, ray_step_m)
    drop = dists ** 2 * (1 - hz.REFRACTION_K) / (2 * R)
    out = np.zeros(len(azimuths))
    for i, az in enumerate(azimuths):
        la, lo = ray_points(LAT, LON, az, dists, geodesic)
        el = hz.sample(grid, lat0, lon0, step, la, lo)
        ang = np.degrees(np.arctan2(el - base - drop, dists))
        ang = ang[np.isfinite(ang)]
        out[i] = max(0.0, float(ang.max())) if ang.size else 0.0
    return out


def geometry_checks(grid, lat0, lon0, step, base):
    print()
    print("=" * 72)
    print("3. SAMPLING GEOMETRY AND TILE SEAMS")
    print("=" * 72)
    print(f"  Grid origin: row 0 at lat {lat0}, col 0 at lon {lon0}")
    print(f"  Spacing: {step:.10f} deg = {step*3600:.1f} arc-second")
    print(f"  Grid shape: {grid.shape[0]} x {grid.shape[1]}")
    print("  Seam handling: each 3601x3601 tile is trimmed to 3600x3600 by")
    print("  dropping its LAST row and LAST column before stacking, which")
    print("  removes the shared edge. Consequence: the southern-most and")
    print("  eastern-most 1-arc-second strip of the mosaic is absent.")
    print()
    print("  Positional error of the planar ray approximation vs a true geodesic:")
    dists = np.array([10_000.0, 30_000.0, 60_000.0])
    worst = 0.0
    for az in (0, 45, 90, 135, 180, 225, 270, 315):
        fa, fo = ray_points(LAT, LON, az, dists, False)
        ga, go = ray_points(LAT, LON, az, dists, True)
        dy = (fa - ga) * 111_320.0
        dx = (fo - go) * 111_320.0 * math.cos(math.radians(LAT))
        err = np.hypot(dx, dy)
        worst = max(worst, err.max())
        print(f"    bearing {az:3d}:  at 10 km {err[0]:6.0f} m   "
              f"30 km {err[1]:6.0f} m   60 km {err[2]:6.0f} m")
    print(f"  Worst positional error at 60 km: {worst:.0f} m")

    print()
    print("  Effect on the horizon angle, planar vs geodesic, over the arcs")
    print("  the sun actually uses on 21 Dec:")
    for lo_a, hi_a, lab in ((120, 150, "morning crossing"),
                            (200, 240, "afternoon crossing")):
        azs = np.arange(lo_a, hi_a + 0.5, 0.5)
        a_flat = horizon_arc(grid, lat0, lon0, step, base, azs, geodesic=False)
        a_geo = horizon_arc(grid, lat0, lon0, step, base, azs, geodesic=True)
        d = np.abs(a_flat - a_geo)
        print(f"    {lab:20s} max |diff| {d.max():.3f} deg, "
              f"mean {d.mean():.3f} deg")


# --------------------------------------------------- 4 & 5. the table, finer rays
def horizon_tables(grid, lat0, lon0, step, base):
    print()
    print("=" * 72)
    print("4. FULL HORIZON TABLE (written to skyline_full.csv)")
    print("=" * 72)
    azs = np.arange(0.0, 360.0, 0.5)
    coarse = horizon_arc(grid, lat0, lon0, step, base, azs)
    np.savetxt(OUT_DIR / "skyline_full.csv", np.c_[azs, coarse], delimiter=",",
               header="bearing_deg,horizon_deg", comments="", fmt="%.4f")
    print(f"  720 rows written. Max {coarse.max():.2f} deg at "
          f"{azs[coarse.argmax()]:.1f} deg.")
    print()
    print("  Near the two bearings the sun actually crosses on 21 Dec:")
    for lo_a, hi_a, lab in ((132, 143, "sun on, az ~137"),
                            (211, 222, "sun off, az ~216")):
        print(f"    {lab}")
        sel = (azs >= lo_a) & (azs <= hi_a)
        for a, v in zip(azs[sel], coarse[sel]):
            print(f"      {a:6.1f}   {v:6.2f}")

    print()
    print("=" * 72)
    print("5. ANGULAR AND RADIAL SAMPLING SENSITIVITY")
    print("=" * 72)
    for lo_a, hi_a, lab in ((120, 150, "morning arc"), (200, 240, "afternoon arc")):
        fine_az = np.arange(lo_a, hi_a + 0.05, 0.05)
        fine = horizon_arc(grid, lat0, lon0, step, base, fine_az)
        interp = np.interp(fine_az, azs, coarse, period=360.0)
        d = fine - interp
        print(f"  {lab} ({lo_a}-{hi_a} deg), 0.05 deg rays vs 0.5 deg interpolated:")
        print(f"    max under-estimate by coarse: {d.max():+.3f} deg "
              f"at {fine_az[d.argmax()]:.2f}")
        print(f"    max over-estimate  by coarse: {d.min():+.3f} deg "
              f"at {fine_az[d.argmin()]:.2f}")
        print(f"    RMS difference: {np.sqrt((d**2).mean()):.3f} deg")
        np.savetxt(OUT_DIR / f"skyline_fine_{lo_a}_{hi_a}.csv",
                   np.c_[fine_az, fine], delimiter=",",
                   header="bearing_deg,horizon_deg", comments="", fmt="%.4f")

        c40 = horizon_arc(grid, lat0, lon0, step, base,
                          np.arange(lo_a, hi_a + 0.5, 0.5), ray_step_m=40.0)
        c15 = horizon_arc(grid, lat0, lon0, step, base,
                          np.arange(lo_a, hi_a + 0.5, 0.5), ray_step_m=15.0)
        print(f"    ray step 40 m vs 15 m: max |diff| "
              f"{np.abs(c40-c15).max():.3f} deg")
    return azs, coarse


# ------------------------------------------------ 6. sensitivity of the headline
def sensitivity(azs, coarse):
    print()
    print("=" * 72)
    print("6. HOW MUCH THE HEADLINE TIMES MOVE")
    print("=" * 72)
    import datetime as dt

    def times(profile, tz):
        vis = []
        t = dt.datetime(2026, 12, 21) - dt.timedelta(hours=tz)
        for _ in range(24 * 60):
            alt, az = sun_position(t, LAT, LON)
            if alt > np.interp(az % 360, azs, profile, period=360.0):
                vis.append(t + dt.timedelta(hours=tz))
            t += dt.timedelta(minutes=1)
        return (vis[0].strftime("%H:%M"), vis[-1].strftime("%H:%M"),
                len(vis) / 60) if vis else ("--", "--", 0)

    print("  21 December 2026, standard time (UTC-7):")
    print(f"    as published                 {times(coarse, -7)}")
    for shift, lab in ((+0.25, "horizon +0.25 deg"), (-0.25, "horizon -0.25 deg"),
                       (+1.0, "horizon +1.0 deg"), (-1.0, "horizon -1.0 deg")):
        print(f"    {lab:28s} {times(np.clip(coarse + shift, 0, None), -7)}")
    print("  A 0.25 deg error in the skyline is worth roughly the difference")
    print("  shown above; compare that against the sampling differences in")
    print("  section 5 to judge whether 0.5 deg rays are fine enough.")


if __name__ == "__main__":
    print("Loading cached elevation mosaic...")
    grid, lat0, lon0, step = hz.load_mosaic(LAT, LON, 60.0)
    provenance()
    base = observer(grid, lat0, lon0, step)
    geometry_checks(grid, lat0, lon0, step, base)
    azs, coarse = horizon_tables(grid, lat0, lon0, step, base)
    sensitivity(azs, coarse)
    print("\nDone. Files written: skyline_full.csv, skyline_fine_*.csv")
