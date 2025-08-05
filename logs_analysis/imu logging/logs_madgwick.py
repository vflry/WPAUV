import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ahrs.filters import Madgwick
from ahrs.common.orientation import q2euler

# === Data Loading and Cleaning ===
df = pd.read_csv("logs/MPU_LOGS_PART_1.csv", names=["time", "ax", "ay", "az", "gx", "gy", "gz"])
df = df.apply(pd.to_numeric, errors="coerce").dropna()
df["time"] /= 1000.0  # ms -> s
df[["gx", "gy", "gz"]] *= np.pi / 180.0  # °/s -> rad/s

# === Data Extraction ===
acc, gyr = df[["ax", "ay", "az"]].to_numpy(), df[["gx", "gy", "gz"]].to_numpy()

# === Function to Apply Madgwick Filter ===
def apply_madgwick(beta):
    madgwick = Madgwick(sampleperiod=np.mean(np.diff(df["time"])), beta=beta)
    quats = np.zeros((len(df), 4))
    q = np.array([1.0, 0.0, 0.0, 0.0])
    for i in range(len(df)):
        q = madgwick.updateIMU(q, gyr[i], acc[i])
        quats[i] = q
    euler = np.array([np.degrees(q2euler(q)) for q in quats])  # roll, pitch, yaw
    return euler

# === Plotly Visualization ===
fig = go.Figure()
beta_values = [2.5]  # Different beta parameters

for beta in beta_values:
    euler = apply_madgwick(beta)
    roll, pitch, yaw = euler[:, 0], euler[:, 1], euler[:, 2]
    fig.add_trace(go.Scatter(x=df["time"], y=roll, mode="lines", name=f"Roll (β={beta})"))
    fig.add_trace(go.Scatter(x=df["time"], y=pitch, mode="lines", name=f"Pitch (β={beta})"))
    fig.add_trace(go.Scatter(x=df["time"], y=yaw, mode="lines", name=f"Yaw (β={beta})"))

# Layout
fig.update_layout(
    title="Filtered Data for Different Madgwick Beta Parameters",
    xaxis_title="Time (s)",
    yaxis_title="Values (°)",
    legend_title="Legend",
    template="plotly_white",
)

fig.show()