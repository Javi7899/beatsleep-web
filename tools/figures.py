#!/usr/bin/env python3
"""Draws the figures the site uses, from one night's worth of made-up data.

The app draws these with a SwiftUI Canvas from the wearer's own night. A web
page has no night to draw, so it draws one night, kept here so the shapes stay
honest: the same stage depths, the same clockwise dial, the same rule that
depth is distance from the rim. Nothing here is a screenshot of the app, and
nothing here is a measurement of anybody.

    python3 tools/figures.py     writes assets/figures/*.svg

The palette is the app's own OKLCH numbers, converted to sRGB here rather than
written as oklch() in the file, because these are <img> and an old browser that
does not know the function has nowhere to fall back to.
"""

import math, os

# ----------------------------------------------------------------- colour ---

def oklch(L, C, h, a=1.0):
    """OKLCH -> #rrggbb (or rgba()), the same conversion the app's palette uses."""
    hr = math.radians(h)
    a_, b_ = C * math.cos(hr), C * math.sin(hr)
    l_ = L + 0.3963377774 * a_ + 0.2158037573 * b_
    m_ = L - 0.1055613458 * a_ - 0.0638541728 * b_
    s_ = L - 0.0894841775 * a_ - 1.2914855480 * b_
    l, m, s = l_**3, m_**3, s_**3
    r = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bl = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    def enc(u):
        u = max(0.0, min(1.0, u))
        u = 12.92*u if u <= 0.0031308 else 1.055*u**(1/2.4) - 0.055
        return int(round(u * 255))
    rgb = (enc(r), enc(g), enc(bl))
    if a >= 1:
        return "#%02x%02x%02x" % rgb
    return "rgba(%d,%d,%d,%.3f)" % (rgb + (a,))

HUE = 282
ACCENT   = oklch(0.74, 0.10, HUE)
ACCENT_D = oklch(0.62, 0.09, HUE)
ACCENT_L = oklch(0.86, 0.06, HUE)
WARM     = oklch(0.78, 0.09, 62)
GROUND   = "#000000"

def wash(alpha):     return "rgba(255,255,255,%.3f)" % alpha

# ------------------------------------------------------------------ night ---
# One night, as stages. (minutes, stage) where stage is one of
# awake / rem / core / deep, the four HealthKit hands back.

NIGHT = [
    (14, "awake"),                      # falling asleep
    (12, "core"), (34, "deep"), (18, "core"), (17, "rem"),
    (5,  "awake"),                      # a surfacing at the end of cycle one
    (22, "core"), (26, "deep"), (14, "core"), (21, "rem"),
    (3,  "awake"),
    (30, "core"), (12, "deep"), (16, "core"), (26, "rem"),
    (6,  "awake"),
    (24, "core"), (31, "rem"), (9, "core"), (28, "rem"),
    (11, "awake"),                      # morning
]

DEPTH = {"awake": 0.06, "rem": 0.44, "core": 0.66, "deep": 1.0}
TOTAL = sum(m for m, _ in NIGHT)

def minute_stage():
    out = []
    for mins, stage in NIGHT:
        out.extend([stage] * mins)
    return out

STAGES = minute_stage()

def heart_at(t):
    """A plausible pulse curve, 0..1 across the night. Low in the deep stretches,
    up on every surfacing, and climbing again towards morning."""
    base = 58 - 9 * math.sin(math.pi * min(t * 1.15, 1.0))      # the long trough
    cycle = 1.6 * math.sin(t * math.pi * 8.5)                    # ultradian ripple
    stage = STAGES[min(int(t * TOTAL), TOTAL - 1)]
    lift = {"awake": 7.5, "rem": 2.6, "core": 0.0, "deep": -1.8}[stage]
    return base + cycle + lift

# -------------------------------------------------------------- nightprint ---

