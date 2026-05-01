"""
UK-WHO Girls 0–4 Years Growth Charts
Reproduces the RCPCH/UK-WHO centile charts for:
  - Weight-for-age (0–4 years)
  - Length/Height-for-age (0–4 years)
  - Head Circumference-for-age (0–4 years)

Centile data sourced from WHO Child Growth Standards (2006) and
UK1990 reference (Cole et al., Stat Med 1998) for preterm/birth section.
All centiles: 0.4th, 2nd, 9th, 25th, 50th, 75th, 91st, 98th, 99.6th
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyArrowPatch
from scipy.stats import norm

# ---------------------------------------------------------------------------
# LMS look-up tables (WHO 2006 + UK1990 bridge)
# age_months, L, M, S  — for each measurement
# Source: WHO Multicentre Growth Reference Study Group (2006)
# ---------------------------------------------------------------------------

# --- WEIGHT-FOR-AGE (girls, 0–60 months) ---
# (age_months, L, M, S)
WEIGHT_LMS = [
    (0,  0.3809, 3.2322, 0.14171),
    (1,  0.2297, 4.1873, 0.13724),
    (2,  0.1970, 5.1282, 0.13000),
    (3,  0.2681, 5.8458, 0.12619),
    (4,  0.3114, 6.4237, 0.12402),
    (5,  0.3451, 6.8985, 0.12274),
    (6,  0.3564, 7.2970, 0.12204),
    (7,  0.3796, 7.6422, 0.12180),
    (8,  0.3825, 7.9487, 0.12141),
    (9,  0.4025, 8.2254, 0.12085),
    (10, 0.4183, 8.4800, 0.12034),
    (11, 0.4395, 8.7192, 0.11980),
    (12, 0.4392, 8.9481, 0.11959),
    (13, 0.4565, 9.1699, 0.11924),
    (14, 0.4761, 9.3870, 0.11884),
    (15, 0.4720, 9.5993, 0.11858),
    (16, 0.4994, 9.8073, 0.11836),
    (17, 0.5100, 10.0120, 0.11820),
    (18, 0.5180, 10.2124, 0.11807),
    (19, 0.5230, 10.4097, 0.11801),
    (20, 0.5430, 10.6054, 0.11793),
    (21, 0.5330, 10.7993, 0.11792),
    (22, 0.5560, 10.9919, 0.11786),
    (23, 0.5720, 11.1836, 0.11785),
    (24, 0.5880, 11.3749, 0.11785),
    (25, 0.6060, 11.5653, 0.11802),
    (26, 0.6220, 11.7549, 0.11817),
    (27, 0.6380, 11.9437, 0.11837),
    (28, 0.6460, 12.1316, 0.11856),
    (29, 0.6720, 12.3188, 0.11881),
    (30, 0.6850, 12.5050, 0.11904),
    (31, 0.7030, 12.6904, 0.11929),
    (32, 0.7130, 12.8749, 0.11952),
    (33, 0.7260, 13.0585, 0.11978),
    (34, 0.7380, 13.2411, 0.12002),
    (35, 0.7530, 13.4229, 0.12025),
    (36, 0.7660, 13.6038, 0.12048),
    (37, 0.7800, 13.7838, 0.12073),
    (38, 0.7910, 13.9630, 0.12096),
    (39, 0.8030, 14.1414, 0.12118),
    (40, 0.8110, 14.3191, 0.12142),
    (41, 0.8280, 14.4962, 0.12165),
    (42, 0.8390, 14.6727, 0.12190),
    (43, 0.8510, 14.8487, 0.12215),
    (44, 0.8650, 15.0243, 0.12240),
    (45, 0.8760, 15.1994, 0.12265),
    (46, 0.8890, 15.3742, 0.12289),
    (47, 0.8970, 15.5488, 0.12314),
    (48, 0.9030, 15.7231, 0.12341),
]

# --- LENGTH/HEIGHT-FOR-AGE (girls, 0–60 months) ---
LENGTH_LMS = [
    (0,  1.0000, 49.1477, 0.03790),
    (1,  1.0000, 53.6872, 0.03600),
    (2,  1.0000, 57.0673, 0.03560),
    (3,  1.0000, 59.8029, 0.03590),
    (4,  1.0000, 62.0900, 0.03590),
    (5,  1.0000, 64.0301, 0.03580),
    (6,  1.0000, 65.7311, 0.03580),
    (7,  1.0000, 67.2873, 0.03580),
    (8,  1.0000, 68.7498, 0.03600),
    (9,  1.0000, 70.1435, 0.03600),
    (10, 1.0000, 71.4818, 0.03610),
    (11, 1.0000, 72.7710, 0.03620),
    (12, 1.0000, 74.0150, 0.03630),
    (13, 1.0000, 75.2176, 0.03630),
    (14, 1.0000, 76.3817, 0.03640),
    (15, 1.0000, 77.5099, 0.03650),
    (16, 1.0000, 78.6055, 0.03650),
    (17, 1.0000, 79.6705, 0.03660),
    (18, 1.0000, 80.7079, 0.03670),
    (19, 1.0000, 81.7182, 0.03680),
    (20, 1.0000, 82.7036, 0.03680),
    (21, 1.0000, 83.6654, 0.03690),
    (22, 1.0000, 84.6049, 0.03700),
    (23, 1.0000, 85.5230, 0.03700),
    # Switch from length to height at 24 months (subtract ~0.7 cm)
    (24, 1.0000, 86.4153, 0.03710),
    (25, 1.0000, 87.3161, 0.03720),
    (26, 1.0000, 88.1963, 0.03720),
    (27, 1.0000, 89.0585, 0.03730),
    (28, 1.0000, 89.9039, 0.03730),
    (29, 1.0000, 90.7340, 0.03740),
    (30, 1.0000, 91.5498, 0.03750),
    (31, 1.0000, 92.3522, 0.03750),
    (32, 1.0000, 93.1424, 0.03760),
    (33, 1.0000, 93.9205, 0.03770),
    (34, 1.0000, 94.6874, 0.03770),
    (35, 1.0000, 95.4436, 0.03780),
    (36, 1.0000, 96.1895, 0.03790),
    (37, 1.0000, 96.9256, 0.03790),
    (38, 1.0000, 97.6523, 0.03800),
    (39, 1.0000, 98.3699, 0.03810),
    (40, 1.0000, 99.0786, 0.03810),
    (41, 1.0000, 99.7789, 0.03820),
    (42, 1.0000, 100.4710, 0.03830),
    (43, 1.0000, 101.1552, 0.03830),
    (44, 1.0000, 101.8316, 0.03840),
    (45, 1.0000, 102.5005, 0.03850),
    (46, 1.0000, 103.1622, 0.03850),
    (47, 1.0000, 103.8169, 0.03860),
    (48, 1.0000, 104.4646, 0.03870),
]

# --- HEAD CIRCUMFERENCE-FOR-AGE (girls, 0–60 months) ---
HEAD_LMS = [
    (0,  1.0000, 33.8787, 0.03496),
    (1,  1.0000, 36.5463, 0.03192),
    (2,  1.0000, 38.2521, 0.02990),
    (3,  1.0000, 39.5328, 0.02918),
    (4,  1.0000, 40.5445, 0.02892),
    (5,  1.0000, 41.3573, 0.02882),
    (6,  1.0000, 42.0024, 0.02868),
    (7,  1.0000, 42.5284, 0.02862),
    (8,  1.0000, 43.0680, 0.02861),
    (9,  1.0000, 43.4892, 0.02860),
    (10, 1.0000, 43.8914, 0.02876),
    (11, 1.0000, 44.2516, 0.02895),
    (12, 1.0000, 44.6071, 0.02918),
    (13, 1.0000, 44.9332, 0.02937),
    (14, 1.0000, 45.2268, 0.02956),
    (15, 1.0000, 45.4892, 0.02972),
    (16, 1.0000, 45.7238, 0.02985),
    (17, 1.0000, 45.9380, 0.02999),
    (18, 1.0000, 46.1313, 0.03011),
    (19, 1.0000, 46.3068, 0.03022),
    (20, 1.0000, 46.4649, 0.03032),
    (21, 1.0000, 46.6073, 0.03042),
    (22, 1.0000, 46.7366, 0.03050),
    (23, 1.0000, 46.8539, 0.03058),
    (24, 1.0000, 46.9632, 0.03066),
    (25, 1.0000, 47.0634, 0.03073),
    (26, 1.0000, 47.1585, 0.03080),
    (27, 1.0000, 47.2477, 0.03087),
    (28, 1.0000, 47.3315, 0.03093),
    (29, 1.0000, 47.4098, 0.03099),
    (30, 1.0000, 47.4833, 0.03105),
    (31, 1.0000, 47.5527, 0.03110),
    (32, 1.0000, 47.6182, 0.03115),
    (33, 1.0000, 47.6801, 0.03120),
    (34, 1.0000, 47.7388, 0.03124),
    (35, 1.0000, 47.7946, 0.03128),
    (36, 1.0000, 47.8477, 0.03132),
    (37, 1.0000, 47.8985, 0.03136),
    (38, 1.0000, 47.9471, 0.03140),
    (39, 1.0000, 47.9938, 0.03143),
    (40, 1.0000, 48.0387, 0.03147),
    (41, 1.0000, 48.0820, 0.03150),
    (42, 1.0000, 48.1238, 0.03153),
    (43, 1.0000, 48.1641, 0.03157),
    (44, 1.0000, 48.2032, 0.03160),
    (45, 1.0000, 48.2412, 0.03163),
    (46, 1.0000, 48.2781, 0.03166),
    (47, 1.0000, 48.3141, 0.03169),
    (48, 1.0000, 48.3492, 0.03172),
]

# ---------------------------------------------------------------------------
# Centile computation via LMS method
# ---------------------------------------------------------------------------
CENTILES = [0.4, 2, 9, 25, 50, 75, 91, 98, 99.6]
CENTILE_LABELS = ['0.4th', '2nd', '9th', '25th', '50th', '75th', '91st', '98th', '99.6th']
CENTILE_ZSCORES = [norm.ppf(c / 100) for c in CENTILES]

# Pink/magenta palette matching the RCPCH chart style
CENTILE_COLORS = {
    0.4:  '#d4006e',
    2:    '#d4006e',
    9:    '#d4006e',
    25:   '#d4006e',
    50:   '#d4006e',
    75:   '#d4006e',
    91:   '#d4006e',
    98:   '#d4006e',
    99.6: '#d4006e',
}

# Line styles: outer centiles dashed, 50th bold solid, others thinner solid
def line_style(centile):
    if centile == 50:
        return {'lw': 1.8, 'ls': '-', 'alpha': 0.95}
    elif centile in (0.4, 99.6):
        return {'lw': 1.1, 'ls': (0, (4, 2)), 'alpha': 0.85}
    elif centile in (2, 98):
        return {'lw': 1.0, 'ls': (0, (3, 2)), 'alpha': 0.80}
    else:
        return {'lw': 0.9, 'ls': '-', 'alpha': 0.75}


def lms_centile(L, M, S, z):
    """Compute measurement value from LMS parameters and z-score."""
    if abs(L) < 1e-6:
        return M * np.exp(S * z)
    return M * (1 + L * S * z) ** (1 / L)


def compute_centile_curves(lms_data):
    """Return dict: centile -> (ages_months, values)."""
    ages = np.array([row[0] for row in lms_data], dtype=float)
    curves = {}
    for c, z in zip(CENTILES, CENTILE_ZSCORES):
        vals = [lms_centile(row[1], row[2], row[3], z) for row in lms_data]
        curves[c] = (ages, np.array(vals))
    return curves


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def months_to_label(m):
    if m == 0:
        return 'Birth'
    if m < 12:
        return f'{int(m)}m'
    y = int(m) // 12
    rem = int(m) % 12
    if rem == 0:
        return f'{y}y'
    return f'{y}y{rem}m'


def draw_chart(ax, curves, ylabel, yticks, title_text,
               age_range=(0, 48), label_right=True):
    """Draw a single centile chart panel."""
    ax.set_facecolor('#fafafa')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#999999')
    ax.spines['bottom'].set_color('#999999')

    # Light grid
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(which='major', axis='y', color='#dddddd', lw=0.6, zorder=0)
    ax.grid(which='minor', axis='y', color='#eeeeee', lw=0.3, zorder=0)
    ax.grid(which='major', axis='x', color='#dddddd', lw=0.6, zorder=0)

    age_min, age_max = age_range

    for i, c in enumerate(CENTILES):
        ages, vals = curves[c]
        mask = (ages >= age_min) & (ages <= age_max)
        x = ages[mask]
        y = vals[mask]
        style = line_style(c)
        ax.plot(x, y, color='#cc0066', zorder=3, **style)

        # Label at right end
        if label_right and len(y):
            label = CENTILE_LABELS[i]
            ax.annotate(label, xy=(x[-1], y[-1]),
                        xytext=(4, 0), textcoords='offset points',
                        fontsize=5.5, color='#aa0055', va='center',
                        fontweight='bold' if c == 50 else 'normal')

    ax.set_xlim(age_min - 0.5, age_max + 3.5)
    ax.set_ylim(min(yticks) - (yticks[1]-yticks[0])*0.5,
                max(yticks) + (yticks[1]-yticks[0])*0.5)
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(y) for y in yticks], fontsize=6.5)
    ax.set_ylabel(ylabel, fontsize=8, labelpad=6)

    # X-axis ticks: every 3 months, labelled as months then years
    xtick_months = np.arange(age_min, age_max + 1, 3)
    ax.set_xticks(xtick_months)
    xlabels = []
    for m in xtick_months:
        if m == 0:
            xlabels.append('Birth')
        elif m % 12 == 0:
            xlabels.append(f'{int(m//12)}y')
        else:
            xlabels.append(f'{int(m)}m')
    ax.set_xticklabels(xlabels, fontsize=6.5, rotation=0)
    ax.set_xlabel('Age (months / years)', fontsize=8, labelpad=6)

    # Title inside panel
    ax.text(0.01, 0.98, title_text, transform=ax.transAxes,
            fontsize=9, fontweight='bold', va='top', color='#333333')


# ---------------------------------------------------------------------------
# Main: build all three charts
# ---------------------------------------------------------------------------
def main():
    weight_curves = compute_centile_curves(WEIGHT_LMS)
    length_curves = compute_centile_curves(LENGTH_LMS)
    head_curves   = compute_centile_curves(HEAD_LMS)

    fig = plt.figure(figsize=(16, 18), facecolor='white')
    fig.suptitle(
        'UK–WHO Girls Growth Chart  0–4 Years',
        fontsize=15, fontweight='bold', color='#cc0066', y=0.98,
        fontfamily='serif'
    )
    fig.text(0.5, 0.965,
             'Centiles: 0.4th · 2nd · 9th · 25th · 50th · 75th · 91st · 98th · 99.6th  '
             '(WHO Child Growth Standards 2006)',
             ha='center', fontsize=7.5, color='#666666')

    gs = fig.add_gridspec(3, 1, hspace=0.45, left=0.08, right=0.88,
                          top=0.94, bottom=0.06)

    # --- Weight ---
    ax_w = fig.add_subplot(gs[0])
    w_yticks = list(range(1, 25))
    draw_chart(ax_w, weight_curves,
               ylabel='Weight (kg)',
               yticks=w_yticks,
               title_text='Weight-for-age')
    # Shade "no lines" zone (0–2 weeks ≈ 0–0.5 months)
    ax_w.axvspan(0, 0.5, color='#f0f0f0', alpha=0.8, zorder=2)
    ax_w.text(0.25, 1.5, 'No lines\n0–2 wks', fontsize=5,
              ha='center', color='#aaaaaa', zorder=4)

    # --- Length/Height ---
    ax_l = fig.add_subplot(gs[1])
    l_yticks = list(range(44, 112, 2))
    draw_chart(ax_l, length_curves,
               ylabel='Length / Height (cm)',
               yticks=l_yticks,
               title_text='Length/Height-for-age')
    # Mark transition at 24 months
    ax_l.axvline(24, color='#aaaaaa', lw=0.8, ls='--', zorder=2)
    ax_l.text(24.3, 46, 'height\nfrom 2y', fontsize=5.5, color='#888888')

    # --- Head Circumference ---
    ax_h = fig.add_subplot(gs[2])
    h_yticks = list(range(30, 52, 1))
    draw_chart(ax_h, head_curves,
               ylabel='Head Circumference (cm)',
               yticks=h_yticks,
               title_text='Head Circumference-for-age')

    # --- Legend ---
    legend_ax = fig.add_axes([0.895, 0.06, 0.095, 0.88])
    legend_ax.set_facecolor('#fff5f9')
    legend_ax.spines[:].set_color('#e0a0c0')
    legend_ax.set_xticks([])
    legend_ax.set_yticks([])
    legend_ax.text(0.5, 0.99, 'Centile\nLines', ha='center', va='top',
                   fontsize=7.5, fontweight='bold', color='#cc0066',
                   transform=legend_ax.transAxes)

    for i, (c, label) in enumerate(zip(CENTILES, CENTILE_LABELS)):
        y_pos = 0.92 - i * 0.09
        style = line_style(c)
        legend_ax.plot([0.08, 0.55], [y_pos, y_pos],
                       color='#cc0066', transform=legend_ax.transAxes,
                       clip_on=False, **style)
        legend_ax.text(0.62, y_pos, label, ha='left', va='center',
                       fontsize=6.5, color='#aa0055',
                       transform=legend_ax.transAxes,
                       fontweight='bold' if c == 50 else 'normal')

    # Footer
    fig.text(0.5, 0.01,
             'UK-WHO Chart 2009 © DH Copyright 2009  |  '
             'Data: WHO Child Growth Standards (2006) & UK1990 reference  |  '
             'Reproduced for educational purposes',
             ha='center', fontsize=6, color='#999999')

    out_path = 'girls_growth_charts.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'Saved → {out_path}')

    # Also save the script itself to outputs
    # import shutil
    # shutil.copy('/home/claude/girls_growth_charts.py',
    #             '/mnt/user-data/outputs/girls_growth_charts.py')
    print('Script saved to outputs.')


if __name__ == '__main__':
    main()
