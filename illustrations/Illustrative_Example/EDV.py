# EDV.py — Event-driven rescheduling visuals (FT06, illustrative timings)
# Produces: step1_baseline.png ... step5_committed.png

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib as mpl

# ------------------------------ Config ---------------------------------
EVENT_T = 14         # time when the new job arrives
T_MAX   = 20         # right limit of the timeline
FONT_SZ = 9          # base font size
ANNOT_MIN_WIDTH = 3  # only annotate bars if duration >= this

mpl.rcParams.update({
    "font.size": FONT_SZ,
    "axes.titlesize": FONT_SZ + 1,
    "axes.labelsize": FONT_SZ,
    "xtick.labelsize": FONT_SZ - 1,
    "ytick.labelsize": FONT_SZ - 1,
})

# ---------------------------- Colours/jobs ------------------------------
JCOL = {
    1: "#8dd3c7",
    2: "#fb8072",
    3: "#bebada",
    4: "#80b1d3",
    5: "#fdb462",
    6: "#b3de69",
}
NEW_JOB_COLOR = "#7fcdbb"  # J7

def blk(t0, d, j, op=None):
    """(start, dur, job_id, label, color)"""
    label = f"J{j}.{op if op is not None else j}"
    return (t0, d, j, label, JCOL.get(j, NEW_JOB_COLOR))

# ------------------------- Baseline "toy" FT06 --------------------------
baseline = {
    1: [blk(0,  7, 1, 1), blk( 7, 4, 4, 1), blk(11, 5, 6, 1)],
    2: [blk(0,  8, 2, 1), blk( 8, 5, 5, 2)],
    3: [blk(0,  5, 3, 1), blk( 5, 6, 1, 2), blk(11, 5, 2, 2)],
    4: [blk(0,  6, 4, 2), blk( 6, 5, 6, 2)],
    5: [blk(0,  6, 5, 1), blk( 6, 6, 3, 2)],
    6: [blk(0,  6, 6, 1), blk( 6, 7, 2, 3)],
}

# -------------------------- Drawing helpers -----------------------------
def annotate_bar_times(ax, x, w, y):
    if w >= ANNOT_MIN_WIDTH:
        txt = f"[{int(x)}–{int(x+w)}]"
        ax.text(x + w/2, y, txt, ha='center', va='center', fontsize=FONT_SZ-1, color="black")

def draw_schedule(ax, schedule, *, frozen=None, t_event=None, title=""):
    bar_h = 0.78
    y_max = len(schedule)
    for m in sorted(schedule):
        y = m
        for (t0, dur, jid, lbl, col) in schedule[m]:
            rect = Rectangle((t0, y-bar_h/2), dur, bar_h,
                             facecolor=col, edgecolor='k', lw=0.6)
            if frozen and (m, t0) in frozen:
                rect.set_hatch("///")
                rect.set_facecolor("#DDDDDD")
            ax.add_patch(rect)
            ax.text(t0 + dur*0.5, y, lbl, ha='center', va='center',
                    fontsize=FONT_SZ-1, color='black')
            annotate_bar_times(ax, t0, dur, y - bar_h*0.33)

    if t_event is not None:
        ax.axvline(t_event, color='k', ls='--', lw=1.2)
        # slightly lower label so it doesn't look too high
        ax.text(t_event + 0.15, y_max - 0.35, "event",
                fontsize=9, rotation=90, va='top', ha='left')

    ax.set_xlim(0, T_MAX)
    ax.set_yticks(range(1, y_max+1))
    ax.set_yticklabels([f"M{m}" for m in sorted(schedule)])
    ax.set_xlabel("Time")
    ax.set_ylim(0.5, y_max + 0.55)
    ax.set_title(title)
    ax.grid(axis='x', color='lightgray', linestyle=':', linewidth=0.5)
    ax.set_axisbelow(True)

def save_panel(name, draw_fn):
    fig, ax = plt.subplots(figsize=(7.0, 3.0), constrained_layout=True)
    draw_fn(ax)
    fig.savefig(name, dpi=300)
    plt.close(fig)

# ------------------------------ STEP 1 ----------------------------------
save_panel(
    "step1_baseline.png",
    lambda ax: draw_schedule(
        ax, baseline,
        title="Step 1 — Baseline schedule (no events yet)"
    )
)

# ------------------------------ STEP 2 ----------------------------------
save_panel(
    "step2_event.png",
    lambda ax: draw_schedule(
        ax, baseline, t_event=EVENT_T,
        title="Step 2 — New-Job event is raised at t = 14"
    )
)

# ------------------------------ STEP 3 ----------------------------------
frozen = set()
for m in baseline:
    for (t0, dur, *_rest) in baseline[m]:
        if t0 + dur <= EVENT_T:
            frozen.add((m, t0))
        elif t0 < EVENT_T < t0 + dur:
            frozen.add((m, t0))

step3 = {m: list(blks) for m, blks in baseline.items()}
step3[3].append((EVENT_T, 4, 7, "J7.1", NEW_JOB_COLOR))

save_panel(
    "step3_frozen.png",
    lambda ax: draw_schedule(
        ax, step3, frozen=frozen, t_event=EVENT_T,
        title="Step 3 — Completed & in-process ops frozen; J7 pending"
    )
)

# ------------------------------ STEP 4 ----------------------------------
def draw_step4(ax):
  # Draw without "event" label
  draw_schedule(ax, step3, frozen=frozen, t_event=EVENT_T,
                title="Step 4 — HGA searches reduced problem (2 s time-limit)")

  # GA run rectangle and label at the top
  ax.add_patch(Rectangle((EVENT_T, 3.6), 2, 0.4,
                         facecolor="#c6dbef", edgecolor='k', lw=0.4))
  ax.text(EVENT_T + 1, 3.8, "GA run", ha='center', va='center', fontsize=7)

  # Candidate window text also at the top
  ax.text(EVENT_T + 2.2, 3.8, "candidate window\n needs capacity check",
          fontsize=7, va='center', ha='left')

  ax.set_ylim(0.5, 7.0)  # Adjust to show the top annotations fully


save_panel("step4_reopt.png", draw_step4)

# ------------------------------ STEP 5 ----------------------------------
t_j7_start = 16
dur_j7 = 4
step5_sched = {m: list(blks) for m, blks in baseline.items()}
# FIX: use NEW_JOB_COLOR (previously new_colour) and save_panel
step5_sched[3].append((t_j7_start, dur_j7, 7, "J7.1", NEW_JOB_COLOR))

save_panel(
    "step5_committed.png",
    lambda ax: draw_schedule(
        ax, step5_sched,
        title="Step 5 — Updated schedule committed (J7 inserted)"
    )
)

print("Created step1_baseline.png … step5_committed.png")
