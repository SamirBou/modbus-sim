# Fuel System Simulation with Modbus

This is a simple simulation of a fuel system control using Modbus. It's designed to demonstrate industrial automation concepts without the complexity of a real PLC system.

## What You Can Do With This Demo

- Watch a virtual fuel tank fill and empty in real-time
- Control a simulated fuel system with switches
- Try different operating modes (automatic vs. manual)
- Practice handling emergency stop situations
- Learn Modbus communication basics

## What's Included

- `plc.py`: The main program that runs the simulation
- `plcLogic.py`: The tank control logic
- `requirements.txt`: Python packages needed

## Quick Start

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the simulation:
   ```bash
   python plc.py
   ```

3. Connect with any Modbus client to port 502

## How It Works

Our virtual fuel system follows these basic rules:

1. The fuel system turns on when the main switch is on (unless emergency stop is activated)
2. In automatic mode, the system tries to keep the fuel level about 2/3 full:
   - Inflow adjusts based on current fuel level
   - Outflow remains constant
3. In manual mode, you control all fuel flow rates
4. If the tank overfills, a fuel spill is detected

## Playing with the Demo

You can use any Modbus client to interact with these registers:

### Holding Registers

| Address | Description        | Values              |
|---------|--------------------|---------------------|
| 0       | Fuel Level         | 0-10000 units       |
| 1       | Emergency Stop     | 0=Off, 1=On         |
| 2       | Main Switch        | 0=Off, 1=On         |
| 3       | System Status      | 0=Off, 1=On         |
| 4       | Inlet Sensor       | 0=Off, 1=On         |
| 5       | Outlet Sensor      | 0=Off, 1=On         |
| 6       | Inlet Flow Rate    | Units/second        |
| 7       | Outlet Flow Rate   | Units/second        |
| 8       | Operating Mode     | 0=Auto, 1=Manual    |
| 9       | Spill Detection    | 0=No Spill, 1=Spill |

### Coils (On/Off Controls)

| Address | Control            | Values            |
|---------|--------------------|-------------------|
| 0       | Emergency Stop     | 0=Off, 1=On       |
| 1       | Main Switch        | 0=Off, 1=On       |
| 2       | Pump               | 0=Off, 1=On       |
| 3       | Inlet Sensor       | 0=Off, 1=On       |
| 4       | Outlet Sensor      | 0=Off, 1=On       |
| 5       | Mode Selection     | 0=Auto, 1=Manual  |
| 6       | Spill Indicator    | 0=No Spill, 1=Spill |

## Fun Experiments

1. **Filling the tank**: Turn on the main switch in auto mode and watch how it manages the fuel level
2. **Manual control**: Switch to manual mode and adjust fuel inflow/outflow rates yourself
3. **Emergency scenario**: Press emergency stop while the fuel system is running
4. **Overflow**: In manual mode, set inflow much higher than outflow and watch for fuel spill detection

## Exiting the Demo

Press Ctrl+C in the terminal to stop the simulation.

Remember, this is just for learning and fun - not for controlling real tanks! 😊