def nightprint(path, size=420, rim=190, hub=54, pulse=True):
    c = size / 2
    spokes, deeps = [], []
    step = 2                                    # a spoke every two minutes
    for i in range(0, TOTAL, step):
        t = i / TOTAL
        ang = math.radians(-90 + t * 360)       # midnight at the top, clockwise
        d = DEPTH[STAGES[i]]
        r_in = rim - (rim - hub) * d
        x1, y1 = c + rim * math.cos(ang), c + rim * math.sin(ang)
        x2, y2 = c + r_in * math.cos(ang), c + r_in * math.sin(ang)
        seg = "M%.1f %.1fL%.1f %.1f" % (x1, y1, x2, y2)
        (deeps if d > 0.8 else spokes).append(seg)

    raw = [heart_at(i / TOTAL) for i in range(TOTAL)]
    span = 9                                     # smoothed, because a thread that
    sm = []                                      # jags is a thread that reads as noise
    for i in range(TOTAL):
        lo_i, hi_i = max(0, i - span), min(TOTAL, i + span + 1)
        sm.append(sum(raw[lo_i:hi_i]) / (hi_i - lo_i))
    hi, lo = max(sm), min(sm)
    pts = []
    for i in range(0, TOTAL, 4):
        ang = math.radians(-90 + (i / TOTAL) * 360)
        k = (sm[i] - lo) / (hi - lo)             # slowest heart, closest to the centre
        r = hub + 8 + (rim - hub - 30) * k
        pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
    thread = ["M%.1f %.1f" % pts[0]]
    for j in range(1, len(pts) - 1):             # midpoint quadratics: one smooth line
        mx = (pts[j][0] + pts[j + 1][0]) / 2
        my = (pts[j][1] + pts[j + 1][1]) / 2
        thread.append("Q%.1f %.1f %.1f %.1f" % (pts[j][0], pts[j][1], mx, my))
    thread.append("L%.1f %.1f" % pts[-1])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="One night drawn as a circle: it starts at the top and runs clockwise to morning, and each spoke reaches inward as far as that minute was deep.">
  <circle cx="{c}" cy="{c}" r="{rim}" fill="none" stroke="{wash(0.10)}" stroke-width="1"/>
  <circle cx="{c}" cy="{c}" r="{hub}" fill="none" stroke="{wash(0.06)}" stroke-width="1"/>
  <path d="{''.join(spokes)}" stroke="{ACCENT_D}" stroke-width="2.1" stroke-linecap="round" opacity="0.72"/>
  <path d="{''.join(deeps)}" stroke="{ACCENT}" stroke-width="2.4" stroke-linecap="round" opacity="0.95"/>'''
    if pulse:
        svg += f'\n  <path d="{"".join(thread)}" fill="none" stroke="{wash(0.55)}" stroke-width="1.4" stroke-linejoin="round"/>'
    svg += "\n</svg>\n"
    open(path, "w").write(svg)

# --------------------------------------------------------------- hypnogram ---

def hypnogram(path, w=760, h=190):
    order = ["awake", "rem", "core", "deep"]
    top, bot = 18, h - 30
    lane = (bot - top) / (len(order) - 1)
    y = {s: top + i * lane for i, s in enumerate(order)}

    pts, x0 = [], 0.0
    for mins, stage in NIGHT:
        x1 = x0 + mins / TOTAL * w
        pts.append((x0, x1, stage))
        x0 = x1

    steps = []
    prev = None
    for x1, x2, stage in pts:
        yy = y[stage]
        if prev is not None:
            steps.append("L%.1f %.1f" % (x1, yy))
        else:
            steps.append("M%.1f %.1f" % (x1, yy))
        steps.append("L%.1f %.1f" % (x2, yy))
        prev = yy

    fills = []
    for x1, x2, stage in pts:
        if stage == "deep":
            fills.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.16" rx="2"/>'
                         % (x1, y["deep"] - 6, max(x2 - x1, 1.2), 12, ACCENT))
        if stage == "awake":
            fills.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.5" rx="1.5"/>'
                         % (x1, y["awake"] - 5, max(x2 - x1, 1.6), 10, WARM))

    rails = "".join('<line x1="0" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                    % (y[s], w, y[s], wash(0.055)) for s in order)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="The same night as a timeline of stages, from awake at the top to deep sleep at the bottom: four cycles, with brief surfacings between them.">
  {rails}
  {''.join(fills)}
  <path d="{''.join(steps)}" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
</svg>
'''
    open(path, "w").write(svg)

