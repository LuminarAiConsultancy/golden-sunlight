# Golden Time Observance — Source Sheet
**Compiled 2026-09-05. Facts and sources only. No drafted remarks.**

---

> ## REVISION NOTE, added 2026-09-06
>
> **The figures in sections 2 and 3 below have been recomputed and some have
> changed. The original numbers are left in place, unedited, so the change is
> visible rather than silent. Where this note and the sections below disagree,
> this note is correct.**
>
> This document has not been circulated outside its author. The note exists to
> keep the working record honest, not to reconcile a version already in
> somebody else's hands.
>
> ### What was recomputed, and why
>
> Sections 2 and 3 were originally produced with the Python `astral` library,
> using a script that was never part of the published code. That meant the
> single most quoted figure in this package, the 87 mornings, could not be
> reproduced by anyone checking the work. `civildawn.py` in this repository now
> recomputes those figures from the same solar code as everything else, with no
> extra dependency. **`civildawn.py` is authoritative from this date.**
>
> This was a recomputation, not a correction of a known error. Nothing was
> adjusted to reproduce or to avoid the original numbers.
>
> ### Section 2, civil dawn and sunrise
>
> All nine **civil dawn** times reproduce exactly. **Sunrise** is one minute
> later on seven of the nine rows (15 Nov, 1 Dec, 15 Dec, 21 Dec, 5 Jan,
> 1 Feb, 1 Mar); 2 Nov and 15 Jan are unchanged.
>
> Section 2 states the coordinates as 51.2967 N, 116.9631 W. The recomputation
> uses the project's coordinates, 51.2969 N, 116.9647 W, so that the repository
> has one location rather than two. The two points are about 115 m apart, which
> is under half a second of time and is **not** the cause of any change below.
>
> ### Section 3, the headline counts
>
> | Measure | As first drafted | Recomputed |
> |---|---|---|
> | Dark at 8:30, BC Pacific | 0 | **0** |
> | Dark at 8:30, permanent MDT | 87 (Nov 17 to Feb 12) | **89** (Nov 17 to Feb 13) |
> | Dark at 8:20, BC Pacific | 0 | **0** |
> | Dark at 8:20, permanent MDT | 98 (Nov 11 to Feb 17) | **101** (Nov 10 to Feb 18) |
> | Sunrise after 8:45, BC Pacific | 31 | **35** |
> | Sunrise after 8:45, permanent MDT | 110 | **113** |
>
> The counts moved because sub-minute differences flip days that sit near the
> threshold. The most likely cause is that `astral` uses a geometric 6 degrees
> for civil dawn while this code applies atmospheric refraction first. Every
> count moved in the same direction, upward, by two to four days.
>
> **The zeros under BC Pacific are unchanged.** The central claim of section 3
> survives the recomputation.
>
> ### Two figures that answer different questions
>
> Section 4 previously recorded Lady Grey and Nicholson bell times as "needs
> checking". Both are now filled in. The provenance differs per school and is
> stated per row rather than under one date, because they are not equally firm:
>
> Every time below was read from the school's own bell-schedule page on
> 2026-09-06. None is inferred from the pattern at the other schools.
>
> | School | Bell | Classes | Source page | Year stated on page |
> |---|---|---|---|---|
> | Nicholson Elementary | 8:40 | 8:45 | `nes.sd6.bc.ca/about-us/bell-schedule` | not stated |
> | Golden Secondary | 8:40 | 8:45 | `gss.sd6.bc.ca/about-us/bell-schedule` | 2026-27 |
> | Alexander Park | 8:50 | 8:55 | `apes.sd6.bc.ca/about-us/bell-schedule` | **2025-26** |
> | Lady Grey Elementary | 8:53 | 8:58 | `lges.sd6.bc.ca/about-us/bell-schedule` | **2025-26** |
>
> Alexander Park's page reads "Warning Bell (inside and outside) 8:50 am" and
> "Morning Classes Begin (no bell) 8:55 am". Nicholson's Friday morning is
> identical to the rest of the week; only dismissal differs.
>
> **Caveat before citing any of this.** Only Golden Secondary is on record as
> the current 2026-27 schedule. Alexander Park and Lady Grey both publish a page
> headed 2025-26, and Nicholson's page does not state a year. Morning bells
> rarely move between years, but "rarely" is not the standard the rest of this
> package is held to. The mitigating fact is that the binding case, the earliest
> bell at 8:40, is also the best-sourced of the four.
>
> Anchoring the count to those actual bells gives, under permanent MDT, **77**
> mornings still dark at the earliest bell of 8:40, falling to 49 at the latest
> classes start of 8:58. Under BC Pacific it is **0 at every bell**.
>
> **77 is not a corrected 87.** The two answer different questions. A bell is an
> ARRIVAL time, so a bell-anchored count measures whether it was dark when the
> child got there, and necessarily understates the walk that preceded it. The
> 8:20 and 8:30 figures were an attempt to represent the walk itself. Both are
> legitimate; presenting either as a revision of the other is not.
>
> ### The assumption that actually carries the weight
>
> The walking time remains unmeasured, and it matters more than any change
> above. Under BC Pacific the count is 0 from 8:15 onward, but **20** at 8:10
> and **46** at 8:00, against 112 and 123 under permanent MDT. The difference
> between the two options stays large at every hour tested, so the argument
> holds in every version. The specific claim "not one morning all winter" holds
> only for departures at 8:15 or later. Section 11 item 2, the walk-versus-bus
> numbers, is still the gap that would move these figures most.
>
> Run `python civildawn.py` to regenerate all of the above.

