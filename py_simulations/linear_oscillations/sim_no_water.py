## Vianney Fleury - ENSTA / University of Adelaide - 2025

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

## Simulation constants

g = 9.81  # gravity (m/s^2)

## Simulation variables

## Oscillating mass characteristics

m = 0.25 # Mass of the oscillating mass (kg)
mu_mag = 1.8
mu_friction = 5
mu = mu_mag + mu_friction  # Damping coefficient of the oscillating mass (kg/s)
k = 237  # Spring constant of the oscillating mass (N/m)




## Linear generator characteristics
Req = 2 # Equivalent resistance of the charging circuit (Ohms)
N = 100  # Number of turns in the coil
B = 0.2



## Oscillation parameters

amplitude = 0.1
frequency = 4 # Frequency of the oscillation (Hz)

## Simulation parameters

tmax = 8  # Total simulation time (s)
dt = 1e-3
t_values = np.arange(0, tmax, dt)  # Time vector

# Initial conditions
y0 = 0.0
vy0 = 0.0
x_vec = np.array([y0, vy0])
X = [x_vec]

def z(t):
    return amplitude * np.sin(2 * np.pi * frequency * t)

def vz(t):
    return 2 * np.pi * frequency * amplitude * np.cos(2 * np.pi * frequency * t)


def f(t, x_vec):
    """Derivates the state vector."""
    y, vy = x_vec
    dydt = vy
    d2ydt = -(k*(y-z(t)) + mu * (vy-vz(t))) / m

    return np.array([dydt, d2ydt])


# RK4 integration
for t in t_values[:-1]:
    rk1 = f(t, x_vec)
    rk2 = f(t + dt/2, x_vec + dt/2 * rk1)
    rk3 = f(t + dt/2, x_vec + dt/2 * rk2)
    rk4 = f(t + dt  , x_vec + dt   * rk3)

    x_vec = x_vec + (dt / 6) * (rk1 + 2*rk2 + 2*rk3 + rk4)
    X.append(x_vec)



X = np.array(X)
t_values = np.array(t_values)
y_values = X[:, 0]
vy_values = X[:, 1]
z_values = z(t_values)
vz_values = vz(t_values)
power = mu_mag * (vz_values - vy_values) ** 2



# Plot results using Plotly with a single y-axis
fig = go.Figure()
fig.add_trace(go.Scatter(x=t_values, y=vz_values, mode='lines', name='Velocity (vz) in m/s'))
fig.add_trace(go.Scatter(x=t_values, y=(y_values-z_values)*100, mode='lines', name='Displacement (y-z) in cm'))
fig.add_trace(go.Scatter(x=t_values, y=vy_values-vz_values, mode='lines', name='Velocity (vy-vz) in m/s'))
fig.add_trace(go.Scatter(x=t_values, y=power, mode='lines', name='Power in W'))
fig.update_layout(
    title='Oscillating Mass Simulation',
    xaxis_title='Time (s)',
    yaxis=dict(title='Values'),
    legend_title='Variables'
)
fig.show()