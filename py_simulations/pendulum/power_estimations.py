import numpy as np
import plotly.graph_objects as go

# --- Wave parameters ---
A = 0.05 # vertical amplitude (m)
Phi = np.radians(30)  # roll amplitude (rad)
f = 1  # frequence (Hz)
omega = 2 * np.pi * f
T = 20  # simulation time (s)

# --- time array ---
dt = 0.001
t = np.arange(0, T, dt)
n_steps = len(t)

# --- tool functions ---
def z_f(t): return A * np.sin(omega * t)
def dz2_f(t): return -A * omega ** 2 * np.sin(omega * t)
def phi_f(t): return Phi * np.sin(omega * t + np.pi / 2)
def dphi2_f(t): return -Phi * omega ** 2 * np.sin(omega * t + np.pi / 2)

# --- pendulum parameters ---
l = 0.3  # length (m)
g = 9.81  # g (m/s^2)
m = 0.25  # mass (kg)


k_rs = np.linspace(0.02, 0.03, 50) # dampening coefs (N·s·m)

results = {}

for k_r in k_rs:

    # --- RK2 ---
    theta = np.zeros(n_steps)
    theta_dot = np.zeros(n_steps)
    theta[0] = 0
    theta_dot[0] = 0

    for i in range(n_steps - 1):
        ti = t[i]

        th = theta[i]
        th_dot = theta_dot[i]


        def accel(t, th, th_dot):
            return -(g/l) * np.sin(th + phi_f(t)) + (dz2_f(t)/l) * np.sin(th) - dphi2_f(t) - (k_r/(m*l**2))*th_dot


        k1_th = th_dot
        k1_th_dot = accel(ti, th, th_dot)

        th_temp = th + dt * k1_th
        th_dot_temp = th_dot + dt * k1_th_dot

        k2_th = th_dot_temp
        k2_th_dot = accel(ti + dt, th_temp, th_dot_temp)

        theta[i + 1] = th + 0.5 * dt * (k1_th + k2_th)
        theta_dot[i + 1] = th_dot + 0.5 * dt * (k1_th_dot + k2_th_dot)

    results[k_r] = [theta, theta_dot]

# --- instant power calculation ---

mean_powers = []

for k_r in k_rs:
    theta, theta_dot = results[k_r]

    power = np.zeros(n_steps)

    angular_speeds = np.zeros(n_steps)

    for i in range(n_steps):
        th = theta[i]
        th_dot = theta_dot[i]
        ti = t[i]

        torque = k_r * th_dot
        power[i] = abs(torque * th_dot)

        angular_speeds[i] = abs(np.degrees(th_dot))

    # --- Angular speed stats ---
    print(f"\n\n=== Angular Speed Stats for k_r = {k_r} ===\n")
    max_angular_speed = np.max(angular_speeds)
    median_angular_speed = np.median(angular_speeds)
    average_angular_speed = np.mean(angular_speeds)
    print(f"Max angular speed: {max_angular_speed:.2f} °/s")
    print(f"Median angular speed: {median_angular_speed:.2f} °/s")
    print(f"Average angular speed: {average_angular_speed:.2f} °/s")

    # --- Power stats ---
    print(f"\n=== Power Stats for k_r = {k_r} ===\n")
    max_power = np.max(power)
    median_power = np.median(power)
    average_power = np.mean(power)
    print(f"Max power: {max_power:.2f} W")
    print(f"Median power: {median_power:.2f} W")
    print(f"Average power: {average_power:.2f} W")
    mean_powers.append(average_power)


# --- Plot mean power values ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=k_rs, y=mean_powers, mode='markers+lines', marker_color='blue'))

fig.update_layout(
    title="Mean Power vs Damping Coefficient",
    xaxis_title="Damping Coefficient (k_r)",
    yaxis_title="Mean Power (W)",
    xaxis=dict(type='linear'),
    template="plotly_white"
)

fig.show()