---

## 1. The two options, stated as clock offsets

| Option | UTC offset | Same clock as |
|---|---|---|
| BC Pacific Time (new, from Nov 1 2026) | UTC-7 | Vancouver, Kamloops, Kelowna. Identical to the Mountain Standard clock Golden currently keeps in winter. |
| Permanent Mountain Daylight (RDEK / Alberta) | UTC-6 | Cranbrook, Invermere, Calgary. Golden's current summer clock, held year round. |

**Confidence: high.** The UTC-7 figure for the new Pacific Time Zone is stated on the RDEK's own engagement page (engage.rdek.bc.ca/timechange).

**Consequence worth stating plainly:** aligning with BC does not move Golden's winter clock at all. It holds the clock Golden already keeps every December. Aligning with the RDEK is the option that changes Golden's winter mornings.

---

## 2. Sunrise and civil dawn, Golden BC

Computed for 51.2967 N, 116.9631 W using standard solar position algorithms (Python `astral` 3.2). Civil dawn is the point at which there is usable outdoor light; before it, conditions are functionally dark.

| Date | Civil dawn (Pacific) | Sunrise (Pacific) | Civil dawn (perm MDT) | Sunrise (perm MDT) |
|---|---|---|---|---|
| Nov 2 2026 | 07:07 | 07:43 | 08:07 | 08:43 |
| Nov 15 2026 | 07:28 | 08:05 | 08:28 | 09:05 |
| Dec 1 2026 | 07:51 | 08:30 | 08:51 | 09:30 |
| Dec 15 2026 | 08:05 | 08:46 | 09:05 | 09:46 |
| **Dec 21 2026** | **08:09** | **08:50** | **09:09** | **09:50** |
| Jan 5 2027 | 08:11 | 08:51 | 09:11 | 09:51 |
| Jan 15 2027 | 08:07 | 08:46 | 09:07 | 09:46 |
| Feb 1 2027 | 07:49 | 08:25 | 08:49 | 09:25 |
| Mar 1 2027 | 06:59 | 07:32 | 07:59 | 08:32 |

**Confidence: high** on the astronomy. These are computed, not sourced, so they are checkable against timeanddate.com if anyone wants a second reference.

---

## 3. The headline figure

Counting every day from Oct 1 2026 to Apr 30 2027:

| Measure | BC Pacific | Permanent MDT |
|---|---|---|
| Days still fully dark (before civil dawn) at 8:30 am | **0** | **87** (Nov 17 to Feb 12) |
| Days still fully dark at 8:20 am | 0 | 98 (Nov 11 to Feb 17) |
| Days sunrise falls after 8:45 am | 31 | 110 |

