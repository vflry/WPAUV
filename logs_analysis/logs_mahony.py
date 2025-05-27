import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ahrs.filters import Mahony
from scipy.spatial.transform import Rotation as R

# === Load and clean data ===
df = pd.read_csv("logs/MPU_LOGS_PART_3.csv", names=["time", "ax", "ay", "az", "gx", "gy", "gz"])
df = df.apply(pd.to_numeric, errors="coerce").dropna()
df["time"] /= 1000.0  # ms → s
df[["gx", "gy", "gz"]] *= np.pi / 180.0  # °/s → rad/s

# === Apply alignment matrix ===
R_align = np.array([
    [ 0,  0,  1],
    [ 0,  1,  0],
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

# === Convert quaternions to Euler angles (YXZ ZXY) ===

rot = R.from_quat(quats)
euler = rot.as_euler('YXZ', degrees=True)
pitch = np.degrees(np.unwrap(np.radians(euler[:, 0])))
yaw = np.degrees(np.unwrap(np.radians(euler[:, 1])))
roll  = np.degrees(np.unwrap(np.radians(euler[:, 2])))


# pitch = ((pitch) % 360) - 180
# yaw = ((yaw + 180) % 360) - 180
# roll = ((roll) % 360) - 180

# === Plot ===
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["time"], y=roll, mode="lines", name="Roll"))
fig.add_trace(go.Scatter(x=df["time"], y=pitch, mode="lines", name="Pitch"))
fig.add_trace(go.Scatter(x=df["time"], y=yaw, mode="lines", name="Yaw"))

fig.update_layout(
    title="Orientation: Roll, Pitch, Yaw (Robust to Gimbal Lock)",
    xaxis_title="Time (s)",
    yaxis_title="Angle (°)",
    legend_title="Legend",
    template="plotly_white",
)

fig.show()