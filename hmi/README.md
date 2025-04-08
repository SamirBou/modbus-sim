# Fuel System Control Dashboard

A simple web interface for monitoring and controlling our virtual fuel system. This dashboard connects to the Modbus fuel system simulation and gives you a visual way to interact with it.

## Features

- Real-time fuel level visualization
- Interactive controls for the fuel system
- Flow rate adjustments
- Auto/Manual mode switching
- Emergency stop button
- Visual alerts for fuel spills and other conditions

## Files In This Folder

- `HMI.py`: The main program that runs the web interface
- `templates/index.html`: The dashboard web page
- `static/`: JavaScript libraries and resources
- `requirements.txt`: Required Python packages

## Getting Started

1. Make sure the fuel system simulation is running first (`plc.py`)

2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the dashboard:
   ```bash
   python HMI.py
   ```

4. Open your web browser and go to:
   ```
   http://localhost:8090
   ```

## How to Use the Dashboard

### Main Controls

- **Main Switch**: Turns the fuel system on or off
- **Mode Selection**: Toggles between Automatic and Manual modes
- **Emergency Stop**: Instantly shuts down the system in case of problems

### Flow Controls

- **Inlet Flow Rate**: Adjust how fast fuel enters the tank (manual mode only)
- **Outlet Flow Rate**: Adjust how fast fuel leaves the tank (manual mode only)

### Status Indicators

- **Fuel Level**: Shows current fill level with visual indicator
- **System Status**: Shows if the fuel system is running or stopped
- **Sensor Status**: Shows if inlet and outlet sensors are active
- **Overflow Alert**: Warns when the fuel tank reaches maximum capacity

## Understanding Auto vs Manual Mode

- **Automatic Mode**: System maintains the fuel level around 2/3 capacity
  - Both inflow and outflow rates are controlled automatically
  - Flow rate sliders are disabled
  - System prevents overflow and maintains optimal fuel level
  
- **Manual Mode**: You control all aspects of the fuel system
  - Set both inflow and outflow rates as desired
  - Be careful not to overflow the fuel tank!

## Settings

The dashboard connects to the fuel system simulation at:
- Host: 0.0.0.0 (localhost)
- Port: 502 (standard Modbus port)

The web interface runs on:
- Host: 0.0.0.0 (accessible from any network interface)
- Port: 8090

## Shutting Down

Close your browser and press Ctrl+C in the terminal running the dashboard.

This is a demonstration system - have fun experimenting with it!