# ------------------------------------------------------------ ten weeks -----

# Ten weeks of scores, 0..1, made up but shaped like a life: a bad fortnight,
# a slow recovery, one hopeless Tuesday. None is a value the app promises.
WEEKS = [
    [.42,.38,.55,.30,.47,.68,.61],
    [.35,.44,.29,.52,.40,.71,.66],
    [.50,.46,.58,.41,.55,.74,.70],
    [.57,.62,.49,.60,.53,.78,.72],
    [.61,.58,.66,.55,.64,.80,.75],
    [.66,.70,.59,.68,.62,.83,.79],
    [.72,.68,.74,.12,.70,.85,.81],
    [.75,.79,.71,.77,.73,.88,.84],
    [.80,.76,.82,.74,.81,.86,.83],
    [.84,.81,.86,.79,.85,None,None],
]

def weeks(path, cell=26, gap=6, pad=1):
    cols, rows = len(WEEKS), 7
    w = cols * cell + (cols - 1) * gap + pad * 2
    h = rows * cell + (rows - 1) * gap + pad * 2
    out = []
    for ci, week in enumerate(WEEKS):
        for ri, v in enumerate(week):
            x = pad + ci * (cell + gap)
            y = pad + ri * (cell + gap)
            if v is None:                        # a night with nothing recorded
                out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="7" fill="none" stroke="%s" stroke-width="1"/>'
                           % (x, y, cell, cell, wash(0.14)))
                continue
            # Shaded by lightness, never by hue: a dark square is a bad night,
            # which survives any colour vision.
            fill = oklch(0.20 + 0.64 * v, 0.02 + 0.085 * v, HUE)
            out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="7" fill="%s"/>'
                       % (x, y, cell, cell, fill))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Ten weeks of nights as a grid, one square a night, shaded by lightness: the darker the square the worse the night, and an outline is a night with nothing recorded.">
  {''.join(out)}
</svg>
'''
    open(path, "w").write(svg)

# ------------------------------------------------------------------ descent --

def descent(path, w=760, h=230):
    """Twenty-five minutes: the wearer's pulse, and the cadence held just under it.

    Simulated rather than drawn by hand, so the shape obeys the app's own two
    rules: the cadence sheds four beats every ten minutes, and it lets go and
    re-anchors when the pulse climbs. The cadence is dashed and the pulse
    solid, so the two are told apart without colour, which is the rule the
    app's own chart follows."""
    left, right, top, bot = 8, w - 8, 24, h - 30
    span, lo_bpm, hi_bpm = 25.0, 53.0, 70.0
    def X(t):   return left + (right - left) * (t / span)
    def Y(bpm): return top + (bot - top) * (hi_bpm - bpm) / (hi_bpm - lo_bpm)

    dt, anchor, floor = 0.05, 67.0, 55.5
    pulse_pts, cad_pts = [], []
    cad, p, conv_t, conv_bpm = anchor - 2.0, anchor, None, 0.0
    t, pulse_at_end = 0.0, anchor
    while t <= span + 1e-9:
        # The cadence is a schedule: four beats every ten minutes, never below
        # the floor. The pulse is not driven; it follows, with a lag.
        cad = max(cad - 0.4 * dt, floor)
        restless = 8.0 * math.exp(-((t - 8.0) ** 2) / 0.30)      # a turn, at eight minutes
        p += (0.34 * (cad - p) + restless) * dt
        p += 0.09 * math.sin(t * 2.6) + 0.05 * math.sin(t * 6.1)
        if p - cad > 5.0:                                        # too far to be followed:
            cad += min((p - 2.0) - cad, 9.0 * dt)                # let go, and climb back
        if conv_t is None or (7.0 < t < 9.5 and p > conv_bpm):
            conv_t, conv_bpm = t, p                              # the turn, for the marker
        pulse_at_end = p
        pulse_pts.append((X(t), Y(p)))
        cad_pts.append((X(t), Y(cad)))
        t += dt

    def path_of(pts):
        return "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % q for q in pts[1:])

    rails = "".join('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                    % (left, Y(b), right, Y(b), wash(0.05)) for b in (68, 64, 60, 56))
    cx, cy = X(conv_t), Y(conv_bpm)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Twenty-five minutes. The solid line is the wearer\u2019s pulse; the dashed line is the taptic cadence, held just below it and shedding four beats every ten minutes. At eight minutes the pulse climbs, the cadence lets go and re-anchors, and then both fall again.">
  {rails}
  <line x1="{cx:.1f}" y1="{top}" x2="{cx:.1f}" y2="{bot}" stroke="{wash(0.14)}" stroke-width="1" stroke-dasharray="2 4"/>
  <path d="{path_of(cad_pts)}" fill="none" stroke="{ACCENT}" stroke-width="2.2" stroke-dasharray="7 5" stroke-linecap="round"/>
  <path d="{path_of(pulse_pts)}" fill="none" stroke="{wash(0.86)}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="none" stroke="{ACCENT}" stroke-width="1" opacity="0.5"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.6" fill="{ACCENT}"/>
</svg>
'''
    open(path, "w").write(svg)

