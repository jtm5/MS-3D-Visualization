"""Meteor forward-scatter Doppler map, WDPN-TV (ch 2, 54.309441 MHz pilot) -> receiver.

For a meteor at point P with velocity vector v, the bistatic path length is R = |P-T| + |P-R|.
    f_D = -(1/lambda) dR/dt = -(v/lambda) * vhat . (uT + uR)
where uT, uR are unit vectors pointing from the transmitter / receiver to P.
f_D = 0  <=>  v tangent to the ellipsoid of constant path length (vhat perpendicular to b = uT + uR).
|f_D| <= 100 Hz  <=>  |vhat . bhat| <= 100*lambda / (v*|b|): a thin band around the great circle of
directions perpendicular to the bisector b.
Outputs: meteor_doppler_wdpn.png, meteor_doppler_wdpn.csv
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- Constants -------------------------------------------------------------
A, E2 = 6378137.0, 0.00669437999014   # WGS-84 semi-major axis (m) and first eccentricity squared
C = 299792458.0                       # speed of light (m/s)
F = 54.309441e6                       # transmitter (TV pilot) frequency (Hz)
LAM = C / F                           # wavelength (m)
import sys
# Meteor speed in km/s; optional first command-line argument overrides the default
V_KMS = float(sys.argv[1]) if len(sys.argv) > 1 else 27000 / 3600.0   # km/s (27000 km/h = 7.5)
V = V_KMS * 1e3                       # meteor speed in m/s
TAG = f"{V_KMS:g}kms"                 # speed label used in output file names
LIM = 100.0                    # Doppler limit (Hz) defining the "near-zero Doppler" band

# Station positions as (latitude deg, longitude deg, altitude m)
RX = (38.821708, -77.103720, 100.0)   # receiver
TX = (40.04169, -75.23614, 378.9)   # WDPN-TV, Roxborough

# RX = (34.74, -86.56, 100.0) #Huntsville
# TX = (36.324, -85.35, 378.9) # An assumed QTH 210 km NE of Huntsville


def ecef(lat, lon, h):
    """Convert geodetic lat/lon (deg) and height h (m) to Earth-centered Earth-fixed xyz (m)."""
    la, lo = np.radians(lat), np.radians(lon)
    n = A / np.sqrt(1 - E2 * np.sin(la) ** 2)   # prime-vertical radius of curvature
    return np.array([(n + h) * np.cos(la) * np.cos(lo), (n + h) * np.cos(la) * np.sin(lo),
                     (n * (1 - E2) + h) * np.sin(la)])


def enu(lat, lon):
    """Local East, North, Up unit vectors (expressed in ECEF coordinates) at lat/lon (deg)."""
    la, lo = np.radians(lat), np.radians(lon)
    e = np.array([-np.sin(lo), np.cos(lo), 0.0])                                  # east
    n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])  # north
    u = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return e, n, u


def geodetic(p, alt_m):
    """(lat, lon, alt) of the point straight above direction p (geocentric direction -> geodetic lat)."""
    lon = np.degrees(np.arctan2(p[1], p[0]))
    lat = np.degrees(np.arctan2(p[2], (1 - E2) * np.hypot(p[0], p[1])))
    return lat, lon, alt_m


def point_on_path(frac, alt_m):
    """Point above the great-circle-ish chord TX->RX at fraction frac, altitude alt (m)."""
    # linear interpolation between the TX and RX ground points (frac=0 -> TX, 1 -> RX)
    g = (1 - frac) * ecef(*TX[:2], 0) + frac * ecef(*RX[:2], 0)
    g /= np.linalg.norm(g)   # project the chord point back out to a direction from Earth's center
    # lat/lon of that direction
    return geodetic(g, alt_m)


def bisector(P):
    """For reflection point P (lat, lon, alt), return (b, uT, uR): b = uT + uR, the (unnormalised)
    bisector of the unit vectors pointing from TX and RX to P. Doppler depends only on vhat . b."""
    p = ecef(*P)                                          # meteor position in ECEF
    uT = (p - ecef(*TX)); uT /= np.linalg.norm(uT)        # unit vector TX -> P
    uR = (p - ecef(*RX)); uR /= np.linalg.norm(uR)        # unit vector RX -> P
    return uT + uR, uT, uR


def doppler(P, az_deg, desc_deg):
    """Doppler (Hz) for velocity heading az (deg from N, direction of travel) descending desc deg below horizontal."""
    e, n, u = enu(P[0], P[1])
    az, d = np.radians(az_deg), np.radians(desc_deg)
    # unit velocity vector in ECEF: horizontal part split into east/north by heading, minus the descent along "up"
    # (az_deg and desc_deg may be arrays; [..., None] lets them broadcast against the 3-vectors)
    vhat = (np.cos(d) * np.sin(az))[..., None] * e + (np.cos(d) * np.cos(az))[..., None] * n \
        - np.sin(d)[..., None] * u
    b, _, _ = bisector(P)
    return -(V / LAM) * (vhat @ b)   # f_D = -(v/lambda) vhat . (uT + uR); positive = path shortening


def zero_doppler_desc(P, az_deg):
    """Descent angle (deg) giving f_D=0 at this heading, or nan if none in 0..90."""
    e, n, u = enu(P[0], P[1])
    b, _, _ = bisector(P)
    be, bn, bu = b @ e, b @ n, b @ u               # east/north/up components of the bisector
    az = np.radians(az_deg)
    h = be * np.sin(az) + bn * np.cos(az)          # horizontal component of b along heading
    # cos(d)*h - sin(d)*bu = 0 -> tan d = h/bu
    d = np.degrees(np.arctan2(h, bu))
    # fold the angle into -90..90 (tan has period 180 deg), then keep only physical descents 0..90
    d = np.where(d < -90, d + 180, np.where(d > 90, d - 180, d))
    return np.where((d >= 0) & (d <= 90), d, np.nan)


def band_halfwidth(P, az_deg, f0=0.0):
    """Range of descent angles giving |f_D|<=LIM at a heading: returns (lo, hi) arrays (deg)."""
    dd = np.linspace(0, 90, 9001)      # descent angles sampled at 0.01 deg steps
    out = []                           # one (lo, hi) pair per heading
    for a in np.atleast_1d(az_deg):
        f = doppler(P, np.full_like(dd, a), dd)   # Doppler along the descent sweep at this heading
        ok = np.abs(f) <= LIM                     # mask of descents inside the +-LIM band
        out.append((dd[ok].min(), dd[ok].max()) if ok.any() else (np.nan, np.nan))
    return np.array(out)


def P_offset(x_km, y_km, alt_m):
    """Reflection point x_km along the baseline (+ toward TX) and y_km to the side (+ = toward 320 deg, NW) of the midpoint."""
    g0 = ecef(*point_on_path(0.5, 0)[:2], 0)        # ground point at the baseline midpoint
    e, n, u = enu(*point_on_path(0.5, 0)[:2])       # local up (u) at the midpoint
    t = ecef(*TX[:2], 0) - ecef(*RX[:2], 0); t /= np.linalg.norm(t)   # unit vector along baseline, RX -> TX
    side = np.cross(u, t); side /= np.linalg.norm(side)               # horizontal unit vector perpendicular to baseline
    p = g0 + x_km * 1e3 * t + y_km * 1e3 * side     # displaced ground point (ECEF)
    return geodetic(p / np.linalg.norm(p), alt_m)


def heading_windows(P, desc_deg):
    """Headings (deg) that give f_D=0 and the +-LIM edges, for a given descent angle. Returns list of (az0, az_lo, az_hi)."""
    e, n, u = enu(P[0], P[1])
    b, _, _ = bisector(P)
    be, bn, bu = b @ e, b @ n, b @ u
    bh, azb = np.hypot(be, bn), np.degrees(np.arctan2(be, bn))   # horizontal magnitude and azimuth of b
    d = np.radians(desc_deg)
    # f_D = 0 requires cos(heading - azb) = c0; the +-LIM edges shift that cosine by +-dc
    c0 = bu * np.tan(d) / bh
    dc = LIM * LAM / (V * np.cos(d)) / bh
    res = []
    for sgn in (+1, -1):               # the two mirror-image headings on either side of azb
        out = []
        for c in (c0, c0 - dc, c0 + dc):   # centre (0 Hz), then the two band edges
            # nan if no heading satisfies it (|cos| > 1)
            out.append((azb + sgn * np.degrees(np.arccos(c))) % 360 if abs(c) <= 1 else np.nan)
        res.append(tuple(out))
    return res


if __name__ == "__main__":
    base = np.linalg.norm(ecef(*TX[:2], 0) - ecef(*RX[:2], 0)) / 1e3
    print(f"lambda = {LAM:.4f} m, v = {V:.0f} m/s, v/lambda = {V/LAM:.1f} Hz per unit; ground baseline = {base:.1f} km")

    # Where are the reflection points?  100 km altitude over the midpoint, plus spread
    P0 = point_on_path(0.5, 100e3)       # reference reflection point: baseline midpoint at 100 km altitude
    b, uT, uR = bisector(P0)
    beta =np.degrees(np.arccos(np.clip(-uT @ uR * -1, -1, 1)))  # angle between uT,uR
    print(f"Midpoint {P0[0]:.3f},{P0[1]:.3f} @100 km: |b| = {np.linalg.norm(b):.3f}, "
          f"max |f_D| = {V/LAM*np.linalg.norm(b):.0f} Hz")
    # fraction of directions on the sphere within +-100 Hz
    k = LIM * LAM / (V * np.linalg.norm(b))   # limit on |vhat . bhat| for |f_D| <= LIM
    print(f"|cos(angle to bisector)| <= {k:.4f}  -> +-{np.degrees(np.arcsin(k)):.2f} deg of tangent plane; "
          f"{k*100:.1f}% of random directions")

    az = np.arange(0, 360, 5.0)     # headings evaluated, every 5 deg
    rows = []                       # CSV rows: (case, heading, zero-Doppler descent, band lo, band hi)
    # name -> (fraction of the way from TX to RX, altitude in m) for each reflection-point case
    cases = {"midpoint 100 km": (0.5, 100e3), "80 km alt": (0.5, 80e3), "120 km alt": (0.5, 120e3),
             "1/4 from TX": (0.25, 100e3), "1/4 from RX": (0.75, 100e3)}
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    ax = axs[0]                     # left panel: zero-Doppler curves for each case
    for (name, (fr, alt)), col in zip(cases.items(), ["k", "tab:blue", "tab:green", "tab:red", "tab:orange"]):
        P = point_on_path(fr, alt)
        zd = zero_doppler_desc(P, az)    # descent angle giving 0 Hz at each heading
        bw = band_halfwidth(P, az)       # (lo, hi) descent range giving |f| <= LIM at each heading
        ax.plot(az, zd, color=col, label=name)                                   # zero-Doppler line
        ax.fill_between(az, bw[:, 0], bw[:, 1], color=col, alpha=0.12)           # shaded +-LIM band
        for a, z, (lo, hi) in zip(az, zd, bw):
            rows.append((name, a, z, lo, hi))
    ax.set_xlim(0, 360); ax.set_ylim(0, 90); ax.set_xticks(range(0, 361, 45))
    ax.set_xlabel("meteor heading, deg (direction of travel, from N)")
    ax.set_ylabel("descent angle below horizontal, deg")
    # ax.set_title(f"Zero-Doppler line (shaded: |f| <= {LIM:.0f} Hz), WDPN 54.31 MHz, {V_KMS:g} km/s") # this is for K1FR to WDPN TV
    ax.set_title(f"Zero-Doppler line (shaded: |f| <= {LIM:.0f} Hz), TX QTH 50 MHz, {V_KMS:g} km/s") # this is a made up TX QTH for Rob

    ax.grid(alpha=0.3); ax.legend(fontsize=8)

    ax = axs[1]                     # right panel: Doppler map over all headings/descents at P0
    P = P0
    A_, D_ = np.meshgrid(np.arange(0, 360.5, 1), np.arange(0, 90.5, 1))   # heading / descent grids (1 deg)
    Fd = doppler(P, A_, D_)         # Doppler (Hz) at every grid point
    cs = ax.pcolormesh(A_, D_, Fd, cmap="RdBu_r", vmin=-2000, vmax=2000, shading="auto")
    ax.contour(A_, D_, Fd, levels=[-LIM, LIM], colors="k", linewidths=1.2)
    ax.contour(A_, D_, Fd, levels=[0], colors="k", linewidths=0.8, linestyles="--")
    plt.colorbar(cs, ax=ax, label="Doppler, Hz (+ = path shortening)")
    ax.set_xlabel("heading, deg"); ax.set_ylabel("descent angle, deg")
    ax.set_title("Doppler over all headings/descents at the midpoint, 100 km (black = ±100 Hz)")
    ax.set_xticks(range(0, 361, 45))
    fig.tight_layout(); fig.savefig(f"meteor_doppler_wdpn_{TAG}.png", dpi=130)

    with open(f"meteor_doppler_wdpn_{TAG}.csv", "w") as fh:
        fh.write("case,heading_deg,zero_doppler_descent_deg,desc_lo_deg_for_pm100Hz,desc_hi_deg_for_pm100Hz\n")
        for r in rows:
            fh.write(",".join(str(round(x, 2)) if not isinstance(x, str) else x for x in r) + "\n")

    print("\nMidpoint, 100 km altitude:  heading -> descent angle for 0 Hz, and range for +-100 Hz")
    zd = zero_doppler_desc(P0, az); bw = band_halfwidth(P0, az)
    for a, z, (lo, hi) in zip(az[::6], zd[::6], bw[::6]):
        print(f"  {a:5.0f}°  zero at {z:5.1f}°   ±100 Hz: {lo:5.1f}–{hi:5.1f}°")

    print("\nReflection point off the baseline (alt 100 km, midpoint along path). y>0 = NW side, y<0 = SE side")
    print("  y_km  desc  heading(0 Hz)  +-100 Hz window   (two mirror-image solutions per row)")
    lines = []                      # collected (y_km, descent, windows) results
    for y in (-200, -150, -100, -50, 50, 100, 150, 200):
        P = P_offset(0, y, 100e3)
        for dsc in (20, 30, 45, 60):
            w = heading_windows(P, dsc)
            if np.isnan(w[0][0]):
                continue
            txt = "  |  ".join(f"{a0:5.1f}  ({lo:5.1f}..{hi:5.1f})" for a0, lo, hi in w)
            print(f"  {y:5d} {dsc:4d}   {txt}")
            lines.append((y, dsc, w))
