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
mu_friction = 0
mu = mu_mag + mu_friction  # Damping coefficient of the oscillating mass (kg/s)
k = 237  # Spring constant of the oscillating mass (N/m)




## Linear generator characteristics
Req = 2 # Equivalent resistance of the charging circuit (Ohms)
N = 100  # Number of turns in the coil
B = 0.2



## Oscillation parameters

amplitude = 0.2
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

z_values = z(t_values)
vz_values = vz(t_values)


def f(t, x_vec):
    """Derivates the state vector."""
    y, vy = x_vec
    dydt = vz(t)
    d2ydt = -(m*g + k*(y-z(t)) + mu * (vy-vz(t))) / m

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




# Plot results using Plotly with two y-axes
fig = go.Figure()
fig.add_trace(go.Scatter(x=t_values, y=y_values-z_values, mode='lines', name='Displacement (y-z)', yaxis='y1'))
fig.add_trace(go.Scatter(x=t_values, y=vz_values, mode='lines', name='Velocity (vz)', yaxis='y1'))
fig.add_trace(go.Scatter(x=t_values, y=vy_values-vz_values, mode='lines', name='Velocity (vy-vz)', yaxis='y2'))
fig.update_layout(
    title='Oscillating Mass Simulation',
    xaxis_title='Time (s)',
    yaxis=dict(title='Displacement (y-z)'),
    yaxis2=dict(title='Velocity (vy-vz)', overlaying='y', side='right'),
    legend_title='Variables'
)
fig.show()