# ------------------------------------------------------------------ record --

# Three weeks of "how long it took to go under", in minutes. Made up, and
# shaped like a record that is slowly improving without ever being tidy.
UNDER = [23,19,26,17,21,14,16,22,13,18,11,15,20,12,14,9,13,16,10,12,8]

def record(path, w=760, h=230):
    """The record of how long each night took to go under, with your median.

    The same figure the app draws in its history sheet: one bar a night, and
    one dashed line at the median, which is the number the eye should land on.
    The bars are a gradient down into the ground the way the app's are."""
    left, right, top, bot = 34, w - 8, 26, h - 26
    hi = 28.0
    n = len(UNDER)
    slot = (right - left) / n
    bw = slot * 0.56
    def Y(m): return top + (bot - top) * (1 - m / hi)

    bars = []
    for i, m in enumerate(UNDER):
        x = left + i * slot + (slot - bw) / 2
        y = Y(m)
        bars.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="url(#bar)"/>'
                    % (x, y, bw, bot - y))

    med = sorted(UNDER)[n // 2]
    my = Y(med)
    rails = "".join('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="1"/>'
                    % (left, Y(m), right, Y(m), wash(0.05)) for m in (10, 20))
    ticks = "".join('<text x="%d" y="%.1f" fill="%s" font-size="10" font-family="ui-sans-serif,system-ui,sans-serif" text-anchor="end">%dm</text>'
                    % (left - 8, Y(m) + 3.5, wash(0.38), m) for m in (10, 20))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Three weeks of nights as bars: how many minutes each one took to go under, falling slowly, with a dashed line across them at the median.">
  <defs><linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{ACCENT_L}"/><stop offset="1" stop-color="{oklch(0.44, 0.08, HUE, 0.5)}"/>
  </linearGradient></defs>
  {rails}
  {''.join(bars)}
  <line x1="{left}" y1="{my:.1f}" x2="{right}" y2="{my:.1f}" stroke="{wash(0.32)}" stroke-width="1" stroke-dasharray="3 4"/>
  <text x="{left + 4}" y="{my - 7:.1f}" fill="{wash(0.5)}" font-size="10" font-family="ui-sans-serif,system-ui,sans-serif">median {med} min</text>
  {ticks}
</svg>
'''
    open(path, "w").write(svg)

# --------------------------------------------------------------------- run ---

if __name__ == "__main__":
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figures")
    os.makedirs(here, exist_ok=True)
    nightprint(os.path.join(here, "nightprint.svg"))
    nightprint(os.path.join(here, "nightprint-small.svg"), size=300, rim=134, hub=38, pulse=False)
    hypnogram(os.path.join(here, "hypnogram.svg"))
    weeks(os.path.join(here, "weeks.svg"))
    record(os.path.join(here, "record.svg"))
    descent(os.path.join(here, "descent.svg"))
    print("wrote", os.path.abspath(here))
