## Vianney Fleury - ENSTA / University of Adelaide - 2025

import numpy as np
import matplotlib.pyplot as plt

## Simulation constants

g = 9.81  # gravity (m/s^2)
rho_water = 1000  # water density (kg/m^3)


## Simulation variables

## AUV characteristics
length_auv = 0.6  # Length of the AUV (m)
diam_auv = 0.15  # Diameter of the AUV (m)
section_auv = np.pi * (diam_auv / 2) ** 2  # Cross-sectional area of the AUV (m^2)

c = 0.01 # Damping coef

##### AUV mass : effect on oscillations to be studied #####
mass_auv = 0.5  # Mass of the AUV (kg)


x0 = mass_auv/(rho_water * section_auv)  # Equilibrium depth of the AUV (m)
z0 = 0 # Initial position of the AUV (m)
z = z0


## Wave characteristics
wave_amplitude = 0.5  # Amplitude of the wave (m)
wave_period = 1  # Period of the wave (s)
wave_frequency = 1/wave_period  # Frequency of the wave (Hz)

## Simulation parameters
k = section_auv*rho_water*g/mass_auv

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
v0 = 0.0
z_vec = np.array([z0, v0])
Z = [z_vec]



def f(t, z_vec):
    """Derivates the state vector."""
    z, v = z_vec
    dzdt = v
    dvdt = k * (wave_height(t) - z) + c/mass_auv * (derivative_wave_height(t) - v)
    return np.array([dzdt, dvdt])


# RK4 integration
for t in t_values[:-1]:
    k1 = f(t, z_vec)
    k2 = f(t + dt/2, z_vec + dt/2 * k1)
    k3 = f(t + dt/2, z_vec + dt/2 * k2)
    k4 = f(t + dt, z_vec + dt * k3)

    z_vec = z_vec + (dt / 6) * (k1 + 2*k2 + 2*k3 + k4)
    Z.append(z_vec)



Z = np.array(Z)
t_values = np.array(t_values)
z_values = Z[:, 0]



# Convert to array for plotting
Z = np.array(Z)
z_values = Z[:, 0]

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(t_values, z_values, label='AUV vertical motion z(t)')
plt.plot(t_values, wave_height(t_values), '--', label='Wave elevation η(t)')
plt.xlabel('Time (s)')
plt.ylabel('Vertical Position (m)')
plt.title('AUV Heave Motion on Waves (RK4 Integration)')
plt.grid()
plt.legend()
plt.show()