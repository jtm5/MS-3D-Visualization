# Meteor Scatter 3D Explorer

An interactive, single-file web page for building intuition about **VHF forward meteor scatter**: where a meteor trail has to be, and how it has to be moving, to produce a given Doppler shift on a TV carrier received off-air.

Current setup: WDPN-TV (Philadelphia, ch 2, 54.309441 MHz pilot) → receiver near Washington DC, about a 210 km baseline.

Included is a partial update of the K1FR-WDPN code for Rob, NN4NT, and each script for that has "_Rob" at the end. This code uses
NN4NT coordinates and an imaginary TX site 210 km NE. The TX site will need changing to a real emitter to include the antenna altitude.

## Files

| File | Purpose |
|---|---|
| `meteor_3d_interactive.py` | Generator script. Writes the HTML page. |
| `meteor_3d_interactive.html` | The explorer (about 3.7 MB, Plotly bundled in). Open it in any modern browser. It works offline and needs no server. |
| `meteor_doppler_wdpn.py` | Shared geometry: TX/RX coordinates, carrier frequency, ECEF/ENU helpers. The generator imports it. |
| `meteor_3d.py` / `meteor_3d.html` | Earlier static version with fixed preset cases. |

To regenerate after changing anything, run the command below. It needs `numpy` and `plotly`.

```bash
python meteor_3d_interactive.py
```

## What you see

- **3D view** (drag to rotate, scroll to zoom): ground, TX (red), RX (blue), the dashed baseline, the reflection point, and the meteor trail as an arrow in its direction of travel.
- **Blue shell**: the surface of constant TX→P→RX path length through the reflection point. A meteor moving *along* this surface (tangent to it) has zero Doppler.
- **Trail colour**: green when |f<sub>D</sub>| ≤ 100 Hz at the reflection point, red when it's outside.
- **Large readout**: Doppler at the reflection point, plus the maximum possible shift at that speed, path length, ranges to TX and RX, and bisector elevation.
- **Lower plot**: Doppler along the trail (shaded band is ±100 Hz). It shows how the shift sweeps as the meteor moves through the geometry.

The math runs live in the page's JavaScript: f<sub>D</sub> = −(v/λ) · v̂ · (û<sub>T</sub> + û<sub>R</sub>). A positive shift means the path is shortening.

## Controls

| Control | Meaning |
|---|---|
| Reflection point along path | Position along the TX–RX line (km from the midpoint). |
| Offset from path | Distance off the baseline (+ = NW). |
| Altitude | 70–130 km. Meteor trails are typically about 80–110 km. |
| Heading | Direction of travel, degrees from north. |
| Descent below horizontal | Entry angle. |
| Speed | 11–72 km/s. |
| Presets | Jump to ¼ from RX, midpoint, or ¼ from TX. |
| Set descent for 0 Hz | Solves for the descent angle that gives exactly 0 Hz at the current heading. |
| Vertical exaggeration ×2 | Stretches height so the geometry is easier to see. |

## Usage tips

1. **Start with "Set descent for 0 Hz."** Pick a position and heading, click it, and you get the tangent trajectory. Then nudge heading or descent and watch the Doppler move off zero.
2. **Doppler is very sensitive to direction.** Speed times the cosine of the angle to the bisector sets it, so a degree or two of heading or descent can change the shift by hundreds of Hz at 20+ km/s. That is why a ±100 Hz window is a narrow sliver of trajectories.
3. **If the button says there is no 0 Hz descent**, the tangent solution would require the meteor to climb. Pick another heading.
4. **Use the lower plot to judge a real event.** A trail that starts at a large shift and sweeps through zero looks very different from one that stays near zero. Compare against your spectrogram.
5. **Try the altitude and offset sliders together.** Moving off the baseline mostly changes path length and the bisector elevation, which sets the maximum Doppler you can get.
6. **Vertical exaggeration** helps with the flat geometry. The earth's curvature is real, so far-off points sit below the horizon.
7. **Rotate to look along the baseline** (or straight down) to see why the tangent surface is an ellipsoid of revolution about the TX–RX axis.

## Model limits

- Straight-line propagation with no refraction.
- Straight trails at constant speed. There is no deceleration or ablation model.
- Specular reflection geometry only. Trail orientation and the Fresnel-zone/reflection-condition constraint are not enforced. The page shows what the Doppler would be at a point, not whether that point is a viable reflector.
- The ±100 Hz threshold is hard-coded in the page.

## Adapting to your own TX and RX sites

There are two files to touch. Everything else (the geometry, the Doppler math, the page logic) follows from them. Line numbers below are approximate; search for the quoted text instead if they have drifted.

### Step 1: Set the sites and frequency in `meteor_doppler_wdpn.py`

Near the top of the file, in the "Constants" and "Station positions" blocks:

