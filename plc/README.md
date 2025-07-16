# PLC Simulation

A Modbus TCP server for simulating the Aloha Water Treatment process. The PLC provides Modbus registers for external clients to monitor and control the process.

## How to Run

1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python plc.py`
3. Server starts on port 502 (connects to HMI and external clients)

## Features

- Simulates water treatment process variables and control logic
- Provides Modbus registers for external clients to interact with
- Implements safety interlocks and alarms
