# Response to technical review
### Golden daylight calculation, 4 September 2026

Answers to all six points. Two are corrections to the published report, which has
been reissued. Three require a diagnostic run to answer with numbers rather than
description, and `diagnostics.py` does that. One is answered in full below.

---

## 1. Elevation dataset, version, tiles, and missing values

**Correction. The report said "1 arc-second SRTM". That was imprecise.**

The data was fetched from `https://s3.amazonaws.com/elevation-tiles-prod/skadi/`,
which is the AWS Terrain Tiles collection (originally Mapzen), distributed in `.hgt`
format. It is SRTM-derived and void-filled at this latitude, but it is a composite
product, not raw SRTMGL1. Anyone reproducing this should use the same source rather
than assuming an unmodified SRTM tile will match.

**Tiles used:** N50W117, N50W118, N51W117, N51W118. Four tiles, each 3601 x 3601
16-bit big-endian signed integers, mosaicked to 7200 x 7200. The diagnostic run prints
the exact byte count and a SHA-256 for each file so the specific tiles can be pinned.

**Void treatment, and this matters.** The loader sets any sample below −1000 m to NaN,
and the ray tracer then drops non-finite samples before taking the maximum. Voids are
**skipped, not filled**. If a void sits on a ridgeline, that ridge is invisible to the
calculation and the horizon comes out too low. So this treatment biases the terrain
effect **downward**, not upward.

The dataset is void-filled, so the count is probably zero, but I did not verify it and
should have. The diagnostic prints the exact void count per tile.

## 2. Observer ground elevation

Taken from the DEM itself: a bilinear interpolation of the four surrounding grid points
at 51.2969 N, 116.9647 W, plus 1.6 m of eye height. It is not a surveyed elevation and
not a published figure.

**Correction. The report describes the townsite as "about 785 metres". That number came
from general knowledge of Golden, not from the DEM, and it was never checked against
what the calculation actually used.** The diagnostic prints the value the code used. If
the two disagree materially, the report's descriptive sentence needs fixing.

The reviewer's point about direction of bias is correct and I had it wrong. The
diagnostic also prints the elevation spread within 50, 100, 250 and 500 m of the
observer. A large spread at short range indicates canopy or structures in the surface
model at the viewpoint, which raises the sightline origin and makes every ridge appear
lower. That runs opposite to the canopy-on-ridges bias.

## 3. Raster coordinates, tile seams, and along-bearing sampling

**Coordinates.** Row 0 of the mosaic is the north edge, at latitude `floor(lat)+1` of
the northernmost tile. Column 0 is the west edge, at `floor(lon)` of the westernmost.
Spacing is 1/3600 degree. Lookup is bilinear on the four surrounding posts.

**Seams.** Adjacent `.hgt` tiles share an edge row and column. Each tile is trimmed to
3600 x 3600 by discarding its last row and last column before stacking north to south
and west to east. This removes the duplication correctly. One consequence worth stating:
the southernmost and easternmost one-arc-second strip of the whole mosaic is absent.
At 60 km from the observer that is immaterial, but it is a real edge condition.

**Along-bearing sampling, and this is the weakest part of the method.** Sample points
are placed using a planar approximation:

    lat_i = lat + (d_i * cos(azimuth)) / 111320
    lon_i = lon + (d_i * sin(azimuth)) / (111320 * cos(lat_observer))

The metres-per-degree-of-longitude scale is computed once at the **observer's** latitude
and held constant along the entire ray. Over 60 km the latitude changes by up to 0.54
degrees and that scale drifts by about 1.3 percent. Measured against a proper spherical
forward geodesic, the positional error at 60 km is:

| Bearing | Error at 60 km |
|---|---|
| 0 or 180 (north/south) | 67 m |
| 45 (diagonal) | 424 m |
| 90 or 270 (east/west) | 359 m |

So a ray thinks it is looking at one point and is actually reading the terrain up to
about 400 m to one side. For a *maximum over a long ray through a continuous mountain
range* this mostly changes which part of the ridge is sampled rather than the height of
the envelope, but that is an argument, not a measurement. The diagnostic recomputes the
horizon over both crossing arcs using a correct geodesic and reports the difference in
degrees. If it is small, the approximation stands. If not, the fix is to switch
`ray_points` to the geodesic form, which is already written.

## 4. The full horizon table, and the bearings that actually matter

