import pandas as pd
import numpy as np
from itertools import permutations, product
from ahrs.filters import Mahony
from scipy.spatial.transform import Rotation as R

# Charger les données
df = pd.read_csv("MPU_LOGS.CSV", names=["time", "ax", "ay", "az", "gx", "gy", "gz"])
df = df.apply(pd.to_numeric, errors="coerce").dropna()
df["time"] /= 1000.0  # ms → s
df[["gx", "gy", "gz"]] *= np.pi / 180.0  # °/s → rad/s

acc_raw = df[["ax", "ay", "az"]].to_numpy()
gyr_raw = df[["gx", "gy", "gz"]].to_numpy()

# Générer les 48 combinaisons possibles de matrices d'alignement
axis_permutations = list(permutations(range(3)))
sign_combinations = list(product([-1, 1], repeat=3))
all_alignments = []

for perm in axis_permutations:
    for signs in sign_combinations:
        mat = np.zeros((3, 3))
        for i, idx in enumerate(perm):
            mat[i, idx] = signs[i]
        all_alignments.append(mat)

# Tester chaque matrice
results = []
for i, R_align in enumerate(all_alignments):
    acc = (R_align @ acc_raw.T).T
    gyr = (R_align @ gyr_raw.T).T

    mahony = Mahony(sampleperiod=np.mean(np.diff(df["time"])), kp=20.0)
    quats = np.zeros((len(df), 4))
    q = np.array([1.0, 0.0, 0.0, 0.0])

    for j in range(len(df)):
        q = mahony.updateIMU(q, gyr[j], acc[j])
        quats[j] = q

    rot = R.from_quat(quats)
    euler = rot.as_euler('ZYX', degrees=True)
    yaw = np.degrees(np.unwrap(np.radians(euler[:, 0])))
    pitch = np.degrees(np.unwrap(np.radians(euler[:, 1])))
    roll = np.degrees(np.unwrap(np.radians(euler[:, 2])))

    results.append({
        "index": i,
        "R_align": R_align,
        "std_roll": np.std(roll),
        "std_pitch": np.std(pitch),
        "std_yaw": np.std(yaw),
        "mean_roll": np.mean(roll),
        "mean_pitch": np.mean(pitch),
        "mean_yaw": np.mean(yaw)
    })

# Afficher les 5 meilleurs (plus sensibles au mouvement)
results.sort(key=lambda x: -(x["std_roll"] + x["std_pitch"] + x["std_yaw"]))
for r in results[:5]:
    print(f"Index: {r['index']}")
    print("R_align:")
    print(r["R_align"])
    print(f"STD → Roll: {r['std_roll']:.2f}, Pitch: {r['std_pitch']:.2f}, Yaw: {r['std_yaw']:.2f}")
    print(f"MEAN → Roll: {r['mean_roll']:.2f}, Pitch: {r['mean_pitch']:.2f}, Yaw: {r['mean_yaw']:.2f}")
    print("-" * 40)
