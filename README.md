# Aloha Water Treatment - Modbus Simulation

A Modbus TCP simulation of a water treatment plant control system. This project provides PLCs and HMIs for generating Modbus traffic and simulating a process that external Modbus clients can interact with.

## Overview

This simulation includes:
- Multi-stage water treatment process (intake, filtration, disinfection)
- Modbus registers for monitoring and controlling the process
- Automatic and manual operating modes
- Safety interlocks and alarms

## Components

### PLC Simulation (`plc/`)
- Modbus TCP server (port 502)
- Simulates water treatment control logic and process variables
- Provides Modbus registers for external clients

### HMI Dashboard (`hmi/`)
- Web-based interface for monitoring and controlling the process
- Reads and writes Modbus registers

## Quick Start

1. **Start the PLC simulation:**
   ```bash
   cd plc
   pip install -r requirements.txt
   python plc.py
   ```

2. **Launch the HMI dashboard:**
   ```bash
   cd hmi
   pip install -r requirements.txt
   python HMI.py
   ```

3. **Access the HMI:**
   Open http://localhost:8090 in your browser

4. **Test with a Modbus client:**
   Connect to the PLC on port 502 to interact with the process.

## Requirements

- Python 3.7+ with Flask and pymodbus installed
- A web browser for the HMI
