import numpy as np
import plotly.graph_objects as go

# --- Wave parameters ---
A = 0.05 # vertical amplitude (m)
Phi = np.radians(30)  # roll amplitude (rad)
f = 1  # frequence (Hz)
omega = 2 * np.pi * f
T = 20  # simulation time (s)

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
l = 0.15  # length (m)
g = 9.81  # g (m/s^2)
m = 0.2  # mass (kg)
k_r = 0.0167 # dampening coef (N·s·m)

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


# --- instant power calculation ---
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
print("=== Angular Speed Stats ===")
max_angular_speed = np.max(angular_speeds)
median_angular_speed = np.median(angular_speeds)
average_angular_speed = np.mean(angular_speeds)
print(f"Max angular speed: {max_angular_speed:.2f} °/s")
print(f"Median angular speed: {median_angular_speed:.2f} °/s")
print(f"Average angular speed: {average_angular_speed:.2f} °/s")

# --- Power stats ---
print("\n=== Power Stats ===")
max_power = np.max(power)
median_power = np.median(power)
average_power = np.mean(power)
print(f"Max power: {max_power:.2f} W")
print(f"Median power: {median_power:.2f} W")
print(f"Average power: {average_power:.2f} W")

# --- Plotly animation ---
frames = []
for i in range(n_steps):
    z = z_f(t[i])
    phi = phi_f(t[i])
    th = theta[i]
    th_dot = theta_dot[i]
    pwr = power[i]

    # anchor point position
    origin_x = 0
    origin_y = z

    # floater position
    floater_x = [-0.1 * np.cos(phi), 0.1 * np.cos(phi)]
    floater_y = [z - 0.1 * np.sin(phi), z + 0.1 * np.sin(phi)]

    # pendulum position
    pendulum_x = [origin_x, origin_x + l * np.sin(th + phi)]
    pendulum_y = [origin_y, origin_y - l * np.cos(th + phi)]

    annotation = go.layout.Annotation(
        x = 0.12, y = 0.5,
        text = f"Power = {pwr:.3f} W<br>Angular Speed = {abs(np.degrees(th_dot)):.2f} °/s",
        showarrow=False,
        font=dict(size=14, color='black'),
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
    )

    frames.append(go.Frame(
        data=[
            go.Scatter(x=floater_x, y=floater_y, mode='lines', line=dict(color='red', width=6), name='Flotteur'),
            go.Scatter(x=pendulum_x, y=pendulum_y, mode='lines+markers', line=dict(color='blue', width=3),
                       marker=dict(size=6, color='black'), name='Pendule')
        ],
        layout=go.Layout(annotations=[annotation]),
        name=str(i)
    ))

fig = go.Figure(
    data=frames[0].data,
    layout=go.Layout(
        title="Simulation du pendule dans un flotteur en mouvement",
        xaxis=dict(range=[-0.2, 0.2], title="x (m)"),
        yaxis=dict(range=[-0.3, 0.6], title="y (m)", scaleanchor="x", scaleratio=1),
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)]),
                     dict(label="Pause",
                          method="animate",
                          args=[[None], dict(mode="immediate", frame=dict(duration=0, redraw=False),
                                             transition=dict(duration=0))])])]
    ),
    frames=frames
)

fig.show()