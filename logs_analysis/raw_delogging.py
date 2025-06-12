import numpy as np
import pandas as pd
import plotly.graph_objects as go

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

# === Compute inclination without filtering ===

roll = np.degrees(np.arctan2(acc[:, 1], acc[:, 2]))
pitch = np.degrees(np.arctan2(-acc[:, 0], np.sqrt(acc[:, 1]**2 + acc[:, 2]**2)))

def incl_angle(pitch, roll):
    return np.degrees(np.arctan2(np.sqrt(np.tan(np.radians(pitch))**2 + np.tan(np.radians(roll))**2), 1))

inclination = incl_angle(pitch, roll)

# === Plot ===

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["time"], y=roll, mode="lines", name="Roll"))
fig.add_trace(go.Scatter(x=df["time"], y=pitch, mode="lines", name="Pitch"))
fig.add_trace(go.Scatter(x=df["time"], y=inclination, mode="lines", name="Inclination"))
fig.update_layout(
    title="Inclination Angle (Without Filtering)",
    xaxis_title="Time (s)",
    yaxis_title="Angle (°)",
    legend_title="Legend",
    template="plotly_white",
)
fig.show()
