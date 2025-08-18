# Wave Powered AUV (WPAUV)

**Vianney Fleury - University of Adelaide / ENSTA Bretagne 2025**

This repository contains simulation codes, Arduino firmware, data analysis scripts, and CAD designs for the Wave Powered AUV project.

## Table of Contents
- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Arduino Codes](#arduino-codes)
- [Electrical Wirings](#electrical-wirings)
- [Python Simulations](#python-simulations)
- [Data Analysis](#data-analysis)
- [CAD Designs](#cad-designs)
- [Installation & Usage](#installation--usage)
- [Experimental Results](#experimental-results)

## Project Overview

The WPAUV project investigates wave energy harvesting mechanisms for autonomous underwater vehicles. Two main approaches are explored:

1. **Linear Oscillations Design**: Utilizes vertical wave motion to drive an internal oscillating mass
2. **Pendulum Design (Seaturns)**: Exploits roll and pitch motions to generate power through air flow

### Key Features
- Real-time data logging with IMU and distance sensors
- Numerical simulations of wave-energy conversion systems
- Parameter optimization for different sea conditions
- Experimental validation with sensor fusion algorithms

## Repository Structure

```
WPAUV/
├── arduino/                    # Embedded systems and data logging
│   ├── data_logger/           # IMU data acquisition
│   └── laserandvoltage_logger/ # Multi-sensor logging system
├── py_simulations/            # Numerical simulations
│   ├── linear_oscillations/   # Linear oscillator models
│   └── pendulum/              # Pendulum-based energy harvesting
├── logs_analysis/             # Data processing and analysis
│   ├── imu logging/           # IMU data analysis and calibration
│   └── laser logging/         # Distance measurement processing
├── electrical_wirings/        # Arduino wiring diagrams and photos
├── CAD/                       # 3D mechanical designs
├── literature/                # Research documentation
└── videos/                    # Experimental recordings
```

## Arduino Codes

### Data Logger (`arduino/data_logger/`)

**Purpose**: High-frequency IMU data acquisition for attitude estimation.

**Hardware Requirements**:
- Arduino Uno/Mega
- MPU6050 IMU sensor
- SD card module

**Key Features**:
- CSV data format: `time_ms,ax,ay,az,gx,gy,gz`
- Real-time SD card logging

**Usage**:
```cpp
// Connect MPU6050 via I2C (SDA/SCL)
// Connect SD card via SPI (CS pin 10)
// Upload code and insert formatted SD card
```

### Laser and Voltage Logger (`arduino/laserandvoltage_logger/`)

**Purpose**: Multi-sensor data acquisition for energy harvesting validation.

**Hardware Requirements**:
- Arduino Mega 2560
- VL53L1X laser distance sensor
- Voltage measurement circuits (3 channels)
- SD card module

**Key Features**:
- High frequency sampling
- Simultaneous distance and voltage logging
- CSV format: `Time_ms,Distance_mm,VA0_V,VA1_V,VA2_V`

**Usage**:
```cpp
// Connect VL53L1X via I2C
// Connect voltage dividers to A0, A1, A2
// CS pin 53 for SD card on Mega
// Adjust VREF constant for your reference voltage
```

## Electrical Wirings

The `electrical_wirings/` folder contains photographs and documentation of the Arduino hardware setups used in the project.


### Data Logger Setup
- **MPU6050 IMU**: Connected via I2C (SDA/SCL pins)
- **SD Card Module**: SPI connection (CS pin 10 for Uno, pin 53 for Mega)
- **Power Supply**: 5V from Arduino or external source

### Laser and Voltage Logger Setup  
- **VL53L1X Sensor**: I2C connection for distance measurements
- **Voltage Dividers**: Three analog channels (A0, A1, A2) for voltage monitoring
- **SD Card Module**: SPI connection (CS pin 53 for Mega)
- **Power Management**: Stable 5V supply for consistent measurements

### Usage
Refer to the photos in `electrical_wirings/`

## Python Simulations

### Prerequisites
The project includes pre-configured virtual environments with all required libraries:
- numpy, matplotlib, scipy
- pandas, plotly 
- ahrs (attitude and heading reference system)

**Activate the environment before running simulations**:
```bash
# macOS/Linux  
source venv/bin/activate
```

### Linear Oscillations (`py_simulations/linear_oscillations/`)

#### Basic Oscillation Model (`oscillations_sim.py`)
**Purpose**: Simulate AUV heave motion response to wave forcing.

**Key Parameters**:
- AUV dimensions: 0.6m length, 0.15m diameter
- Mass: 0.5 kg
- Damping coefficient: 0.01
- Wave amplitude: 0.5m, period: 1s

**Usage**:
```bash
python oscillations_sim.py
```

**Output**: Time-domain plot of AUV vertical motion vs wave elevation.

#### Oscillating Mass System (`oscillations_sim_withmass.py`)
**Purpose**: Simulate internal oscillating mass for energy harvesting.

**Additional Parameters**:
- Oscillating mass: 0.4 kg
- Spring constant: variable
- Electromagnetic damping: variable

**Features**:
- RK4 numerical integration
- Energy harvesting calculations
- Relative motion analysis

#### Parameter Studies
- **`mu_tests.py`**: Electromagnetic damping coefficient optimization
- **`k1_tests.py`**: Spring constant sensitivity analysis
- **`oscillations_sim_display.py`**: Animated visualization of AUV motion

### Pendulum Design (`py_simulations/pendulum/`)

#### Seaturns Simulation (`seaturns_sim.py`)
**Purpose**: Model large-scale pendulum system with air turbines.

**System Parameters**:
- Tank dimensions: 4-6m diameter, 10m length
- Turbine diameter: 1m, efficiency: 50%
- Maximum roll angle: 0.8 rad
- Wave period: 10s, height: 1.8m

**Key Functions**:
```python
roll_angle(t)        # Roll motion as function of time
volumic_flow_rate(t) # Air flow rate calculation
power(t)             # Instantaneous power output
```

**Usage**:
```bash
python seaturns_sim.py
```

**Output**: 
- Power vs time plots
- Parameter sensitivity analysis
- Average power calculations

#### Pendulum Dynamics (`pendulum_sim.py`, `pendulum_sim_dyn.py`)
**Purpose**: Detailed pendulum motion simulation with wave forcing.

**Features**:
- RK2 integration scheme
- Real-time power calculations
- Interactive Plotly animations
- Torque and angular velocity analysis

#### Power Estimation (`power_estimations.py`)
**Purpose**: Optimize damping coefficients for maximum power extraction.

**Usage**:
```bash
python power_estimations.py
```

## Data Analysis

### Prerequisites
Use the pre-configured virtual environment:
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
```

### IMU Data Analysis (`logs_analysis/imu logging/`)

#### Automatic Calibration (`calib.py`)
**Purpose**: Determine optimal IMU orientation matrix from 48 possible combinations.

**Features**:
- Tests all axis permutations and sign combinations
- Mahony filter implementation
- Automatic best configuration selection

**Usage**:
```bash
python3 calib.py
```

#### Attitude Estimation (`logs_mahony.py`, `logs_madgwick.py`)
**Purpose**: Convert raw IMU data to attitude angles using sensor fusion.

**Algorithms**:
- Mahony filter (complementary filter approach)
- Madgwick filter (gradient descent optimization)

**Key Features**:
- Quaternion-based attitude representation
- Euler angle conversion (ZXY sequence)
- Interactive Plotly visualizations

**Usage**:
```bash
python3 logs_mahony.py  # For Mahony filter
python3 logs_madgwick.py  # For Madgwick filter
```

#### Raw Data Processing (`raw_delogging.py`)
**Purpose**: Basic attitude calculation without filtering.

**Features**:
- Direct accelerometer-based tilt calculation
- Roll, pitch, and inclination angles
- Useful for quick data validation

### Laser Data Analysis (`logs_analysis/laser logging/`)

#### Laser Data Processing (`laser_delog.py`)
**Purpose**: Clean and analyze distance measurement data.

**Features**:
- Binary file cleaning and ASCII conversion
- Time series reconstruction with restart handling
- Voltage and distance correlation analysis
- Interactive plotting with Plotly

**Usage**:
```bash
python3 laser_delog.py
```

**Input Files**: Raw CSV logs from Arduino
**Output**: Cleaned time series data and analysis plots

## CAD Designs

### Files
- **`oscillating_design v15.f3z`**: Complete mechanical design (Fusion 360)
- **`logger v4.f3z`**: Data logger housing design

### Features
- Waterproof enclosures for electronics
- Mechanical interfaces for oscillating masses
- Sensor mounting solutions
- Hydrodynamic hull design

## Installation & Usage

### Setting up the Development Environment

1. **Clone the repository**:
```bash
git clone https://github.com/vflry/WPAUV.git
cd WPAUV
```

2. **Activate Python virtual environment**:
The project uses pre-configured virtual environments with all required libraries.

**On macOS/Linux**:
```bash
# Activate the virtual environment
source venv/bin/activate
```

**Verify installation**:
```bash
# Check that all libraries are available
python -c "import numpy, matplotlib, scipy, pandas, plotly, ahrs; print('All libraries loaded successfully')"
```

3. **Arduino IDE Setup**:
   - Install libraries: MPU6050, VL53L1X, SD, SPI
   - Select appropriate board (Uno/Mega)
   - Configure I2C and SPI connections
   - **Refer to `electrical_wirings/` folder for connection photos and diagrams**

### Running Simulations

**Important**: Always activate the virtual environment first:
```bash
source venv/bin/activate  # macOS/Linux
```

1. **Basic linear oscillation**:
```bash
cd py_simulations/linear_oscillations/
python3 oscillations_sim.py
```

2. **Parameter optimization**:
```bash
python3 mu_tests.py  # Damping analysis
python3 k1_tests.py  # Spring constant study
```

3. **Pendulum system**:
```bash
cd ../pendulum/
python3 seaturns_sim.py  # Full system simulation
python3 pendulum_sim_dyn.py  # Animated dynamics
```

### Data Analysis Workflow

**Important**: Activate the virtual environment before analysis:
```bash
source venv/bin/activate  # macOS/Linux
```

1. **Collect data** using Arduino loggers
2. **Calibrate IMU** orientation:
```bash
cd logs_analysis/imu\ logging/
python3 calib.py
```

3. **Process logger attitude data**:
```bash
python3 logs_mahony.py
```

4. **Analyze distance measurements**:
```bash
cd ../laser\ logging/
python3 laser_delog.py
```



## Contributing

This is an academic research project.

**Author**: Vianney Fleury  
**Institution**: ENSTA Bretagne / University of Adelaide  
**Year**: 2025  

