"""
plots an illustrative figure used to explain the main idea of the paper
"""

import os
import matplotlib.pyplot as plt
from Dunnsigouin_etal_2025 import config

# input ----------------------------------------------------------------
path_in     = config.dirs['fig'] 
fig_path_01 = path_in + "presentation_fig_01.pdf"  # blue only
fig_path_02 = path_in + "presentation_fig_02.pdf"  # blue + green
fig_path_03 = path_in + "presentation_fig_03.pdf"  # blue + red
write2file  = True
# ----------------------------------------------------------------------


def setup_axes():
    """Create XKCD-styled axes with common limits, labels, and ticks."""
    plt.xkcd()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(1, 10)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Lead time (days)")
    ax.set_ylabel("Forecast accuracy")
    ax.set_xticks(range(1, 11))
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    return fig, ax


def draw_blue(ax):
    """Blue (grid-scale) arrow."""
    ax.annotate(
        "",
        xy=(7, 0), xytext=(1, 0.8),
        arrowprops=dict(arrowstyle="->, head_length=0.75, head_width=0.75", lw=4, color="tab:blue"),
    )


def draw_red(ax):
    """Red (spatially-aggregated) arrow."""
    ax.annotate(
        "",
        xy=(10, 0), xytext=(1, 0.9),
        arrowprops=dict(arrowstyle="->, head_length=0.75, head_width=0.75", lw=4, color="tab:red"),
    )


def draw_green(ax):
    """Green (temporally-aggregated) arrows (two segments)."""
    ax.annotate(
        "",
        xy=(7, 0.4), xytext=(1, 0.4),
        arrowprops=dict(arrowstyle="->, head_length=0.75, head_width=0.75", lw=4, color="tab:green"),
    )
    ax.annotate(
        "",
        xy=(10, 0.2), xytext=(7, 0.2),
        arrowprops=dict(arrowstyle="->, head_length=0.75, head_width=0.75", lw=4, color="tab:green"),
    )


def annotate_blue(ax):
    """Blue label."""
    ax.text(5.0, 0.15, "raw forecast", color="tab:blue", fontsize=20, ha="right")


def annotate_red(ax):
    """Red label."""
    ax.text(5, 0.58, "spatially-aggregated", color="tab:red", fontsize=20, ha="left")


def annotate_green(ax):
    """Green label."""
    ax.text(5, 0.5, "temporally-aggregated", color="tab:green", fontsize=20, ha="left")


def finalize_figure(fig, outpath, write):
    """Tighten layout and either save or show."""
    fig.tight_layout()
    if write:
        outdir = os.path.dirname(os.path.abspath(outpath))
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        fig.savefig(outpath)
        plt.close(fig)
    else:
        plt.show()


def make_figure_blue_only(outpath, write):
    """Figure 1: blue arrow + blue text."""
    fig, ax = setup_axes()
    draw_blue(ax)
    annotate_blue(ax)
    finalize_figure(fig, outpath, write)


def make_figure_blue_green(outpath, write):
    """Figure 2: blue + green arrows and labels."""
    fig, ax = setup_axes()
    draw_blue(ax)
    draw_green(ax)
    annotate_blue(ax)
    annotate_green(ax)
    finalize_figure(fig, outpath, write)


def make_figure_blue_red(outpath, write):
    """Figure 3: blue + red arrows and labels."""
    fig, ax = setup_axes()
    draw_blue(ax)
    draw_red(ax)
    annotate_blue(ax)
    annotate_red(ax)
    finalize_figure(fig, outpath, write)


    
if __name__ == "__main__":

    make_figure_blue_only(fig_path_01, write2file)
    make_figure_blue_green(fig_path_02, write2file)
    make_figure_blue_red(fig_path_03, write2file)

