from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from threading import Thread, Event
from plcLogic import plcLogic
import time
import signal
import sys
import os
from multiprocessing import Process

# Basic settings for our fuel system
MODBUS_HOST = "0.0.0.0"  # Listen on all network interfaces
MODBUS_PORT = 502        # Standard Modbus port
MODBUS_REGISTER_COUNT = 10
TANK_MAX = 10000         # Maximum fuel capacity in units
RATE_MIN = 500           # Minimum fuel flow rate in units/second

# Initial values when starting the system
INIT_LEVEL = 0           # Start with an empty fuel tank for demo purposes
INIT_ESTOP = 0           # Emergency stop off
INIT_SWITCH = 0          # Main switch off
INIT_MOTOR = 0           # Fuel system off
INIT_IN_SENS = 0         # Inlet sensor off
INIT_OUT_SENS = 0        # Outlet sensor off
INIT_IN_RATE = 0         # No fuel inlet flow
INIT_OUT_RATE = 0        # No fuel outlet flow
INIT_AUTO = 0            # Auto mode on (0=auto, 1=manual)
INIT_SPILL = 0           # No fuel spillage

# Register addresses - these are like memory slots for the PLC
# Holding registers store numeric values (fuel level, flow rates, etc.)
HOLDING_REGISTER_BASE = 0
HOLDING_REGISTER_LEVEL = 0      # Fuel tank level
HOLDING_REGISTER_ESTOP = 1      # Emergency stop status
HOLDING_REGISTER_SWITCH = 2     # Main switch status
HOLDING_REGISTER_MOTOR = 3      # Fuel system status 
HOLDING_REGISTER_IN_SENS = 4    # Inlet sensor status
HOLDING_REGISTER_OUT_SENS = 5   # Outlet sensor status
HOLDING_REGISTER_IN_RATE = 6    # Fuel inlet flow rate
HOLDING_REGISTER_OUT_RATE = 7   # Fuel outlet flow rate
HOLDING_REGISTER_AUTO = 8       # Mode (0=auto, 1=manual)
HOLDING_REGISTER_SPILL = 9      # Fuel spillage status

# Coils store simple on/off values (switches and indicators)
COIL_BASE = 0
COIL_ESTOP = 0      # Emergency stop button
COIL_SWITCH = 1     # Main power switch
COIL_MOTOR = 2      # Motor/pump status
COIL_IN_SENS = 3    # Inlet sensor
COIL_OUT_SENS = 4   # Outlet sensor
COIL_AUTO = 5       # Mode switch (0=auto, 1=manual)
COIL_SPILL = 6      # Spillage indicator

# Runtime flags
active = True             # Controls if the system is running
server_started = Event()  # Signals when the server is ready

def setup_modbus_server():
    """Set up the Modbus server with our fuel system registers and values"""
    
    # Initialize our tank system values
    holding_register_values = [
        INIT_LEVEL, INIT_ESTOP, INIT_SWITCH, INIT_MOTOR,
        INIT_IN_SENS, INIT_OUT_SENS, INIT_IN_RATE, 
        INIT_OUT_RATE, INIT_AUTO, INIT_SPILL
    ]
    
    coil_values = [
        INIT_ESTOP, INIT_SWITCH, INIT_MOTOR,
        INIT_IN_SENS, INIT_OUT_SENS, INIT_SPILL, INIT_AUTO
    ]
    
    # Create the data storage for our Modbus server
    holding_registers = ModbusSequentialDataBlock(0x00, [0] + holding_register_values + 
                               [0] * (MODBUS_REGISTER_COUNT - len(holding_register_values)))
    
    coils = ModbusSequentialDataBlock(0x00, [0] + coil_values + 
                               [0] * (MODBUS_REGISTER_COUNT - len(coil_values)))
    
    input_registers = ModbusSequentialDataBlock(0x00, [0] * MODBUS_REGISTER_COUNT)
    discrete_inputs = ModbusSequentialDataBlock(0x00, [0] * MODBUS_REGISTER_COUNT)

    # Add some product info (like a nameplate on real equipment)
    device = ModbusDeviceIdentification()
    device.VendorName = "FuelTech Industries"
    device.ProductCode = "FT-5300"
    device.VendorUrl = "https://fueltechindustries.com"
    device.ProductName = "TankMaster Pro"
    device.ModelName = "Series 5300"
    device.MajorMinorRevision = "2.1.5"

    # Set up the Modbus server's data store
    modbus_store = ModbusSlaveContext(
        di=discrete_inputs,  # Read-only status bits
        co=coils,            # Read-write switches
        hr=holding_registers, # Read-write values
        ir=input_registers   # Read-only values
    )

    # Create the final server context
    modbus_context = ModbusServerContext(slaves=modbus_store, single=True)
    
    return modbus_context, device, discrete_inputs, coils, holding_registers, input_registers

def handle_signal(sig, frame):
    """Handle shutdown signals for a clean exit"""
    global active
    print("\nShutting down fuel system simulation...")
    active = False
    sys.exit(0)

def run_modbus_server():
    """Run the Modbus server and fuel system control logic"""
    global active
    
    # Set up clean shutdown with Ctrl+C
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Create our server with the tank data
    modbus_context, device, discrete_inputs, coils, holding_registers, input_registers = setup_modbus_server()

    # Start the Modbus server in the background
    serverThread = Thread(
        target=StartTcpServer,
        kwargs={
            'context': modbus_context,
            'identity': device,
            'address': (MODBUS_HOST, MODBUS_PORT),
        },
        daemon=True
    )
    serverThread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    server_started.set()
    print("Fuel system simulation running on port", MODBUS_PORT)
    
    # Main system loop - keeps checking and updating the fuel system state
    try:
        while active:
            try:
                # Get the latest values from all registers
                discrete_inputs.setValues(0, discrete_inputs.getValues(0, MODBUS_REGISTER_COUNT + 1))
                coils.setValues(0, coils.getValues(0, MODBUS_REGISTER_COUNT + 1))
                holding_registers.setValues(0, holding_registers.getValues(0, MODBUS_REGISTER_COUNT + 1))
                input_registers.setValues(0, input_registers.getValues(0, MODBUS_REGISTER_COUNT + 1))

                # Run our tank control logic
                plcLogic(discrete_inputs, coils, holding_registers, input_registers)
            except Exception as e:
                print(f"System error: {e}")
                
            time.sleep(1)  # Update once per second
    except KeyboardInterrupt:
        print("Stopping simulation...")
    except Exception as e:
        print(f"Critical failure: {e}")

def main():
    """Start the tank simulation system"""
    run_modbus_server()

if __name__ == "__main__":
    main()
