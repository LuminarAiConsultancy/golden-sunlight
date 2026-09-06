"""
Build a HORIZON PROFILE for a point on the ground.

The idea in one sentence: stand at the townsite, turn slowly through all 360
degrees of the compass, and for each bearing record how high above level you
have to look before you clear the highest ridge in that direction.

The result is a lookup table: bearing -> horizon angle in degrees. On a flat
prairie every entry is 0. In the Columbia Valley some entries will be many
degrees, and that is exactly the gap between almanac sunrise and real sunrise.
"""

import gzip
import math
import os
import urllib.request

import numpy as np

EARTH_R = 6_371_000.0     # mean radius, metres
REFRACTION_K = 0.13       # standard atmospheric refraction coefficient

# Public, no-login mirror of 1-arc-second (~30 m) SRTM tiles, gzipped .hgt.
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/skadi/{ns}/{name}.hgt.gz"


# ---------------------------------------------------------------------------
# Loading elevation data
# ---------------------------------------------------------------------------

def tile_name(lat: float, lon: float) -> str:
    """SRTM tiles are named for their SOUTH-WEST corner, e.g. N51W117."""
    la, lo = math.floor(lat), math.floor(lon)
    return f"{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}"


def fetch_tile(name: str, cache_dir: str = "dem") -> str:
    """Download one .hgt tile if we do not already have it. Returns the path."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, name + ".hgt")
    if os.path.exists(path):
        return path
    url = TILE_URL.format(ns=name[:3], name=name)
    print(f"  downloading {name} ...")
    with urllib.request.urlopen(url, timeout=120) as resp:
        raw = gzip.decompress(resp.read())
    with open(path, "wb") as fh:
        fh.write(raw)
    return path


def load_mosaic(lat: float, lon: float, radius_km: float, cache_dir: str = "dem"):
    """Stitch together every tile we need to see `radius_km` in all directions.

    Returns (grid, lat0, lon0, step) where grid[row, col] is metres above sea
    level, row 0 is the NORTH edge, and step is the grid spacing in degrees.
    """
    # How far the radius reaches in degrees. Longitude degrees shrink as you
    # go north, hence the cos(lat).
    dlat = radius_km / 111.32
    dlon = radius_km / (111.32 * math.cos(math.radians(lat)))

    lat_lo, lat_hi = math.floor(lat - dlat), math.floor(lat + dlat)
    lon_lo, lon_hi = math.floor(lon - dlon), math.floor(lon + dlon)

    tiles, size = {}, None
    for la in range(lat_lo, lat_hi + 1):
        for lo in range(lon_lo, lon_hi + 1):
            name = tile_name(la + 0.5, lo + 0.5)
            path = fetch_tile(name, cache_dir)
            n_bytes = os.path.getsize(path)
            side = int(round(math.sqrt(n_bytes / 2)))   # 3601 for 1", 1201 for 3"
            arr = np.fromfile(path, dtype=">i2").reshape(side, side).astype(np.float32)
            arr[arr < -1000] = np.nan                   # SRTM voids
            tiles[(la, lo)] = arr
            size = side

    # Tiles overlap by one row/column on each shared edge; trim then stack.
    rows = []
    for la in range(lat_hi, lat_lo - 1, -1):            # north to south
        row = [tiles[(la, lo)][:-1, :-1] for lo in range(lon_lo, lon_hi + 1)]
        rows.append(np.hstack(row))
    grid = np.vstack(rows)

    step = 1.0 / (size - 1)
    lat0 = lat_hi + 1.0          # latitude of grid row 0 (north edge)
    lon0 = float(lon_lo)         # longitude of grid col 0 (west edge)
    return grid, lat0, lon0, step


def sample(grid, lat0, lon0, step, lats, lons):
    """Bilinear lookup of elevation at arbitrary lat/lon arrays."""
    fr = (lat0 - lats) / step
    fc = (lons - lon0) / step
    r0, c0 = np.floor(fr).astype(int), np.floor(fc).astype(int)
    dr, dc = fr - r0, fc - c0
    r0 = np.clip(r0, 0, grid.shape[0] - 2)
    c0 = np.clip(c0, 0, grid.shape[1] - 2)
    return ((grid[r0,     c0    ] * (1 - dr) * (1 - dc)) +
            (grid[r0 + 1, c0    ] * dr       * (1 - dc)) +
            (grid[r0,     c0 + 1] * (1 - dr) * dc)       +
            (grid[r0 + 1, c0 + 1] * dr       * dc))


# ---------------------------------------------------------------------------
# The horizon calculation itself
# ---------------------------------------------------------------------------

def horizon_profile(grid, lat0, lon0, step, lat, lon,
                    observer_height=1.6, radius_km=60.0,
                    az_step=0.5, ray_step_m=40.0):
    """For every compass bearing, find the highest apparent ridge angle.

    observer_height: eye level above ground, metres.
    radius_km:       how far out to look. 60 km is generous; beyond that,
                     Earth's curvature drops terrain below the sightline anyway.
    """
    base = float(sample(grid, lat0, lon0, step,
                        np.array([lat]), np.array([lon]))[0]) + observer_height

    dists = np.arange(ray_step_m, radius_km * 1000, ray_step_m)
    # Curvature + refraction: how far a distant point sinks below a straight
    # sightline. Refraction bends light down slightly, partly cancelling it.
    drop = dists ** 2 * (1 - REFRACTION_K) / (2 * EARTH_R)

    m_per_deg_lat = 111_320.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))

    azimuths = np.arange(0.0, 360.0, az_step)
    angles = np.zeros_like(azimuths)

    for i, az in enumerate(azimuths):
        rad = math.radians(az)
        pt_lat = lat + (dists * math.cos(rad)) / m_per_deg_lat
        pt_lon = lon + (dists * math.sin(rad)) / m_per_deg_lon
        elev = sample(grid, lat0, lon0, step, pt_lat, pt_lon)
        # Apparent angle of each point along the ray, seen from the observer.
        ang = np.degrees(np.arctan2(elev - base - drop, dists))
        ang = ang[np.isfinite(ang)]
        angles[i] = max(0.0, float(np.max(ang))) if ang.size else 0.0

    return azimuths, angles


def angle_at(azimuths, angles, az):
    """Horizon angle at any bearing, linearly interpolated, wrapping at 360."""
    return float(np.interp(az % 360, azimuths, angles,
                           period=360.0))
