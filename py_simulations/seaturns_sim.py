# Simulation for the seaturns design

# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# Design parameters

###################
# Tank dimensions #
###################

tank_inner_diam = 4 # m
tank_outer_diam = 6 # m
tank_length = 10 # m
#   Tank volume
tank_vol = np.pi * (tank_outer_diam**2 - tank_inner_diam**2) * tank_length # m^3

# We assume the tank is filled halfway with water
water_vol = tank_vol / 2 # m^3
water_mass = water_vol * 1000 # kg

# Air / Water interface area
section_area = (tank_outer_diam-tank_inner_diam)*tank_length/2 # m^2


########################
# Wave characteristics #
########################

wave_height = 1.8 # m
wave_period = 10 # s
wave_frequency = 1 / wave_period # Hz


###########################
# Turbine characteristics #
###########################

turbine_diam = 1 # m
turbine_efficiency = 0.5
turbine_area = np.pi * (turbine_diam / 2)**2 # m^2

air_density = 1.2 # kg/m^3





# Assumption : max roll angle
max_roll = 0.8 # rad

# The tank will roll from -max_roll to max_roll and back to -max_roll in a wave period
# The roll speed will follow a sine curve

# Roll angle as a function of time :
def roll_angle(t):
    return max_roll * np.sin(2 * np.pi * (t+wave_period/4) / wave_period)

# Roll speed as a function of time :
def roll_speed(t):
    return (max_roll * 2 * np.pi / wave_period) * np.cos(2 * np.pi * (t + wave_period / 4) / wave_period)

# As a first approximation, we assume that the flow rate is directly proportional to the roll speed
# flow_rate as a function of time :
def volumic_flow_rate(t):
    return abs(roll_speed(t)) * (tank_inner_diam + tank_outer_diam)/4 * section_area # m^3/s

def power(t):
    flow_rate = volumic_flow_rate(t)
    velocity = flow_rate / turbine_area
    return 0.5 * air_density * turbine_area * velocity**3 * turbine_efficiency









t = np.linspace(0, wave_period, 1000)
power_values = np.vectorize(power)(t)
plt.plot(t, power_values, label='Theoretical Power Output', color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Power (W)')
plt.title('Theorical power Output of the Seaturns Design')

# Compute average power
t_start = 0
t_end = wave_period
average_power, _ = quad(power, t_start, t_end)
average_power /= (t_end - t_start)
print(f"Average Power: {average_power:.4f} W")

# Plot average power as a horizontal line
plt.plot(t, [average_power] * len(t), label='Average Power', color='red')


turbine_diameters = np.linspace(0.1, 2, 100)
turbine_powers = []
for diameter in turbine_diameters:
    turbine_diam = diameter
    average_power, _ = quad(power, t_start, t_end)
    average_power /= (t_end - t_start)
    turbine_powers.append(average_power)

turbine_diam = 1 # m

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(turbine_diameters, turbine_powers, label='Average Power vs Turbine Diameter', color='blue')
plt.xlabel('Turbine Diameter (m)')
plt.ylabel('Average Power (W)')
plt.title('Average Power Output vs Turbine Area')


max_tilt_angles = np.linspace(0, 1.5, 100)
turbine_powers = []
for angle in max_tilt_angles:
    max_roll = angle
    average_power, _ = quad(power, t_start, t_end)
    average_power /= (t_end - t_start)
    turbine_powers.append(average_power)

max_roll = 0.8 # rad

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(max_tilt_angles, turbine_powers, label='Average Power vs Max Tilt Angle', color='green')
plt.xlabel('Max Tilt Angle (rad)')
plt.ylabel('Average Power (W)')
plt.title('Average Power Output vs Max Tilt Angle')


wave_periods = np.linspace(5, 20, 100)
turbine_powers = []
for period in wave_periods:
    wave_period = period
    average_power, _ = quad(power, t_start, t_end)
    average_power /= (t_end - t_start)
    turbine_powers.append(average_power)

wave_period = 10 # s

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(wave_periods, turbine_powers, label='Average Power vs Wave Period', color='orange')
plt.xlabel('Wave Period (s)')
plt.ylabel('Average Power (W)')
plt.title('Average Power Output vs Wave Period')

plt.legend()
plt.show()