import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ahrs.filters import Mahony
from scipy.spatial.transform import Rotation as R

# === Load and clean data ===
df = pd.read_csv("logs/MPU_LOGS_PART_2.csv", names=["time", "ax", "ay", "az", "gx", "gy", "gz"])
df = df.apply(pd.to_numeric, errors="coerce").dropna()
df["time"] /= 1000.0  # ms → s
df[["gx", "gy", "gz"]] *= np.pi / 180.0  # °/s → rad/s

# === Apply alignment matrix ===
R_align = np.array([
    [ 0,  0,  1],
    [ 0, -1,  0],
    [ 1,  0,  0]
])

# === Rotate sensor data ===
acc_raw = df[["ax", "ay", "az"]].to_numpy()
gyr_raw = df[["gx", "gy", "gz"]].to_numpy()
acc = (R_align @ acc_raw.T).T
gyr = (R_align @ gyr_raw.T).T

# === Mahony filter ===
mahony = Mahony(sampleperiod=np.mean(np.diff(df["time"])), kp=20.0)
quats = np.zeros((len(df), 4))
q = np.array([1.0, 0.0, 0.0, 0.0])

for i in range(len(df)):
    q = mahony.updateIMU(q, gyr[i], acc[i])
    quats[i] = q

# === Inclination computation ===
# Inclination = angle between local Z axis and world Z axis
rot = R.from_quat(quats)
z_vectors = rot.apply(np.array([0, 0, 1]))
vertical = np.array([0, 0, 1])
dot_products = np.clip(np.dot(z_vectors, vertical), -1.0, 1.0)
inclination = np.abs(90.0 - np.degrees(np.arccos(dot_products)))


# === Plot ===
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["time"], y=inclination, mode="lines", name="Inclination"))

fig.update_layout(
    title="Inclination Angle (Quaternion-Based)",
    xaxis_title="Time (s)",
    yaxis_title="Inclination (°)",
    legend_title="Legend",
    template="plotly_white",
)

fig.show()