Under BC Pacific there is not one morning all winter when a child leaving the house at 8:30 is walking before civil dawn. Under permanent Mountain Daylight there are 87.

**Confidence: high**, subject to the walking-time assumption in section 4.

---

## 4. Bell times (these drive everything above)

| School | Grades | Warning bell | Classes begin | Source |
|---|---|---|---|---|
| Golden Secondary | 8-12 | 8:40 | 8:45 | gss.sd6.bc.ca/about-us/bell-schedule (2026-27 schedule, current) |
| Alexander Park Elementary | K-3 | 8:50 | 8:55 | apes.sd6.bc.ca/about-us/bell-schedule |
| Lady Grey Elementary | 4-7 | not retrieved | not retrieved | **needs checking** |
| Nicholson Elementary | K-7 | not retrieved | not retrieved | **needs checking** |

**Confidence: high** for GSS and Alexander Park, both from current school pages. The 8:20 to 8:40 walking window used above is an inference from these bell times, not a measured figure.

---

## 5. School district structure

Golden is in School District 6 Rocky Mountain, which spans Golden, Windermere/Invermere/Canal Flats and Kimberley. Roughly 3,500 to 4,000 students, three zones, three trustees per zone.

**Relevance:** Invermere and Kimberley are RDEK and will be on permanent MDT. If Golden goes Pacific, one school district operates across a one-hour internal offset. This is a real operational point and it cuts against your position, so it is better to have it than to be handed it.

**Confidence: high** on the boundary. Sources: sd6.bc.ca school directory, SD6 LinkedIn profile.

---

## 6. Health service structure

Interior Health lists Golden and District Hospital as a Level 1 community hospital **in the East Kootenay health service area**, notwithstanding that Golden sits in the CSRD for local government purposes.

**Relevance:** Golden's hospital administratively faces a region going to MDT. Coordination questions about transfers, on-call and visiting clinics are legitimate. Equipment allocation is a different question and no link to time observance has been shown.

**Confidence: high** on the health service area (interiorhealth.ca location page). **No evidence found** that Golden and District Hospital has a CT scanner. A peer-reviewed study conducted at the hospital describes it as 247 km from the nearest CT scanner, which matches the 246 km road distance to Cranbrook. That study is several years old, so confirm current status with Interior Health before relying on it.

**On CT versus MRI:** if the claim was actually about MRI rather than CT, the analysis does not change. Neither machine's allocation has been shown to depend on time observance, and swapping which machine is named does not supply a mechanism. Interior Health capital allocation runs on population, utilisation and regional hospital district cost-sharing, none of which are affected by what a municipality sets its clocks to.

**Worth checking, because it is the nearest thing to a real mechanism:** which regional hospital district Golden contributes to for capital cost-sharing. Golden is CSRD for local government but its hospital sits in the East Kootenay health service area. If there is a funding relationship running east, that is the only pathway by which regional divergence could plausibly touch equipment. It would still be a governance question, not a time-observance one.

---

## 7. Distance and travel time to Cranbrook

Golden to Cranbrook is **246 km**, roughly 2.5 to 3 hours driving. **Time observance does not change drive time under any scenario.**

If Golden is on Pacific and Cranbrook on MDT, a 3-hour drive departing Golden at 8:00 arrives at 12:00 by Cranbrook clocks. That is a clock-reading artifact and it reverses on the return trip.

**Confidence: high** on both the principle and the 246 km figure (confirmed locally 2026-09-05).

---

## 8. Calgary field trip arithmetic

Golden and Calgary are currently on the same clock. Alberta is moving to permanent Mountain Daylight. If Golden adopts Pacific Time, Golden runs one hour behind Calgary year round.

To meet a fixed opening time at a Calgary destination, a bus would depart one hour earlier by Golden clocks. **This arithmetic is correct.** The inference that schools would therefore stop running the trips is speculation about district behaviour, not an error in the premise.

**Confidence: high** on the arithmetic, **low** on the consequence.

---

## 9. The 1974 US permanent daylight saving experiment

