import numpy as np
import plotly.graph_objects as go

# --- Wave parameters ---
A = 0.05  # vertical amplitude (m)
Phi = np.radians(30)  # roll amplitude (rad)
f = 1  # frequency (Hz)
omega = 2 * np.pi * f
T = 20  # simulation duration (s)

# --- time array ---
dt = 0.01
t = np.arange(0, T, dt)
n_steps = len(t)


# --- tool functions ---
def z_f(t): return A * np.sin(omega * t)


def dz2_f(t): return -A * omega ** 2 * np.sin(omega * t)


def phi_f(t): return Phi * np.sin(omega * t + np.pi / 2)


def dphi2_f(t): return -Phi * omega ** 2 * np.sin(omega * t + np.pi / 2)


# --- pendulum parameters ---
l = 0.1  # Length (m)
g = 9.81  # Gravity (m/s²)
m = 0.15  # Mass (kg)
k_r = 5e-3  # Damping coefficient (N·s·m)

# --- RK2 init ---
theta = np.zeros(n_steps)
theta_dot = np.zeros(n_steps)
theta[0] = np.radians(0)
theta_dot[0] = 0

# --- RK2 Integration ---
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


# --- instant power calculation ---
I = m * l**2
power = np.zeros(n_steps)

for i in range(n_steps):
    th = theta[i]
    th_dot = theta_dot[i]
    ti = t[i]

    torque = I * (-(g/l)*np.sin(th + phi_f(ti)) + (dz2_f(ti)/l)*np.sin(th) - dphi2_f(ti))
    power[i] = abs(torque * th_dot)

# --- plotting ---
fig = go.Figure()

fig.add_trace(go.Scatter(x=t, y=np.degrees(theta), mode='lines', name='θ (pendulum)', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=t, y=np.degrees(phi_f(t)), mode='lines', name='ϕ (floater)', line=dict(color='red', dash='dot')))
fig.add_trace(go.Scatter(x=t, y=1000*power, mode='lines', name='Theorical power (mW)', line=dict(color='green')))
fig.update_layout(
    title="Pendulum oscillations in the floater",
    xaxis_title="Temps (s)",
    yaxis_title="Angle (°) / Vitesse angulaire (°/s)",
    legend=dict(x=0.02, y=0.98),
    template="plotly_white"
)

fig.show()
