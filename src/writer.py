import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import calendar
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

from map import get_letter_map

# Define commit color shades (lighter means fewer commits)
COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

LETTER_MAP = get_letter_map()  # Load or define the letter map
# Define a simple 5x5 pixel font for letters A-Z
# LETTER_MAP = {
#     " ": ["     ", "     ", "     ", "     ", "     "],
#     "A": ["  #  ", " # # ", "#####", "#   #", "#   #"],
#     "B": ["#### ", "#   #", "#### ", "#   #", "#### "],
#     "C": [" ####", "#    ", "#    ", "#    ", " ####"],
#     "D": ["###  ", "#  # ", "#   #", "#  # ", "###  "],
#     "E": ["#####", "#    ", "#####", "#    ", "#####"],
#     "F": ["#####", "#    ", "#####", "#    ", "#    "],
# }


def generate_commit_data():
    """Generate random commit activity levels for a 7x52 grid"""
    return np.random.randint(0, 1, (8, 52))


def apply_letter_overlay(grid, text):
    """Overlay letters onto the commit grid by reducing intensity"""
    start_x, start_y = 2, 2  # Positioning letters within grid

    for letter in text.upper():
        if letter in LETTER_MAP:
            letter_grid = LETTER_MAP[letter]
            for row in range(len(letter_grid)):
                for col in range(len(letter_grid[row])):
                    if letter_grid[row][col] == "#":
                        x, y = start_x + col, start_y + row
                        if 0 <= x < 52 and 0 <= y < 7:
                            grid[y, x] = max(0, grid[y, x] + 2)  # Make it lighter
            start_x += 6  # Move to next letter position

    return grid


def plot_commit_graph(grid):
    print("Plotting commit graph")
    logger.debug(f"Generated year_dict with {grid.shape} dates")
    assert len(grid.shape) == 2 and grid.shape[0] == 7 and grid.shape[1] == 52

    """Plot the commit graph with text overlay"""
    fig, ax = plt.subplots(figsize=(13, 3))

    # Plot each grid cell
    for y in range(grid.shape[0]+1): # 0-7 plus one for zero row
        for x in range(grid.shape[1]):
            # Safely map grid value to a color index to avoid IndexError
            try:
                val = int(grid[y-1, x])
            except Exception:
                val = 0
            idx = min(max(val, 0), len(COLORS) - 1)
            ax.add_patch(
                Rectangle((x, -y), 1, 1, ec="white", lw=2, color=COLORS[idx])
            )  # type: ignore

    # Plot legend: place one square per defined color
    legend_start_x = 47
    for i, color in enumerate(COLORS):
        x_pos = legend_start_x + i
        ax.add_patch(Rectangle((x_pos, -8), 1, 1, ec="white", lw=2, color=color))  # type: ignore
    ax.text(legend_start_x - 1, -8, "Less", ha="center", va="bottom", fontsize=10, color="black")
    ax.text(legend_start_x + len(COLORS) + 1, -8, "More", ha="center", va="bottom", fontsize=10, color="black")

    # Add Y-axis labels (Mon, Wed, Fri)
    day_labels = {1.5: "Mon", 3.5: "Wed", 5.5: "Fri"}
    for y in day_labels:
        ax.text(
            -1, -y, day_labels[y], va="center", ha="right", fontsize=10, color="black"
        )

    # Add X-axis labels (Months)
    current_month = datetime.now().month  # Get the current month

    month_labels = []
    month_starts = []

    # Estimate month divisions based on 52 weeks
    weeks_per_month = 4.33  # Approximate average
    weeks_passed = 0

    for i in range(12):
        month = (
            current_month + i - 1
        ) % 12 + 1  # Cycle through months starting from the current one
        month_labels.append(calendar.month_abbr[month])
        month_starts.append(int(weeks_passed))
        weeks_passed += weeks_per_month

    for i, month in enumerate(month_labels):
        if month_starts[i] < 53:  # Prevent overflow beyond 52 weeks
            ax.text(
                month_starts[i] + 1.5,
                0.5,
                month,
                ha="center",
                va="bottom",
                fontsize=10,
                color="black",
            )

    ax.set_xlim(0, 55)
    ax.set_ylim(-9, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    ax.set_aspect("equal")

    #plt.show()
    return fig