Year-round DST began Jan 6 1974 as an energy-crisis measure, intended to run two years. Eight Florida children were killed in traffic accidents in the weeks following; a Florida education department spokesman told the New York Times that six of those deaths were clearly attributable to children travelling to school in darkness. Governor Reubin Askew called a special session. Public support fell from 79% (Dec 1973) to 42% (Feb 1974). Ford signed the repeal Oct 5 1974; the US returned to standard time Oct 27 1974.

**Counter-evidence you will be handed:** the National Safety Council reported pre-sunrise fatalities rising only from 18 to 20 nationally. The sample is small and short. Subsequent transportation analysis did not establish a robust national effect.

**Confidence: high** that the events occurred and drove the repeal. **Low** that permanent DST caused a measurable national increase in child fatalities. Sources: Smithsonian, Washingtonian, PolitiFact (2026), History.com.

**Assessment: rhetorically strong, evidentially soft.** The Golden sunrise figures in section 3 are better ground.

---

## 10. Independent support for standard time

The American Medical Association has endorsed permanent standard time, and sleep medicine bodies take the same position, on circadian grounds. This is independent of the 1974 traffic data.

**Confidence: medium-high.** Verify the current AMA position statement directly before citing it.

---

## 11. Gaps — things not verified, needed before you speak

1. Lady Grey and Nicholson bell times.
2. How many Golden students walk versus bus, by school. This is the number that decides how much weight section 3 carries. School district or PAC should have it.
3. Any written record of Highway 1 closure effects on in-town traffic volumes, and any near-miss or complaint history at the Highway 95 crossings. Town, RCMP or district.
4. Bridge construction detour routing. **Duration confirmed at a further year or more as of 2026-09-05**, so the detour conditions persist through the entire winter this decision governs. Get the routing specifics and the projected completion date on paper.
5. Whether Golden and District Hospital has a CT or MRI scanner, current status, and whether either is on any capital plan.
6. Which regional hospital district Golden contributes to for hospital capital cost-sharing.

**Resolved since first compilation:** Golden to Cranbrook road distance, 246 km.

---

## 12. Highway 1 winter closures and in-town traffic

**No agency publishes a clean annual count of Highway 1 closures affecting Golden.** DriveBC does not retain accessible historical closure statistics. The figures below are what is publicly documented; the authoritative source for a defensible number is the Ministry of Transportation Rocky Mountain district office, which holds the closure logs.

**Two different closure types, two different effects on town:**

| Closure | Direction | What happens to traffic |
|---|---|---|
| Rogers Pass (west), avalanche control | Golden to Revelstoke | No alternate route exists. Parks Canada holds traffic **in Golden**. Vehicles queue and park in town. |
| Kicking Horse Canyon (east) | Golden to Castle Junction | Through traffic **routed via Highways 93S and 95**, adding up to 1.5 hours. This puts highway volume directly onto Highway 95. |

Both produce the in-town congestion described. The eastward one puts traffic on the road children cross.

**Documented frequency and duration:**

- Parks Canada states avalanche control closures last **2 to 8 hours or longer**, and that traffic is held in Revelstoke and Golden when longer closures are required. Source: parks.canada.ca Glacier National Park winter driving page. **Confidence: high.**
- Parks Canada material states closures for avalanche control normally run Golden to Revelstoke and last **about 4 to 8 hours**. **Confidence: high.**
- **2024-25 season:** approximately **a dozen avalanche control missions** in Rogers Pass (537 howitzer rounds, 45 remote explosives, 71 helicopter explosives). Snowfall that season was reported 15% below average. Source: Parks Canada via Black Press, May 2026. **Confidence: medium-high.**
- **December 2025:** three Rogers Pass closures between Dec 10 and Dec 18, one of them an 8-hour closure. Source: Revelstoke Review, Dec 18 2025. **Confidence: high.** Useful as an illustration of clustering during storm cycles.
- **March 2026:** an atmospheric river produced 700+ detected avalanches and an intermittent **four-day** closure of Highway 1. Source: Parks Canada via Black Press. **Confidence: high.**
- Winter traffic volume through Rogers Pass: **approximately 3,000 to 4,000 vehicles per day**. Sources: Parks Canada, Kootenay Rockies. **Confidence: medium.** Illustrates the volume that gets held or diverted.
- Rogers Pass has the highest avalanche rating of any highway in North America: 135 avalanche paths across a 43 km stretch. Source: Parks Canada. **Confidence: high.**