| Name | What it is | Format |
|---|---|---|
| `F` | Transmitter carrier frequency | Hz, for example `54.309441e6` |
| `RX` | Receiver position | `(latitude°, longitude°, height m)` |
| `TX` | Transmitter position | `(latitude°, longitude°, height m)` |

- Use decimal degrees: north and east are positive, so a US longitude is negative.
- Height is metres above the ellipsoid, not above ground. Use the antenna height above sea level plus the tower height for a real emitter.
- The file keeps a second, commented-out `RX`/`TX` pair (Huntsville and an assumed site 210 km NE). Comment one pair out and the other in to switch between setups.
- The speed default is also here (`V_KMS`). You can override it without editing: `python meteor_doppler_wdpn.py 30` runs the static plots at 30 km/s. The interactive page has its own speed slider.

Quick check: running `python meteor_doppler_wdpn.py` prints the wavelength and the ground baseline length in km. Note that baseline number, because you need it in the next step.

### Step 2: Rescale the page in `meteor_3d_interactive.py`

The generator builds an HTML page from the template string `PAGE`. The slider ranges and a few numbers inside it were chosen for a 210 km baseline, so a longer or shorter baseline needs them changed. Search for the text in the **Find** column.

| What to change | Find | Default (210 km baseline) | Set it to |
|---|---|---|---|
| Along-path slider range | `id="x" type="range"` | `min="-105" max="105"` | about ± half your baseline |
| Along-path starting value | the `value=` on that same slider | `-52` | ¼ of the baseline, toward the RX |
| Preset buttons | `{q:-52,m:0,t:52}` (near the bottom of the script) | `-52`, `0`, `52` | −¼, 0, +¼ of the baseline |
| Offset slider range | `id="y" type="range"` | `min="-250" max="250"` | roughly ± the baseline or a bit more |
| Ground patch size | the `// ground:` comment, then `x=-330+15*j` and `y=-330+15*i` | ±330 km, 45 × 45 grid, 15 km spacing | enough to cover both stations and the ellipsoid |

For the ground patch, keep the grid symmetric: the start value (`-330`) times 2 should equal the step (`15`) times the loop count (`44`, so 660). If you change one, change the others. The patch follows the curve of the Earth, so a large patch will visibly drop away at its edges.

### Step 3: How to use the sliders

The **Reflection point along path** and **Offset from path** sliders place the meteor trail's reflection point on the ground below it; **Altitude** lifts it.

- **Along path**: `0` is the midpoint of the baseline. Negative values move toward the RX, positive toward the TX. The ends of the slider are the stations themselves. Use the **¼ from RX / Midpoint / ¼ from TX** buttons to jump there; they also reset the offset to 0.
- **Offset from path**: distance in km to the side of the baseline. `+` is to the left when you face from the RX toward the TX. For the WDPN setup the TX is to the NE of the RX, so left is **NW**, and that is what the on-page label says.
- **Altitude**: 70 to 130 km. The slider limits are in the `id="h"` line if you need a different range.
- **Heading, Descent, Speed**: the trail's direction (degrees from north), its angle below horizontal, and its speed. These do not depend on the sites, so leave them alone.

A good first session with a new site pair:

1. Open the new HTML and click **Midpoint**. The reflection point should sit right between the red TX and blue RX markers.
2. Drag **Offset** to both ends. The point should leave the baseline symmetrically and stay on the page.
3. Click **Set descent for 0 Hz**. The readout should show a value near 0 Hz and the trail should turn green.

### Step 4: Fix the labels and the offset note

These are plain text in the page, so they do not affect the math:

- The page title and the heading `WDPN 54.31 MHz → RX forward scatter` (the `<title>` and `<h1>` lines).
- The marker text `WDPN TX` in the TX trace.
- The offset label `Offset from path (+ = NW)`. If your TX is not to the NE of your RX, the left-of-baseline side will not be NW. Work out which compass direction is to the left when looking from RX toward TX, and write that in the label.
- The slider help text in the blue-shell note is generic and can stay.

### Step 5: Regenerate

```bash
python meteor_3d_interactive.py
```

This rewrites `meteor_3d_interactive.html`. Reload it in the browser (a hard refresh, Ctrl+F5, avoids a cached copy).

### Common problems

- **The page is blank or the shell looks wrong**: the console (F12) usually shows a JavaScript error. A stray character in one of the edited lines inside `PAGE` is the usual cause.
- **The reflection point is nowhere near the stations**: the along-path range or preset values are still the 210 km defaults.
- **The ground patch cuts through the stations**: the `±330` km patch is too small for your baseline.
- **The slider directions seem backwards**: check that `TX` and `RX` are not swapped. Negative along-path values point toward the RX and positive toward the TX.

The scene frame is local East/North/Up in km, centred on the ground point below the baseline midpoint. It is an exact rigid transform of ECEF, so distances and angles are true.
