import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from ahrs.filters import Mahony
from ahrs.common.orientation import q2euler
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R

# === Load and clean data ===
df = pd.read_csv("logs/MPU_LOGS_PART_3.csv", names=["time", "ax", "ay", "az", "gx", "gy", "gz"])
df = df.apply(pd.to_numeric, errors="coerce").dropna()
df["time"] /= 1000.0  # ms → s
df[["gx", "gy", "gz"]] *= np.pi / 180.0  # °/s → rad/s

# === Sensor data ===
acc = df[["ax", "ay", "az"]].to_numpy()
gyr = df[["gx", "gy", "gz"]].to_numpy()

# === Mahony Filter ===
dt = np.mean(np.diff(df["time"]))
mahony = Mahony(sampleperiod=dt, kp=20.0)
quats = np.zeros((len(df), 4))
q = np.array([1.0, 0.0, 0.0, 0.0])

for i in range(len(df)):
    q = mahony.updateIMU(q, gyr[i], acc[i])
    quats[i] = q

# === Convert quaternions to Euler angles ===
euler = np.array([np.degrees(q2euler(q)) for q in quats])
df[["roll", "pitch", "yaw"]] = euler

# === Convert to [x, y, z, w] for scipy Rotation ===
scipy_quats = quats[:, [1, 2, 3, 0]]

# === Setup reference axes ===
origin = np.zeros(3)
axes = np.eye(3)

# === Create 3D figure ===
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.view_init(elev=30, azim=135)

# === Animation variables ===
frame_idx = 0
playing = True

# === Animation function ===
def update(frame):
    ax.cla()
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.view_init(elev=30, azim=135)
    ax.set_title(f"Time : {df['time'].iloc[frame]:.2f} s")

    rot = R.from_quat(scipy_quats[frame])
    rotated_axes = rot.apply(axes)

    colors = ['r', 'g', 'b']
    for vec, color in zip(rotated_axes, colors):
        ax.quiver(*origin, *vec, color=color)

# === Slider update function ===
def slider_update(val):
    global frame_idx
    frame_idx = int(slider.val)
    update(frame_idx)
    fig.canvas.draw_idle()

# === Play/Pause button function ===
def toggle_play(event):
    global playing
    playing = not playing
    if playing:
        play_button.label.set_text("Pause")
    else:
        play_button.label.set_text("Play")

# === Add slider ===
ax_slider = plt.axes([0.2, 0.02, 0.6, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Frame', 0, len(df) - 1, valinit=0, valstep=1)
slider.on_changed(slider_update)

# === Add play/pause button ===
ax_button = plt.axes([0.85, 0.02, 0.1, 0.04])
play_button = Button(ax_button, 'Pause', color='lightblue', hovercolor='lightgreen')
play_button.on_clicked(toggle_play)

# === Animation loop ===
def animation_loop(i):
    global frame_idx
    if playing:
        frame_idx = (frame_idx + 1) % len(df)
        slider.set_val(frame_idx)

ani = FuncAnimation(fig, animation_loop, interval=1)
plt.tight_layout()
plt.show()