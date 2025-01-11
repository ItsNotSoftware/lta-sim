# LTA-Sim

A simulator for a Lane Tracking Assistance (LTA) system, including a vehicle model and customizable highway configurations.

## Overview

This project simulates a highway environment for testing the LTA system. The highway can be either flat or sinusoidal, defined by the equation `A * sin(w * t)`, where:
- `A` is the amplitude in meters.
- `w` is the angular frequency in radians/second.

## Features
- Simulates realistic lane tracking scenarios.
- Supports flat and sinusoidal highway profiles.
- Customizable amplitude and frequency parameters.
- Real-time data visualization via [PlotJuggler](https://github.com/facontidavide/PlotJuggler).
- Interactive control to steer the car out of its path.

---

## How to Run

### Option 1: Using `uv` Project Manager

1. Install [uv](https://github.com/astral-sh/uv):
   ```bash
   pip install uv
   ```
2. Run the simulator:
   ```bash
   uv lta-sim <amplitude> <frequency>
   ```
   **Note:** For best results, ensure `frequency <= 0.002` and `aplitude <= 6`.

---

### Option 2: Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the simulator:
   ```bash
   python lta-sim.py <amplitude> <frequency>
   ```
      **Note:** For best results, ensure `frequency <= 0.002` and `aplitude <= 6`.

---

## Real-Time Visualization with PlotJuggler

You can connect [PlotJuggler](https://github.com/facontidavide/PlotJuggler) to the simulator via UDP JSON on port `5005` for real-time data visualization. Ensure PlotJuggler is configured to listen on this port for incoming data.

---

## Interactive Controls

- **Steer the car out of its path:** Use `A` and `D` or the **left** and **right arrow keys**.
- **Toggle controller:** Press `Space` to enable/disable the controller.
- **Quit the simulation:** Press `Q`.

---

## Requirements

- Python 3.8 or later
- Required Python packages (listed in `requirements.txt`)

---

## Example Usage

Run the simulator with a sinusoidal highway profile:
```bash
uv lta-sim 3 0.001
```

This will simulate a highway with an amplitude of 3 meters and a frequency of 0.001 rad/s.

---

## Tips for Optimal Use

- Lower frequencies (e.g., `<= 0.002`) result in smoother simulations and better performance.
- For flat highways, set amplitude to `0`.

---
