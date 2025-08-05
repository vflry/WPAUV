import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2euler
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation as R

# === Chargement et nettoyage ===
df = pd.read_csv("MPU_LOGS.CSV", names=["time", "ax", "ay", "az", "gx", "gy", "gz"])
df = df.apply(pd.to_numeric, errors="coerce").dropna()  # conversion + suppression NaN
df["time"] /= 1000.0  # ms -> s
df[["gx", "gy", "gz"]] *= np.pi / 180.0  # °/s -> rad/s

# === Extraction des données ===
acc, gyr = df[["ax", "ay", "az"]].to_numpy(), df[["gx", "gy", "gz"]].to_numpy()

# === Filtrage Madgwick ===
dt = np.mean(np.diff(df["time"]))
madgwick = Madgwick(sampleperiod=dt, beta = 0.3)
quats = np.zeros((len(df), 4))
q = np.array([1.0, 0.0, 0.0, 0.0])

for i in range(len(df)):
    q = madgwick.updateIMU(q, gyr[i], acc[i])
    quats[i] = q

# === Angles d'Euler ===
euler = np.array([np.degrees(q2euler(q)) for q in quats])  # roll, pitch, yaw
df[["roll", "pitch", "yaw"]] = euler

# === Préparation des quaternions pour scipy ===
# Reorder quats from [w, x, y, z] → [x, y, z, w]
scipy_quats = quats[:, [1, 2, 3, 0]]

# === Repère de base : X, Y, Z unitaires ===
origin = np.zeros(3)
axes = np.eye(3)  # identifie les vecteurs X, Y, Z

# === Création de la figure 3D ===
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.view_init(elev=30, azim=135)  # orientation de vue

# === Fonction d’animation ===
def update(frame):
    ax.cla()  # Clear axes
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.view_init(elev=30, azim=135)
    ax.set_title(f"Time : {df['time'].iloc[frame]:.2f} s")

    # Appliquer la rotation
    rot = R.from_quat(scipy_quats[frame])
    rotated_axes = rot.apply(axes)

    # Tracer les vecteurs X (rouge), Y (vert), Z (bleu)
    colors = ['r', 'g', 'b']
    for vec, color in zip(rotated_axes, colors):
        ax.quiver(*origin, *vec, color=color)

# === Animation ===
ani = FuncAnimation(fig, update, frames=range(0, len(df), 5), interval=30)
plt.tight_layout()
plt.show()
