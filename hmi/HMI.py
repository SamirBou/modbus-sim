from flask import Flask, render_template, request, jsonify
from pymodbus.client import ModbusTcpClient
import threading
import time

# Server settings
FLASK_SERVER_IP = "0.0.0.0"      # Web interface address
FLASK_SERVER_PORT = 8090         # Web interface port
MODBUS_SERVER_IP = "0.0.0.0"     # Modbus server address
MODBUS_SERVER_PORT = 502         # Standard Modbus port
REGISTER_COUNT = 10              # Number of registers to monitor
TANK_MAX = 10000                 # Fuel tank capacity in units

# Modbus addresses for switches and status lights
COIL_BASE = 0
COIL_ESTOP = 0      # Emergency stop button
COIL_SWITCH = 1     # Main power switch 
COIL_MOTOR = 2      # Fuel system status
COIL_IN_SENS = 3    # Fuel inlet sensor
COIL_OUT_SENS = 4   # Fuel outlet sensor
COIL_AUTO = 5       # Auto/manual switch (0=auto, 1=manual)
COIL_SPILL = 6      # Fuel overflow indicator

# Modbus addresses for numeric displays and controls
HOLDING_REGISTER_BASE = 0
HOLDING_REGISTER_LEVEL = 0     # Fuel level display
HOLDING_REGISTER_ESTOP = 1     # Emergency stop status
HOLDING_REGISTER_SWITCH = 2    # Main switch status
HOLDING_REGISTER_MOTOR = 3     # Fuel system status
HOLDING_REGISTER_IN_SENS = 4   # Fuel inlet sensor status
HOLDING_REGISTER_OUT_SENS = 5  # Fuel outlet sensor status
HOLDING_REGISTER_IN_RATE = 6   # Fuel inlet flow rate control
HOLDING_REGISTER_OUT_RATE = 7  # Fuel outlet flow rate control
HOLDING_REGISTER_AUTO = 8      # Mode selection (0=auto, 1=manual)
HOLDING_REGISTER_SPILL = 9     # Fuel overflow status

