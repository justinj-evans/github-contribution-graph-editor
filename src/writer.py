import numpy as np
import matplotlib.pyplot as plt
import calendar
from datetime import datetime, timedelta

from src.map import get_letter_map

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
    """Plot the commit graph with text overlay"""
    fig, ax = plt.subplots(figsize=(13, 3))

    # Plot each grid cell
    for y in range(8):
        for x in range(52):
            ax.add_patch(
                plt.Rectangle((x, -y), 1, 1, ec="white", lw=2, color=COLORS[grid[y, x]])
            )  # type: ignore

    # Plot legend
    for i, x in enumerate(range(47, 52)):
        ax.add_patch(plt.Rectangle((x, -9), 1, 1, ec="white", lw=2, color=COLORS[i]))  # type: ignore
    ax.text(45.5, -9, "Less", ha="center", va="bottom", fontsize=10, color="black")
    ax.text(53.5, -9, "More", ha="center", va="bottom", fontsize=10, color="black")

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
        if month_starts[i] < 52:  # Prevent overflow beyond 52 weeks
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

    plt.show()


def convert_grid_to_dates(data) -> list:
    """
    Convert a 7x52 grid of commit data into a list of dates and values.
    The grid is assumed to represent weeks, with each column being a week
    and each row being a day (Sunday to Saturday).

    Returns:
        dates: a list of tuples [(date_str, value)], where date_str is in ISO format
    """

    # Step 1: Define the start date (must be a Sunday)
    one_year_ago = datetime.now() - timedelta(days=365)
    start_date = one_year_ago - timedelta(days=one_year_ago.weekday() + 1 % 7)

    # Step 2: Map dates
    dates = []
    commit_dates = []
    for col in range(data.shape[0]):  # iterate over weeks
        for row in range(data.shape[0]):  # iterate over days (Sunday to Saturday)
            day_offset = col * 7 + row
            date = start_date + timedelta(days=day_offset)
            commit_date_str = date.strftime("%Y-%m-%dT%H:%M:%S")  # FIXED format
            value = data[row, col].astype(int)
            dates.append((commit_date_str, value))
            if value > 0:
                commit_dates.append((commit_date_str, value))

    return commit_dates
