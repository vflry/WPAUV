## Vianney Fleury - ENSTA / University of Adelaide - 2025

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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
m1 = 0.4 # Mass of the oscillating mass (kg)
mu_mag = 1.8
mu_friction = 0
mu = mu_mag + mu_friction  # Damping coefficient of the oscillating mass (kg/s)
k1 = 0.4  # Spring constant of the oscillating mass (N/m)




## Linear generator characteristics
Req = 2 # Equivalent resistance of the charging circuit (Ohms)
N = 100  # Number of turns in the coil
B = 0.2



## Wave characteristics
wave_amplitude = 0.5  # Amplitude of the wave (m)
wave_frequency = 2  # Frequency of the wave (Hz)
wave_period = 1/wave_frequency  # Period of the wave (s)

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
    fem = - mu * (vy - vz)
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
vz_values = X[:, 1]
y_values = X[:, 2]
vy_values = X[:, 3]



relative_dist = y_values - z_values  # Relative distance between the AUV and the oscillating mass

print(f"Max relative distance between AUV and oscillating mass: {max(abs(relative_dist)):.2f} m")



## Animation setup
fig, ax = plt.subplots(figsize=(8, 5))
ax.set_xlim(-1, 1)
ax.set_ylim(-1.5, 1.5)
ax.set_title("AUV Floating on Waves (RK4 Simulation)")

x_wave = np.linspace(-1, 1, 500)
wave_line, = ax.plot([], [], 'b-', lw=2, label="Water surface")
auv_body, = ax.plot([], [], 'ro', markersize=15, label="AUV")
mass_body, = ax.plot([], [], 'go', markersize=10, label="Oscillating mass")
relative_dist_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')
power_text = ax.text(0.05, 0.90, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')


def init():
    wave_line.set_data([], [])
    auv_body.set_data([], [])
    mass_body.set_data([], [])
    relative_dist_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    power_text = ax.text(0.05, 0.90, '', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    return wave_line, auv_body, mass_body, relative_dist_text, power_text

# Update frame
def update(frame):
    t = t_values[frame]
    auv_alt = z_values[frame]
    mass_alt = y_values[frame]
    auv_speed = vz_values[frame]
    mass_speed = vy_values[frame]
    relative_dist = abs(mass_alt - auv_alt)
    power = mu_mag * (mass_speed - auv_speed) ** 2

    wave_line.set_data(x_wave, wave_amplitude * np.sin(2 * np.pi * wave_frequency * t + x_wave * 4 * np.pi))
    auv_body.set_data([0], [auv_alt])
    mass_body.set_data([0], [mass_alt])
    relative_dist_text.set_text(f'Relative distance: {relative_dist:.2f} m')
    power_text.set_text(f'Power: {power:.2f} W')

    return wave_line, auv_body, mass_body, relative_dist_text, power_text


ani = FuncAnimation(fig, update, frames=len(t_values), init_func=init,interval=dt*10, blit=True)

plt.legend()
plt.grid()
plt.show()
