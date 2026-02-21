from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


def load_data_from_txt(file_path: str, num_cols: int = 6) -> np.ndarray:
    """Load bracketed, comma-separated rows from a text file into an ndarray."""
    rows = []
    path = Path(file_path)
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Remove surrounding brackets/commas, then split on commas
        stripped = stripped.strip(",").strip("[]")
        parts = [p.strip() for p in stripped.split(",") if p.strip()]
        if len(parts) != num_cols:
            raise ValueError(
                f"Expected {num_cols} columns but got {len(parts)} in line: {line}"
            )
        rows.append([float(p) for p in parts])
    return np.asarray(rows)


DATA_FILE = Path(__file__).parent / "data" / "0028_11_22_25.txt"
data = load_data_from_txt(DATA_FILE)

# Time index (you can scale it if you have real dt)
T = data.shape[0]
t = np.arange(T)

# Component names
labels = ["Fx", "Fy", "Fz", "Tx", "Ty", "Tz"]

# Consistent colors per axis (x, y, z)
axis_colors = {
    "x": "#e74c3c",  # red
    "y": "#27ae60",  # green
    "z": "#2980b9",  # blue
}
component_colors = [
    axis_colors["x"],  # Fx
    axis_colors["y"],  # Fy
    axis_colors["z"],  # Fz
    axis_colors["x"],  # Tx
    axis_colors["y"],  # Ty
    axis_colors["z"],  # Tz
]

# Create two figures: force (3×1) and torque (3×1)
fig_force, axes_force = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
fig_torque, axes_torque = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
axes = np.concatenate([axes_force, axes_torque])

lines = []

# Precompute y-limits per component (with small margins)
for i, ax in enumerate(axes):
    y = data[:, i]
    y_min = y.min()
    y_max = y.max()
    pad = 0.1 * (y_max - y_min if y_max != y_min else 1.0)
    ax.set_xlim(0, T - 1)
    ax.set_ylim(y_min - pad, y_max + pad)
    ax.set_title(labels[i])
    ax.set_xlabel("Time step")
    if i < 3:
        ax.set_ylabel("N")
    else:
        ax.set_ylabel("Nm")
    # Initialize an empty line for each subplot
    line, = ax.plot([], [], marker="o", markersize=3, color=component_colors[i])
    lines.append(line)

fig_force.suptitle("Force Components Over Time", fontsize=14)
fig_torque.suptitle("Torque Components Over Time", fontsize=14)

def init():
    """Initialize all lines to empty."""
    for line in lines:
        line.set_data([], [])
    return lines

def update(frame):
    """Update all lines up to the current frame."""
    # up to and including index = frame
    for i, line in enumerate(lines):
        line.set_data(t[:frame + 1], data[:frame + 1, i])
    return lines

# Create animations for each figure
ani_force = FuncAnimation(
    fig_force,
    update,
    frames=T,
    init_func=init,
    blit=True,
    interval=300,
    repeat=True,
)

ani_torque = FuncAnimation(
    fig_torque,
    update,
    frames=T,
    init_func=init,
    blit=True,
    interval=300,
    repeat=True,
)

fig_force.tight_layout()
fig_torque.tight_layout()
plt.show()