class ModbusClient:
    def __init__(self, server_ip, server_port):
        """Connect to the Modbus server and start monitoring the fuel system"""
        # Create connection to the tank system
        self.modbus_client = ModbusTcpClient(host=server_ip, port=server_port, auto_open=True, debug=False)
        self.modbus_client.connect()
        
        # Start reading data in background
        self.thread = threading.Thread(target=self.read_data, daemon=True)
        self.thread.start()

        # Set up data storage for UI
        self.data = {
            'emergencyStopStatus': None,
            'pumpSwitchStatus': None,
            'pumpStatus': None,
            'inflowMeterStatus': None,
            'outflowMeterStatus': None,
            'overflowed': None,
            'inflowMode': None,
            'tankVolume': None,
            'maxVolume': TANK_MAX,
            'inflowRate': None,
            'outflowRate': None
        }

    def read_data(self):
        """Continuously read tank data from the Modbus server"""
        while True:
            try:
                # Read the on/off values (switches, indicators)
                coil_response = self.modbus_client.read_coils(COIL_BASE, REGISTER_COUNT)
                if not coil_response.isError():
                    coil_values = coil_response.bits
                    self.data['emergencyStopStatus'] = int(coil_values[COIL_ESTOP]) if coil_values[COIL_ESTOP] is not None else None
                    self.data['pumpSwitchStatus'] = int(coil_values[COIL_SWITCH]) if coil_values[COIL_SWITCH] is not None else None
                    self.data['pumpStatus'] = int(coil_values[COIL_MOTOR]) if coil_values[COIL_MOTOR] is not None else None
                    self.data['inflowMeterStatus'] = int(coil_values[COIL_IN_SENS]) if coil_values[COIL_IN_SENS] is not None else None
                    self.data['outflowMeterStatus'] = int(coil_values[COIL_OUT_SENS]) if coil_values[COIL_OUT_SENS] is not None else None
                    self.data['overflowed'] = int(coil_values[COIL_SPILL]) if coil_values[COIL_SPILL] is not None else None
                    self.data['inflowMode'] = int(coil_values[COIL_AUTO]) if coil_values[COIL_AUTO] is not None else None
            except Exception as e:
                print(f"Error reading switches: {e}")

            try:
                # Read the numeric values (tank level, flow rates)
                hr_response = self.modbus_client.read_holding_registers(HOLDING_REGISTER_BASE, REGISTER_COUNT)
                if not hr_response.isError():
                    hr_values = hr_response.registers
                    self.data['tankVolume'] = hr_values[HOLDING_REGISTER_LEVEL]
                    self.data['emergencyStopStatus'] = hr_values[HOLDING_REGISTER_ESTOP]
                    self.data['pumpSwitchStatus'] = hr_values[HOLDING_REGISTER_SWITCH]
                    self.data['pumpStatus'] = hr_values[HOLDING_REGISTER_MOTOR]
                    self.data['inflowMeterStatus'] = hr_values[HOLDING_REGISTER_IN_SENS]
                    self.data['outflowMeterStatus'] = hr_values[HOLDING_REGISTER_OUT_SENS]
                    self.data['inflowRate'] = hr_values[HOLDING_REGISTER_IN_RATE]
                    self.data['outflowRate'] = hr_values[HOLDING_REGISTER_OUT_RATE]
                    self.data['inflowMode'] = hr_values[HOLDING_REGISTER_AUTO]
                    self.data['overflowed'] = hr_values[HOLDING_REGISTER_SPILL]
            except Exception as e:
                print(f"Error reading values: {e}")
                
            # Wait a bit before next update
            time.sleep(1)

    def write_data(self, control, value):
        """Send control commands to the fuel system"""
        print(f"Sending command: {control}={value}")
        try:
            # Check if trying to change flow rates in auto mode
            if self.data['inflowMode'] == 0:  # If in auto mode (0=auto, 1=manual)
                if control == 'outflowRate' or control == 'inflowRate':
                    # Don't allow changing fuel flow rates in auto mode
                    return jsonify({"error": f"Fuel flow rates are automatically controlled in auto mode"}), 400
            
            # Handle different control types
            if control == 'emergencyStop':
                self.modbus_client.write_register(HOLDING_REGISTER_ESTOP, value)
                self.modbus_client.write_coil(COIL_ESTOP, value)
                
            elif control == 'inflowRate':
                self.modbus_client.write_register(HOLDING_REGISTER_IN_RATE, int(value))
                
            elif control == 'outflowRate':
                self.modbus_client.write_register(HOLDING_REGISTER_OUT_RATE, int(value))
                
            elif control == 'pumpSwitch':
                self.modbus_client.write_register(HOLDING_REGISTER_SWITCH, value)
                self.modbus_client.write_coil(COIL_SWITCH, value)
                
            elif control == 'inflowMode':
                self.modbus_client.write_register(HOLDING_REGISTER_AUTO, value)
                self.modbus_client.write_coil(COIL_AUTO, value)
                
            else:
                return jsonify({"error": "Unknown control"}), 400
                
            print(f"Command sent successfully")
            return jsonify({"success": "Command sent"}), 200
            
        except Exception as e:
            print(f"Command error: {e}")
            return jsonify({"error": str(e)}), 500

    def __del__(self):
        """Clean up when done"""
        if self.modbus_client is not None:
            self.modbus_client.close()
            self.modbus_client = None

# Set up the web interface
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tank-monitor-demo-key'

# Connect to the tank system
modbus = ModbusClient(MODBUS_SERVER_IP, MODBUS_SERVER_PORT)

# Web routes
@app.route('/')
def index():
    """Show the main dashboard page"""
    return render_template('index.html')

@app.route('/update', methods=['GET'])
def update():
    """Send current tank data to browser"""
    return jsonify({
        'tankVolume': modbus.data['tankVolume'],
        'inflowRate': modbus.data['inflowRate'],
        'outflowRate': modbus.data['outflowRate'],
        'pumpSwitchStatus': modbus.data['pumpSwitchStatus'],
        'emergencyStopStatus': modbus.data['emergencyStopStatus'],
        'inflowMeterStatus': modbus.data['inflowMeterStatus'],
        'outflowMeterStatus': modbus.data['outflowMeterStatus'],
        'inflowMode': modbus.data['inflowMode'],
        'overflowed': modbus.data['overflowed'],
        'maxVolume': modbus.data['maxVolume']
    })

@app.route('/write', methods=['POST'])
def write():
    """Receive control commands from browser"""
    # Check for valid input
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    control = request.json.get('control')
    if control is None:
        return jsonify({"error": "Missing control parameter"}), 400

    value = request.json.get('value')
    if value is None:
        return jsonify({"error": "Missing value parameter"}), 400
        
    # Pass valid commands to the system
    if control in ['pumpSwitch', 'emergencyStop', 'inflowMode', 'inflowRate', 'outflowRate']:
        try:
            return modbus.write_data(control, value)
        except Exception as e:
            print(f"Error sending command: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid control type"}), 400

# Start the web server when run directly
if __name__ == '__main__':
    app.run(host=FLASK_SERVER_IP, port=FLASK_SERVER_PORT)