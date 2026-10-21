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

1. In `meteor_doppler_wdpn.py`, edit `TX` and `RX` (`(lat°, lon°, height m)`) and the carrier frequency `F` in Hz.
2. Update the hard-coded values in `meteor_3d_interactive.py` that assume a 210 km baseline:
   - The slider range of **Reflection point along path** (`min`/`max` of `#x`) should be about ± half the baseline.
   - The preset positions (`-52`, `0`, `52`) should be about ±¼ of the baseline.
   - The ground patch extent (`±330` km) and the **Offset** range should be scaled to the baseline.
3. Change the labels: the title (`WDPN 54.31 MHz → RX`), the `WDPN TX` marker, and the "+ = NW" offset note. Check the sign of the offset against your geometry.
4. Run `python meteor_3d_interactive.py` and open the new HTML.

The scene frame is local East/North/Up in km, centred on the ground point below the baseline midpoint. It is an exact rigid transform of ECEF, so distances and angles are true.