**The eight-point summary published in the report must not be interpolated to
reconstruct the profile.** It was a visual summary, not a dataset. `diagnostics.py`
writes the full 720-row table to `skyline_full.csv`.

**A correction to my own framing.** I drew attention to the 12.2 degree maximum at
bearing 240. That peak is nearly irrelevant to the solstice result, because the sun
never gets there. On 21 December 2026 at Golden the sun's azimuth runs from about 126
degrees at first light to about 231 degrees at last light, peaking at only 15.3 degrees
altitude due south. The two bearings that decide the published times are:

| Event | Time (MST) | Solar azimuth | Solar altitude at crossing |
|---|---|---|---|
| Sun on | 9:35 am | 137.1 deg | 4.50 deg |
| Sun off | 3:26 pm | 216.5 deg | 7.55 deg |

So the horizon values that carry the entire result are those near **137 degrees** and
**216 degrees**. The diagnostic prints every 0.5-degree entry across 132 to 143 and 211
to 222 so those two bands can be inspected directly.

Note also what this shows: the afternoon loss is larger than the morning loss (73 versus
42 minutes) because the south-western skyline stands about 7.5 degrees high where the
sun sets, against about 4.5 degrees in the south-east where it rises. That is a terrain
asymmetry, not a property of the clock.

## 5. Angular and radial sampling

The concern is correct in principle. At 0.5-degree spacing, adjacent rays are 524 m
apart at 60 km, 87 m at 10 km, and 9 m at 1 km. A narrow notch or spire between two rays
is invisible, and linear interpolation between bearings smooths any spike that is
narrower than the sampling interval. Radially, the 40 m step is coarser than the roughly
30 m grid posting, so some cells along each ray are stepped over.

Rather than argue about it, the diagnostic measures it. Over both crossing arcs it
recomputes the horizon at **0.05 degrees**, a factor of ten finer, and reports the
maximum and RMS difference against the interpolated 0.5-degree profile. It separately
recomputes at a 15 m radial step and reports the difference against 40 m.

It then converts that into the only unit that matters, by recomputing the 21 December
times with the horizon shifted by 0.25 and 1.0 degrees. That gives a direct answer to
"is 0.5 degrees fine enough": compare the measured sampling error against the shift
needed to move the published times by a minute.

## 6. Equation of time, in full, and the years

**Correction. The report did not state its years.** The solstice figures are for
**21 December 2026**. The other six dates in the year table are **2027**: 15 January,
1 February, 20 March, 21 June, 22 September, 15 November. All annual day-counts are for
calendar year **2027**, which is not a leap year, so the denominator is 365. Both the
web and Word versions have been reissued with this stated.

**The equation of time.** With `t` in Julian centuries since J2000.0, `L0` the geometric
mean longitude and `M` the geometric mean anomaly (both in degrees, converted to radians
as `gml` and `gma`), and `eps` the corrected obliquity in radians:

    var_y = tan(eps / 2)^2

    ecc   = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)

    EoT (minutes) = 4 * degrees(
                        var_y * sin(2 * gml)
                      - 2 * ecc * sin(gma)
                      + 4 * ecc * var_y * sin(gma) * cos(2 * gml)
                      - 0.5 * var_y^2 * sin(4 * gml)
                      - 1.25 * ecc^2 * sin(2 * gma)
                    )

This is the NOAA spreadsheet formulation. It is then applied as:

    true_solar_minutes = (UTC_minutes + EoT + 4 * longitude_degrees) mod 1440
    hour_angle_degrees = true_solar_minutes / 4 - 180

with longitude negative west of Greenwich.

---

## What has changed in the published report

1. The dataset is now named as AWS Terrain Tiles rather than SRTM.
2. The bias statement is rewritten. It previously said the surface model makes ridges
   too tall and therefore overstates the effect. That was one-sided and unsupportable.
   It now states that ridge canopy overstates the effect, canopy or structures at the
   observation point understate it, obstructions closer than about thirty metres are
   absent entirely, and the net direction has not been established.
3. Years are now stated explicitly.

## What is still unverified

The observer elevation the code actually used, the void count, the geodesic sensitivity,
and the fine-sampling sensitivity. All four come out of one diagnostic run against the
already-cached tiles. Until that is done, the published times should be treated as
having an unquantified uncertainty, not as settled to the minute.

To run it, in PowerShell on the laptop, from the folder holding the scripts and the
`dem` cache:

    C:\Python314\python.exe diagnostics.py

Expect several minutes, most of it in the 0.05-degree arcs.
