# Golden BC time observance: sunlight, terrain and the clock

Every published sunrise table, almanac and news figure in this debate assumes a flat, unobstructed horizon. Golden does not have one. The town sits on the floor of the Columbia Valley with the Purcells on one side and the Rockies on the other, and on the winter solstice direct sun does not reach the townsite until 45 minutes after the published almanac says the sun has risen. Decisions taken on published times are being taken on numbers that do not describe this place. This repository measures the difference and lets anyone reproduce it.

## What it does and what it found

The project calculates two things the almanac cannot: when direct sunlight actually clears the mountain ridge and reaches the townsite, and when there is enough light outdoors to be seen. It does both under the two clock options in front of council, permanent Mountain Standard at UTC minus 7 and permanent Mountain Daylight at UTC minus 6.

The central result is that the clock does not change how much sunlight Golden gets. It changes which end of the day that sunlight lands on. On the winter solstice the town receives 5 hours and 52 minutes of direct sun under either option. A flat horizon would give 7 hours and 47 minutes; the mountains take the difference, 42 minutes off the morning and 73 minutes off the afternoon. What the clock decides is whether that window opens at 9:35 in the morning or at 10:35. (Comparisons here use this project's own flat-horizon run, 8:53. A published almanac gives 8:50 for the same morning, three minutes earlier for a documented reason set out under Method and assumptions.)

Across the year 2027, counting days when the sun has not cleared the ridge by a given time:

| Sun still behind the ridge at | Standard time | Daylight time |
|---|---|---|
| 8:00 am | 166 days | 201 days |
| 9:00 am | 104 days | 166 days |
| 10:00 am | 0 days | 104 days |

On the other side of the ledger, summer evenings favour daylight time by the same mechanism, and that is reported too rather than left out.

## Quick start

Requires Python 3 and numpy. From the repository folder:

1. `pip install -r requirements.txt`
2. `python goldensun.py --flat`

The second command takes under a second, downloads nothing, and prints a set of PASS or FAIL lines checking the solar calculations against published values from the US Naval Observatory. Run it before anything else. If it fails, nothing downstream is worth reading.

3. `python goldensun.py`

This is the full model with real terrain. **The first run downloads about 51 MB of elevation data, which expands to 104 MB in a `dem` folder beside the scripts.** That happens once. The run itself took 87 seconds on a cold file cache and 52.8 seconds warm, measured on Windows 11 with Python 3.14.2.

4. `python civildawn.py`

Civil dawn and sunrise on a flat horizon, 8.1 seconds, no download.

`python season.py` gives month by month evening tables in 10.7 seconds and also needs no download, because `skyline_full.csv` is committed to the repository deliberately. That file is a generated artifact, but committing it means the summer figures can be reproduced without fetching a hundred megabytes of terrain first.

`python diagnostics.py` runs the full set of provenance and sensitivity measurements in 1.4 seconds, using the cached tiles. It regenerates the three CSV files.

## How to check the work

This is the section that matters. Everything else is output; this is how to decide whether to believe it.

**Start with the self-test.** `python goldensun.py --flat` replaces the mountain horizon with a flat one and checks the result against an outside authority. On a flat horizon the answers must reproduce standard almanac sunrise and sunset, so any disagreement is a defect in the solar arithmetic rather than a fact about terrain. The reference values come from the US Naval Observatory rise, set, transit and twilight API, queried for the same coordinates the model uses, at UTC minus 7 with no daylight saving, retrieved on 6 September 2026. The URL and query format are recorded in `selftest.py` alongside the values, so the query can be repeated.

**Read the deviations, not just the verdict.** The tolerance is 4 minutes, derived as 3 minutes of documented convention difference plus 1 minute of sampling granularity, and it was not tuned to make rows pass. Every row prints its signed deviation. Those deviations should be systematic and one-signed: this code marks sunrise when the sun's centre crosses the horizon while the Naval Observatory marks it when the upper limb does, so every sunrise here must land slightly late and every sunset slightly early, by a similar amount. They do, at plus 1.22 to plus 2.32 minutes for sunrise and minus 1.67 to minus 2.40 for sunset, with a spread of 1.10 minutes. Deviations scattered in sign or size would indicate a real defect that a passing tolerance would hide, and the test asserts against that separately.

**The strongest single check is solar noon.** Transit has no limb convention in it at all, so it is a clean test of the equation of time, which is the part of the solar arithmetic most likely to be wrong. It agrees with the Naval Observatory to within 0.6 minutes on all four test dates.

**Confirm the test can fail.** A test that has never failed is not evidence. Forcing the tolerance to an impossible value produces nine named failures and a non-zero exit code:

```
python -c "import selftest; selftest.TOLERANCE_MIN=0.5; selftest.run_all(2027)"
```

**Check the internal invariants.** `selftest.py` also verifies things that need no external source: that the sun's declination never exceeds the tilt of the Earth's axis, that it passes through zero at both equinoxes, and that on a flat horizon sunrise and sunset are symmetric about solar noon. These catch gross errors independently of whether the reference data was transcribed correctly.

**Check that the terrain calculation is deterministic.** Running `python diagnostics.py` twice regenerates `skyline_full.csv`, `skyline_fine_120_150.csv` and `skyline_fine_200_240.csv` byte for byte identically. Compare with `git status` after a run; if the files are unchanged, the pipeline is reproducible.

**Read the commit history.** It is a record of what changed and what each change cost. Commit messages carry before and after figures where numbers moved, including a case where a 1.6 metre inconsistency between two modules shifted seventeen times by one minute each, and a case where recomputing a headline figure moved it from 87 to 89. The history is the audit trail; the code alone would not tell you that.

**Read `diagnostics.py` output.** It answers, with measurements rather than assurances, what the elevation dataset is, how many voids it contains, what observer elevation was used, how far the planar ray approximation departs from a proper geodesic, how much the 0.5 degree angular sampling smooths the skyline, and how far the headline times move if the whole skyline is shifted by a quarter of a degree.

## Two different questions

The repository contains two calculations that are easy to conflate and must not be.

`goldensun.py` asks **when direct sunlight reaches the town**. It includes terrain. The sun is counted as present when its altitude exceeds the height of the ridge in the direction it happens to be sitting. This is the question behind "how much sun does Golden get".

`civildawn.py` asks **when there is enough light outdoors to see and be seen**. It excludes terrain deliberately. Civil dawn is the moment the sun's centre reaches 6 degrees below the horizon, and it is about scattered light from the whole sky rather than a beam from the sun. Ridges block direct sunlight but they do not stop the sky lighting up, so including terrain here would understate available light.

A reader who takes a `goldensun.py` time as a statement about darkness, or a `civildawn.py` time as a statement about sunshine, will misread both. The two also use different sunrise conventions, for reasons given below.

## Method and assumptions

**Location.** One observation point, 51.2969 degrees north, 116.9647 degrees west, set at `goldensun.py:26` and imported everywhere else so the repository uses a single location. Sun-on times differ across town and differ more on the benches.

**Terrain.** For each of 720 compass bearings, half a degree apart, the code steps outward in 40 metre increments to 60 kilometres, reads the ground elevation, subtracts the amount that point falls below a straight sightline because the Earth curves and the atmosphere bends light, and takes the maximum apparent angle along the ray. Elevation comes from the AWS Terrain Tiles collection at 1 arc-second resolution. Observer eye height is 1.6 metres, at `horizon.py:28`. The refraction coefficient is the standard 0.13, at `horizon.py:27`.

**Why two sunrise conventions.** `goldensun.py` marks the sun as present when its centre clears the skyline. Almanacs mark sunrise when the upper edge of the disc appears, which happens earlier because the edge reaches the horizon before the middle does. The centre is the better test for direct light reaching the ground, which is what that script is about, so it uses the centre deliberately and accepts a difference of 1 to 2 minutes from published tables. `civildawn.py` uses the almanac's upper-limb convention instead, because its figures are meant to be checked against published sunrise tables, and a comparison is only meaningful if both sides define the event the same way. The constant is `solarpos.UPPER_LIMB_DEG`.

This is also why two baselines for the winter solstice appear in discussions of this work and both are correct. Against this project's own flat-horizon run, which marks the centre and gives 8:53, the terrain delay is 42 minutes. Against a published almanac time of 8:50, which marks the upper limb, it is 45. The three-minute gap is the convention and nothing else. The rule this README follows is that it uses **42 where it holds the method constant and isolates the terrain**, which is the comparison that measures the thing being measured, and **45 where it compares against a published table**, which is the comparison that matters to somebody holding an almanac. Every occurrence of either figure names the baseline it is against, and any figure quoted from this work elsewhere should do the same.

**School bell times, and where they came from.** `civildawn.py` counts mornings against the four schools' actual bells rather than an assumed walking time. Each was read from the school's own bell-schedule page on 6 September 2026, and none is inferred from the pattern at the others.

| School | Bell | Classes begin | Source page | Year stated on page |
|---|---|---|---|---|
| Nicholson Elementary | 8:40 | 8:45 | `nes.sd6.bc.ca/about-us/bell-schedule` | not stated |
| Golden Secondary | 8:40 | 8:45 | `gss.sd6.bc.ca/about-us/bell-schedule` | 2026-27 |
| Alexander Park | 8:50 | 8:55 | `apes.sd6.bc.ca/about-us/bell-schedule` | 2025-26 |
| Lady Grey Elementary | 8:53 | 8:58 | `lges.sd6.bc.ca/about-us/bell-schedule` | 2025-26 |

Two of those four pages are headed 2025-26, the previous school year, and one states no year at all. Only Golden Secondary is on record as current. Morning bells rarely move between years, but that is an assumption rather than a check, and it is recorded here rather than buried. The mitigating fact is that the binding case, the earliest bell at 8:40, is also the best-sourced of the four.

A bell is an arrival time, so a count anchored to it measures whether it was dark when a child got to school, not whether it was dark while they walked. `civildawn.py` reports both, and the departure-time figures span a range because nobody has measured when children actually leave.

**Changing the inputs.**

| To change | Edit |
|---|---|
| The observation point | `goldensun.py:26` |
| The year reported | `goldensun.py:39`, or pass `--year` to `goldensun.py` and `season.py` |
| Morning thresholds for the day counts | `goldensun.py:33` |
| How far out the skyline is traced | `--radius` on `goldensun.py`, default at `goldensun.py:124` |
| Observer eye height | `horizon.py:28` |
| Angular and radial ray spacing | `horizon.py:118` |
| The winter window for civil dawn counts | `civildawn.py:71` and `:72` |
| School bell times | `civildawn.py:117` |
| The departure-time sweep | `civildawn.py:135` to `:137` |

Solstice and equinox dates are derived from the year rather than typed in, by finding the days of extreme and zero solar declination, so there is no second date to keep in step.

**Environment.** Tested on Python 3.14.2 and numpy 2.4.4, on Windows 11. `requirements.txt` specifies `numpy>=1.24`. That floor is **inferred, not verified**: the code uses only long-established numpy features, and the oldest Python the syntax requires is 3.6, but numpy 1.24 itself requires Python 3.8, which makes 3.8 the effective floor. Nothing older than the tested versions has actually been run.

## Limitations

State these before citing any figure from this project.

**The terrain half has never been checked against an outside source.** There is no published skyline profile for Golden to compare against. The solar arithmetic is thoroughly validated; the ridge angles are not, and cannot be without either surveyed horizon data or independent processing of the same elevation tiles. The self-test covers the half that can be checked and is silent on the half that cannot. This is the largest single weakness in the project.

**The civil dawn figures carry the almanac's own blind spot, and they err in a known direction.** `civildawn.py` uses a flat horizon, so like every published sunrise table it does not account for Golden sitting in a valley. This matters more than it sounds. At civil dawn the twilight glow is concentrated low in the eastern sky, which is precisely the band the eastern ridge occludes, so usable light on the ground in Golden arrives later than these figures show. The direction of that error is known with confidence; the magnitude is not computed anywhere in this project and could not be, because it would require a sky-radiance model rather than the ray trace used here. The practical consequence is that the civil dawn counts are **conservative**: real exposure is at least this bad and probably worse, under both clock options. That cuts in the same direction for both, so the comparison between them is not undermined, but any absolute claim about a specific morning is a floor rather than an estimate.

For direct sunlight the valley effect is not left unquantified. `goldensun.py` is the terrain-aware half and measures it: on the winter solstice the sun reaches the townsite at 9:35 against a flat-horizon 8:53, which is 42 minutes later, and leaves at 3:26 against 4:39, which is 73 minutes earlier.

**The departure time is not measured.** The civil dawn counts depend on when children actually leave home, and nobody has that number. Under BC Pacific the count is zero from an 8:15 departure onward, but 20 at 8:10 and 46 at 8:00. The difference between the two clock options stays between 77 and 107 mornings across the whole plausible range, so the comparison is robust even though the absolute figure is not. The phrase "not one morning all winter" is true only for departures at 8:15 or later.

**Two of four bell schedules are from the previous school year.** All four schools' times were read from their own pages on 6 September 2026, but the Alexander Park and Lady Grey pages are headed 2025-26, and the Nicholson page states no year. Only Golden Secondary is on record as current. Morning bells rarely move between years, but that is an assumption rather than a check. The binding case, the earliest bell at 8:40, is the best-sourced of the four.

**One observation point.** Every figure describes the townsite coordinates above. Other parts of town will differ.

**Surface model, not bare earth.** The elevation data includes trees and buildings. On distant ridgelines that makes them slightly too tall and overstates the terrain effect. At the observation point it raises the assumed viewpoint and understates it. Anything closer than about 30 metres does not appear at all. The biases pull in opposite directions and which one dominates here has not been established.

**Clear skies only.** Valley cloud and December temperature inversions are not modelled, and in December they matter. Inversions also bend light more than the standard refraction coefficient allows, which would place true sunrise slightly earlier than calculated.

**The two figures are not equally firm.** Sensitivity testing shows the morning time is robust, because the ridge falls away steeply as the sun climbs, while the afternoon time is more sensitive, because the sun descends into a skyline that is rising again. A quarter of a degree of skyline error is worth about ten minutes in the afternoon. Treat 9:35 as firm and 3:26 as give or take a few minutes.

**Sampling.** The annual day counts use 2 minute sampling, so individual days near a threshold could be off by one sample. Rays are spaced half a degree apart, which is 524 metres at 60 kilometres, so a narrow notch or spire between two rays is invisible. `diagnostics.py` measures both effects rather than assuming they are small.

## Data sources and attribution

Elevation data is the AWS Terrain Tiles open dataset, accessed from `https://s3.amazonaws.com/elevation-tiles-prod/skadi/`. It is not redistributed here; the scripts download it on demand and `.gitignore` excludes the `dem` folder. The collection draws on several national datasets and the attribution required depends on which underlies a given tile. For this area both of the following apply:

- SRTM data courtesy of the U.S. Geological Survey
- Contains information licensed under the Open Government Licence, Canada
- Mapzen, for the Terrain Tiles collection itself

Terrain Tiles was accessed on 2026-09-06 from `https://registry.opendata.aws/terrain-tiles`.

Solar position uses the NOAA Solar Calculator algorithm. Validation reference values come from the US Naval Observatory, Astronomical Applications Department.

## Licence

The code is licensed under the MIT License; see `LICENSE`. The documents, meaning the reports, the method statement, the source sheet and this README, are licensed under Creative Commons Attribution 4.0; see `LICENSE-docs`. The two differ because MIT is written for software and grants the right to run, modify and redistribute code with almost no conditions, while CC BY is written for written work and asks that the author be credited when the material is reused or quoted.

This is personal work by a councillor. It is not a Town of Golden publication and not a LUMINARYX product.

## Appendix: installing Python on Windows and running from scratch

For a machine with nothing installed.

**Install Python.**

1. Go to `https://www.python.org/downloads/windows/` and download the latest stable Windows installer.
2. Run the installer. On the first screen, **tick the box marked "Add python.exe to PATH"** before clicking Install Now. This is the single step that causes the most trouble later if it is missed.
3. Click Install Now and wait for it to finish.
4. Open PowerShell from the Start menu and type `python --version`. It should print a version number.

**Get the code, using git.**

1. In PowerShell, move to where you want the folder to live, for example `cd $HOME\Documents`
2. `git clone <repository URL>`
3. `cd timechange`

**Get the code, without git.**

1. On the repository page in your browser, click the green Code button.
2. Choose Download ZIP.
3. Open the downloaded file, and drag the folder inside it to somewhere permanent such as Documents.
4. In PowerShell, `cd` to that folder, for example `cd $HOME\Documents\timechange`

**Install the dependency and run.** All of the following are typed into PowerShell.

1. `pip install -r requirements.txt`
2. `python goldensun.py --flat`
3. `python goldensun.py`

Step 3 downloads about 51 MB the first time and takes roughly 90 seconds after that.

**Troubleshooting.**

*"python is not recognized as the name of a cmdlet, function, script file, or operable program."* Python is installed but Windows cannot find it, almost always because the "Add python.exe to PATH" box was not ticked. The fix is to run the installer again, choose Modify, and ensure that option is selected; or reinstall and tick it. Closing and reopening PowerShell afterwards is necessary, because a terminal reads PATH when it starts.

*"No module named numpy."* The dependency is not installed in the Python being used. Run `pip install -r requirements.txt` from the repository folder. If that appears to succeed but the error persists, more than one Python is installed and `pip` belongs to a different one; use `python -m pip install -r requirements.txt` instead, which forces the two to match.

*"Access is denied" or a permissions error during `pip install`.* Install for your user account only rather than for the whole machine: `python -m pip install --user -r requirements.txt`. Do not run PowerShell as Administrator to work around this.

*The scripts run but cannot find something, or `python: can't open file`.* You are in the wrong folder. Run `Get-Location` to see where you are and `Get-ChildItem` to list what is there; you should see `goldensun.py`. If not, `cd` to the folder containing the scripts. The scripts locate their own data files relative to themselves rather than to the terminal, so the tile cache and the CSV files are found correctly once the command itself resolves.

*The first run of `goldensun.py` appears to hang.* It is downloading roughly 51 MB of elevation tiles and prints a line per tile. Give it a minute or two on a normal connection. If the download fails, the same tiles are available free from USGS EarthExplorer or viewfinderpanoramas.org; place the four `.hgt` files for N50W117, N50W118, N51W117 and N51W118 into a folder named `dem` beside the scripts and the download will be skipped.

## Contact

Written by Joy Guyot. Contact: joy@luminaryx.ca

Provided as is, without warranty of any kind. See `LICENSE`.
