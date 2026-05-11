"""
WHO Boys 0–4 Years Growth Charts
Reproduces the WHO centile charts for:
  - Weight-for-age (0–4 years)
  - Length/Height-for-age (0–4 years)
  - Head Circumference-for-age (0–4 years)

Centile data sourced from WHO Child Growth Standards (2006).
All centiles: 0.4th, 2nd, 9th, 25th, 50th, 75th, 91st, 98th, 99.6th
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import norm

# ---------------------------------------------------------------------------
# LMS look-up tables (WHO 2006, boys)
# age_months, L, M, S  — for each measurement
# Source: WHO Multicentre Growth Reference Study Group (2006)
# ---------------------------------------------------------------------------

# --- WEIGHT-FOR-AGE (boys, 0–48 months) ---
WEIGHT_LMS = [
    ( 0,  0.3487,  3.3464, 0.14602),
    ( 1,  0.2297,  4.4709, 0.13395),
    ( 2,  0.1970,  5.5675, 0.12385),
    ( 3,  0.1740,  6.3690, 0.11732),
    ( 4,  0.1553,  7.0023, 0.11316),
    ( 5,  0.1395,  7.5105, 0.11080),
    ( 6,  0.1257,  7.9340, 0.10958),
    ( 7,  0.1134,  8.2970, 0.10902),
    ( 8,  0.1021,  8.6151, 0.10882),
    ( 9,  0.0917,  8.9014, 0.10881),
    (10,  0.0820,  9.1649, 0.10891),
    (11,  0.0730,  9.4122, 0.10906),
    (12,  0.0644,  9.6479, 0.10925),
    (13,  0.0563,  9.8749, 0.10949),
    (14,  0.0487, 10.0953, 0.10976),
    (15,  0.0413, 10.3108, 0.11007),
    (16,  0.0343, 10.5228, 0.11041),
    (17,  0.0275, 10.7319, 0.11079),
    (18,  0.0211, 10.9385, 0.11119),
    (19,  0.0148, 11.1430, 0.11164),
    (20,  0.0087, 11.3462, 0.11211),
    (21,  0.0029, 11.5486, 0.11261),
    (22, -0.0028, 11.7504, 0.11314),
    (23, -0.0083, 11.9514, 0.11369),
    (24, -0.0137, 12.1515, 0.11426),
    (25, -0.0189, 12.3502, 0.11485),
    (26, -0.0240, 12.5466, 0.11544),
    (27, -0.0289, 12.7401, 0.11604),
    (28, -0.0337, 12.9303, 0.11664),
    (29, -0.0385, 13.1169, 0.11723),
    (30, -0.0431, 13.3000, 0.11781),
    (31, -0.0476, 13.4798, 0.11839),
    (32, -0.0520, 13.6567, 0.11896),
    (33, -0.0564, 13.8309, 0.11953),
    (34, -0.0606, 14.0031, 0.12008),
    (35, -0.0648, 14.1736, 0.12062),
    (36, -0.0689, 14.3429, 0.12116),
    (37, -0.0729, 14.5113, 0.12168),
    (38, -0.0769, 14.6791, 0.12220),
    (39, -0.0808, 14.8466, 0.12271),
    (40, -0.0846, 15.0140, 0.12322),
    (41, -0.0883, 15.1813, 0.12373),
    (42, -0.0920, 15.3486, 0.12425),
    (43, -0.0957, 15.5158, 0.12478),
    (44, -0.0993, 15.6828, 0.12531),
    (45, -0.1028, 15.8497, 0.12586),
    (46, -0.1063, 16.0163, 0.12643),
    (47, -0.1097, 16.1827, 0.12700),
    (48, -0.1131, 16.3489, 0.12759),
]


# --- LENGTH/HEIGHT-FOR-AGE (boys, 0–48 months) ---
LENGTH_LMS = [
    ( 0, 1.0000,  49.8842, 0.03795),
    ( 1, 1.0000,  54.7244, 0.03557),
    ( 2, 1.0000,  58.4249, 0.03424),
    ( 3, 1.0000,  61.4013, 0.03329),
    ( 4, 1.0000,  63.8860, 0.03257),
    ( 5, 1.0000,  65.9026, 0.03204),
    ( 6, 1.0000,  67.6236, 0.03165),
    ( 7, 1.0000,  69.1645, 0.03139),
    ( 8, 1.0000,  70.5994, 0.03124),
    ( 9, 1.0000,  71.9687, 0.03117),
    (10, 1.0000,  73.2812, 0.03118),
    (11, 1.0000,  74.5388, 0.03125),
    (12, 1.0000,  75.7488, 0.03137),
    (13, 1.0000,  76.9186, 0.03154),
    (14, 1.0000,  78.0497, 0.03174),
    (15, 1.0000,  79.1458, 0.03197),
    (16, 1.0000,  80.2113, 0.03222),
    (17, 1.0000,  81.2487, 0.03250),
    (18, 1.0000,  82.2587, 0.03279),
    (19, 1.0000,  83.2418, 0.03310),
    (20, 1.0000,  84.1996, 0.03342),
    (21, 1.0000,  85.1348, 0.03376),
    (22, 1.0000,  86.0477, 0.03410),
    (23, 1.0000,  86.9410, 0.03445),
    # Switch from length to height at 24 months (subtract ~0.7 cm)
    (24, 1.0000,  87.8161, 0.03479),
    (25, 1.0000,  87.9720, 0.03542),
    (26, 1.0000,  88.8065, 0.03576),
    (27, 1.0000,  89.6197, 0.03610),
    (28, 1.0000,  90.4120, 0.03642),
    (29, 1.0000,  91.1828, 0.03674),
    (30, 1.0000,  91.9327, 0.03704),
    (31, 1.0000,  92.6631, 0.03733),
    (32, 1.0000,  93.3753, 0.03761),
    (33, 1.0000,  94.0711, 0.03787),
    (34, 1.0000,  94.7532, 0.03812),
    (35, 1.0000,  95.4236, 0.03836),
    (36, 1.0000,  96.0835, 0.03858),
    (37, 1.0000,  96.7337, 0.03879),
    (38, 1.0000,  97.3749, 0.03900),
    (39, 1.0000,  98.0073, 0.03919),
    (40, 1.0000,  98.6310, 0.03937),
    (41, 1.0000,  99.2459, 0.03954),
    (42, 1.0000,  99.8515, 0.03971),
    (43, 1.0000, 100.4485, 0.03986),
    (44, 1.0000, 101.0374, 0.04002),
    (45, 1.0000, 101.6186, 0.04016),
    (46, 1.0000, 102.1933, 0.04031),
    (47, 1.0000, 102.7625, 0.04045),
    (48, 1.0000, 103.3273, 0.04059),
]

# --- HEAD CIRCUMFERENCE-FOR-AGE (boys, 0–48 months) ---
HEAD_LMS = [
    ( 0, 1.0000, 34.4618, 0.03690),
    ( 1, 1.0000, 37.2759, 0.03130),
    ( 2, 1.0000, 39.1285, 0.03000),
    ( 3, 1.0000, 40.5008, 0.02920),
    ( 4, 1.0000, 41.6317, 0.02870),
    ( 5, 1.0000, 42.5576, 0.02840),
    ( 6, 1.0000, 43.3306, 0.02820),
    ( 7, 1.0000, 43.9803, 0.02800),
    ( 8, 1.0000, 44.5300, 0.02800),
    ( 9, 1.0000, 44.9998, 0.02790),
    (10, 1.0000, 45.4051, 0.02790),
    (11, 1.0000, 45.7573, 0.02790),
    (12, 1.0000, 46.0661, 0.02790),
    (13, 1.0000, 46.3395, 0.02790),
    (14, 1.0000, 46.5844, 0.02790),
    (15, 1.0000, 46.8060, 0.02790),
    (16, 1.0000, 47.0088, 0.02800),
    (17, 1.0000, 47.1962, 0.02800),
    (18, 1.0000, 47.3711, 0.02800),
    (19, 1.0000, 47.5357, 0.02800),
    (20, 1.0000, 47.6919, 0.02810),
    (21, 1.0000, 47.8408, 0.02810),
    (22, 1.0000, 47.9833, 0.02810),
    (23, 1.0000, 48.1201, 0.02820),
    (24, 1.0000, 48.2515, 0.02820),
    (25, 1.0000, 48.3777, 0.02830),
    (26, 1.0000, 48.4989, 0.02830),
    (27, 1.0000, 48.6151, 0.02830),
    (28, 1.0000, 48.7264, 0.02840),
    (29, 1.0000, 48.8331, 0.02840),
    (30, 1.0000, 48.9351, 0.02850),
    (31, 1.0000, 49.0327, 0.02850),
    (32, 1.0000, 49.1260, 0.02860),
    (33, 1.0000, 49.2153, 0.02860),
    (34, 1.0000, 49.3007, 0.02860),
    (35, 1.0000, 49.3826, 0.02870),
    (36, 1.0000, 49.4612, 0.02870),
    (37, 1.0000, 49.5367, 0.02880),
    (38, 1.0000, 49.6093, 0.02880),
    (39, 1.0000, 49.6791, 0.02880),
    (40, 1.0000, 49.7465, 0.02890),
    (41, 1.0000, 49.8116, 0.02890),
    (42, 1.0000, 49.8745, 0.02890),
    (43, 1.0000, 49.9354, 0.02900),
    (44, 1.0000, 49.9942, 0.02900),
    (45, 1.0000, 50.0512, 0.02900),
    (46, 1.0000, 50.1064, 0.02910),
    (47, 1.0000, 50.1598, 0.02910),
    (48, 1.0000, 50.2115, 0.02910),
]


# ---------------------------------------------------------------------------
# Centile computation via LMS method
# ---------------------------------------------------------------------------
CENTILES = [0.4, 2, 9, 25, 50, 75, 91, 98, 99.6]
CENTILE_LABELS = ['0.4th', '2nd', '9th', '25th', '50th', '75th', '91st', '98th', '99.6th']
CENTILE_ZSCORES = [norm.ppf(c / 100) for c in CENTILES]

# Blue palette matching the RCPCH boys chart style
LINE_COLOR = '#1f6fb2'
LINE_COLOR_DARK = '#155080'
PANEL_BG = '#f5f8fc'
ACCENT = '#0d3b66'


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
        ax.plot(x, y, color=LINE_COLOR, zorder=3, **style)

        # Label at right end
        if label_right and len(y):
            label = CENTILE_LABELS[i]
            ax.annotate(label, xy=(x[-1], y[-1]),
                        xytext=(4, 0), textcoords='offset points',
                        fontsize=5.5, color=LINE_COLOR_DARK, va='center',
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
        'WHO Boys Growth Chart  0–4 Years',
        fontsize=15, fontweight='bold', color=LINE_COLOR_DARK, y=0.98,
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
    legend_ax.set_facecolor(PANEL_BG)
    legend_ax.spines[:].set_color('#a0c0e0')
    legend_ax.set_xticks([])
    legend_ax.set_yticks([])
    legend_ax.text(0.5, 0.99, 'Centile\nLines', ha='center', va='top',
                   fontsize=7.5, fontweight='bold', color=LINE_COLOR_DARK,
                   transform=legend_ax.transAxes)

    for i, (c, label) in enumerate(zip(CENTILES, CENTILE_LABELS)):
        y_pos = 0.92 - i * 0.09
        style = line_style(c)
        legend_ax.plot([0.08, 0.55], [y_pos, y_pos],
                       color=LINE_COLOR, transform=legend_ax.transAxes,
                       clip_on=False, **style)
        legend_ax.text(0.62, y_pos, label, ha='left', va='center',
                       fontsize=6.5, color=LINE_COLOR_DARK,
                       transform=legend_ax.transAxes,
                       fontweight='bold' if c == 50 else 'normal')

    # Footer
    fig.text(0.5, 0.01,
             'Data: WHO Child Growth Standards (2006)  |  '
             'Reproduced for educational purposes',
             ha='center', fontsize=6, color='#999999')

    out_path = 'boys_growth_charts.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f'Saved → {out_path}')


if __name__ == '__main__':
    main()
