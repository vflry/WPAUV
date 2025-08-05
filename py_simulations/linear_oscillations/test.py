## Vianney Fleury - ENSTA / University of Adelaide - 2025

import numpy as np
import plotly.graph_objects as go

## Simulation constants

g = 9.81  # gravity (m/s^2)
rho_water = 1000  # water density (kg/m^3)


## Simulation variables

## AUV characteristics
length_auv = 0.6  # Length of the AUV (m)
diam_auv = 0.15  # Diameter of the AUV (m)
section_auv = np.pi * (diam_auv / 2) ** 2  # Cross-sectional area of the AUV (m^2)
m0 = 0.5  # Mass of the AUV (kg)

c0 = 0.01 # Damping coef


x0 = m0/(rho_water * section_auv)  # Equilibrium depth of the AUV (m)
z0 = 0 # Initial position of the AUV (m)
z = z0

## Oscillating mass characteristics
m1 = 0.2  # Mass of the oscillating mass (kg)
mu = 0.1 # Damping coefficient of the oscillating mass (N.s/m)
k1 = 8    # Spring constant of the oscillating mass (N/m)


## Wave characteristics
wave_amplitude = 0.5  # Amplitude of the wave (m)
wave_period = 1  # Period of the wave (s)
wave_frequency = 1/wave_period  # Frequency of the wave (Hz)

## Simulation parameters
k0 = section_auv*rho_water*g/m0

def wave_height(t):
    """Calculates the wave height at time t."""
    return wave_amplitude * np.sin(2 * np.pi * wave_frequency * t)

def derivative_wave_height(t):
    """Calculates the derivative of the wave height at time t."""
    return 2 * np.pi * wave_frequency * wave_amplitude * np.cos(2 * np.pi * wave_frequency * t)



tmax = 20  # Total simulation time (s)
dt = 1e-3
t_values = np.arange(0, tmax, dt)  # Time vector

# Initial conditions
z0 = 0.0
vz0 = 0.0
y0 = 0.0
vy0 = 0.0
x_vec = np.array([z0, vz0, y0, vy0])
X = [x_vec]



def f(t, x_vec):
    """Derivates the state vector."""
    z, vz, y, vy = x_vec
    dzdt = vz
    dydt = vy
    wave_ht = wave_height(t)
    fem = - mu * (vy - vz) * abs(vy - vz)
    d2zdt = (-c0 * vz - k0 * (z - wave_ht) - fem - k1 * (z - y)) / m0
    d2ydt = (fem - k1 * (y - z)) / m1

    return np.array([dzdt, d2zdt, dydt, d2ydt])


# RK4 integration
for t in t_values[:-1]:
    rk1 = f(t, x_vec)
    rk2 = f(t + dt/2, x_vec + dt/2 * rk1)
    rk3 = f(t + dt/2, x_vec + dt/2 * rk2)
    rk4 = f(t + dt  , x_vec + dt * rk3)

    x_vec = x_vec + (dt / 6) * (rk1 + 2*rk2 + 2*rk3 + rk4)
    X.append(x_vec)



X = np.array(X)
t_values = np.array(t_values)
z_values = X[:, 0]
y_values = X[:, 2]

# Plotting
fig = go.Figure()

fig.add_trace(go.Scatter(x=t_values, y=wave_height(t_values), mode='lines', name='Wave Height', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=t_values, y=z_values, mode='lines', name='AUV Height', line=dict(color='red', dash='dot')))
fig.add_trace(go.Scatter(x=t_values, y=y_values, mode='lines', name='Oscillating Mass Height', line=dict(color='green')))

fig.update_layout(
    title="Wave, AUV, and Oscillating Mass Heights",
    xaxis_title="Time (s)",
    yaxis_title="Height (m)",
    legend=dict(x=0.02, y=0.98),
    template="plotly_white"
)

fig.show()