**Note on the Kicking Horse Canyon:** Phase 4 construction is complete as of July 2024 and the canyon operates as a four-lane highway. The heavy scheduled construction closures of 2021 to 2024 are historical and should not be cited as current conditions. Unplanned closures from crashes, weather and rockfall continue.

**The strongest item is one the Town already holds.** Golden Fire Rescue members acting as crossing guards during a Highway 1 closure is a documented operational fact from the Town's own service. It is local, specific, and no one at the table can dispute it. Get the dates, the closure that triggered it, how many times it has happened, and whether the fire chief will put it in writing. That single fact does more work than every statistic above, because it establishes that the crossing already fails under closure conditions without any darkness added.

**Foreseeable worsening: end of military avalanche control.**

The Department of National Defence has confirmed it will not renew the Operation PALACI memorandum of understanding with Parks Canada. The agreement expires **August 17, 2027**. Operation PALACI has run since 1961, using 105-mm howitzers and 15 to 20 reserve personnel across the 43-km stretch between Revelstoke and Golden. It is Canada's longest-running domestic military operation and the world's largest mobile avalanche control program. DND cites defence modernization priorities and divestment of legacy artillery systems; a November 2025 letter from the Chief of the Defence Staff obtained under access to information points to resource pressure.

**The line that matters for Golden, and it is the Province's own:** the BC Ministry of Transportation stated it is deeply concerned, and that withdrawal of Armed Forces support **"will significantly increase closure durations through Rogers Pass."** The ministry has asked Ottawa to extend the service until alternate mitigation measures are in place. Highway 1 through the corridor carries roughly $65 million in commercial goods daily.

**Confidence: high.** Sources: Canadian Press May 12 2026, CBC May 12 2026, Castanet May 1 2026, Black Press/Revelstoke Review Apr 30 2026.

**Timing caveat you must state if you use this.** The MOU runs through August 2027, so winter 2026-27, the first winter under whatever Golden decides, is still covered by the current program. The increase in closure durations is a winter 2027-28 issue and beyond. This is a foreseeable worsening of the conditions your argument relies on, not a description of this coming winter. Say it that way or someone will correctly point out the gap.

**What it does for the argument:** it means the closure conditions that already force Golden Fire Rescue to staff crossings are officially expected to get longer, on the Province's own assessment, within the life of the decision council is making. A time observance choice is not reviewed every year.


1. Golden Fire Rescue record of crossing guard deployments and the closures that prompted them.
2. MoTI Rocky Mountain district closure log for Highway 1 either side of Golden, last three to five winters, with dates and durations.
3. Any Town or RCMP traffic count on Highway 95 through town during a closure event versus a normal day.

---

## 13. RDEK vote record, for reference

- **Mar 13 2026:** board voted 8-7 for year-round Mountain Standard, effective Nov 1 2026, declining a staff recommendation to survey first. In favour included Wayne Price and Norma Blissett (Cranbrook), David Wilks (Sparwood), Al Miller (Invermere), Don McCormick (Kimberley).
- **Apr 10 2026:** board rescinded that decision and directed a public survey. Only two directors opposed reopening: Blissett and Wilks.
- **Jul 3 to Aug 3 2026:** survey, 14,000+ responses. 89% wanted to stop semi-annual changes. Of those choosing a time, 66% Daylight / 34% Standard. Top reason among Standard supporters: alignment with the rest of BC.
- **Aug 14 2026:** board voted 12-3 for permanent Mountain Daylight. The three opposed: Al Miller (Invermere), Wayne Price (Cranbrook), Roberta Schneider (Area G).

**Confidence: high** on all four. **Note:** no published source names the twelve who voted in favour on Aug 14. Any statement about how a specific director other than Miller, Price or Schneider voted that day is unverified. The RDEK minutes or meeting recording would settle it.

Sources: e-KNOW, Cranbrook Daily Townsman, Columbia Valley Pioneer, CBC, RDEK release, City of Cranbrook releases.
