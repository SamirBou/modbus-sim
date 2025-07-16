# HMI Dashboard

A web-based interface for interacting with the Aloha Water Treatment simulation. The HMI reads and writes Modbus registers to monitor and control the process.

## How to Run

1. Start the PLC first (see ../plc/README.md)
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python HMI.py`
4. Open browser to: http://localhost:8090

## Features

- Monitor process variables (e.g., tank levels, flow rates)
- Control pumps, valves, and operating modes
- View and acknowledge alarms
