"""
Aloha Water Treatment Plant HMI
Flask web application for monitoring and controlling the water treatment plant simulation.
"""

import threading
import time

from flask import Flask, render_template, request, jsonify
from pymodbus.client import ModbusTcpClient

flaskServerIp = "0.0.0.0"
flaskServerPort = 8090
modbusServerIp = "0.0.0.0"
modbusServerPort = 502
registerCount = 10
tankMax = 10000

coilBase = 0
coilEstop = 0
coilSwitch = 1
coilPump = 2
coilInValve = 3
coilOutValve = 4
coilAuto = 5
coilAlarm = 6
coilLowLevelAlarm = 7
coilOperatorErrorAlarm = 8

holdingRegisterBase = 0
holdingRegisterLevel = 0
holdingRegisterEstop = 1
holdingRegisterSwitch = 2
holdingRegisterPump = 3
holdingRegisterInValve = 4
holdingRegisterOutValve = 5
holdingRegisterInFlow = 6
holdingRegisterOutFlow = 7
holdingRegisterAuto = 8
holdingRegisterAlarm = 9

class ModbusClient:
    def __init__(self, serverIp, serverPort):
        self.modbusClient = ModbusTcpClient(host=serverIp, port=serverPort, auto_open=True, debug=False)
        self.modbusClient.connect()
        
        self.thread = threading.Thread(target=self.readData, daemon=True)
        self.thread.start()

        self.data = {
            'emergencyStopStatus': None,
            'pumpSwitchStatus': None,
            'pumpStatus': None,
            'inflowValveStatus': None,
            'outflowValveStatus': None,
            'overflowed': None,
            'inflowMode': None,
            'tankVolume': None,
            'maxVolume': tankMax,
            'inflowRate': None,
            'outflowRate': None,
            'lowLevelAlarm': None,
            'operatorErrorAlarm': None
        }

    def readData(self):
        while True:
            try:
                coilResponse = self.modbusClient.read_coils(coilBase, 10)
                if not coilResponse.isError():
                    coilValues = coilResponse.bits
                    self.data['emergencyStopStatus'] = int(coilValues[coilEstop]) if coilValues[coilEstop] is not None else None
                    self.data['pumpSwitchStatus'] = int(coilValues[coilSwitch]) if coilValues[coilSwitch] is not None else None
                    self.data['pumpStatus'] = int(coilValues[coilPump]) if coilValues[coilPump] is not None else None
                    self.data['inflowValveStatus'] = int(coilValues[coilInValve]) if coilValues[coilInValve] is not None else None
                    self.data['outflowValveStatus'] = int(coilValues[coilOutValve]) if coilValues[coilOutValve] is not None else None
                    self.data['overflowed'] = int(coilValues[coilAlarm]) if coilValues[coilAlarm] is not None else None
                    self.data['inflowMode'] = int(coilValues[coilAuto]) if coilValues[coilAuto] is not None else None
                    self.data['lowLevelAlarm'] = int(coilValues[coilLowLevelAlarm]) if coilValues[coilLowLevelAlarm] is not None else None
                    self.data['operatorErrorAlarm'] = int(coilValues[coilOperatorErrorAlarm]) if coilValues[coilOperatorErrorAlarm] is not None else None
            except Exception as e:
                print(f"Error reading coils: {e}")

            try:
                hrResponse = self.modbusClient.read_holding_registers(holdingRegisterBase, registerCount)
                if not hrResponse.isError():
                    hrValues = hrResponse.registers
                    self.data['tankVolume'] = hrValues[holdingRegisterLevel]
                    self.data['emergencyStopStatus'] = hrValues[holdingRegisterEstop]
                    self.data['pumpSwitchStatus'] = hrValues[holdingRegisterSwitch]
                    self.data['pumpStatus'] = hrValues[holdingRegisterPump]
                    self.data['inflowValveStatus'] = hrValues[holdingRegisterInValve]
                    self.data['outflowValveStatus'] = hrValues[holdingRegisterOutValve]
                    self.data['inflowRate'] = hrValues[holdingRegisterInFlow]
                    self.data['outflowRate'] = hrValues[holdingRegisterOutFlow]
                    self.data['inflowMode'] = hrValues[holdingRegisterAuto]
                    self.data['overflowed'] = hrValues[holdingRegisterAlarm]
            except Exception as e:
                print(f"Error reading holding registers: {e}")
                
            time.sleep(1)

    def writeData(self, control, value):
        print(f"Sending command: {control}={value}")
        try:
            if self.data['inflowMode'] == 0:
                if control == 'outflowRate' or control == 'inflowRate':
                    return jsonify({"error": f"Water flow rates are automatically controlled in auto mode"}), 400
            
            if control == 'emergencyStop':
                self.modbusClient.write_register(holdingRegisterEstop, value)
                self.modbusClient.write_coil(coilEstop, value)
                
            elif control == 'inflowRate':
                self.modbusClient.write_register(holdingRegisterInFlow, int(value))
                
            elif control == 'outflowRate':
                self.modbusClient.write_register(holdingRegisterOutFlow, int(value))
                
            elif control == 'pumpSwitch':
                self.modbusClient.write_register(holdingRegisterSwitch, value)
                self.modbusClient.write_coil(coilSwitch, value)
                
            elif control == 'inflowMode':
                self.modbusClient.write_register(holdingRegisterAuto, value)
                self.modbusClient.write_coil(coilAuto, value)
                
            else:
                return jsonify({"error": "Unknown control"}), 400
                
            print(f"Command sent successfully")
            return jsonify({"success": "Command sent"}), 200
            
        except Exception as e:
            print(f"Command error: {e}")
            return jsonify({"error": str(e)}), 500

    def __del__(self):
        if self.modbusClient is not None:
            self.modbusClient.close()
            self.modbusClient = None


app = Flask(__name__)
app.config['SECRET_KEY'] = 'water-treatment-demo-key'

modbus = ModbusClient(modbusServerIp, modbusServerPort)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update', methods=['GET'])
def update():
    return jsonify({
        'tankVolume': modbus.data['tankVolume'],
        'inflowRate': modbus.data['inflowRate'],
        'outflowRate': modbus.data['outflowRate'],
        'pumpSwitchStatus': modbus.data['pumpSwitchStatus'],
        'emergencyStopStatus': modbus.data['emergencyStopStatus'],
        'inflowValveStatus': modbus.data['inflowValveStatus'],
        'outflowValveStatus': modbus.data['outflowValveStatus'],
        'inflowMode': modbus.data['inflowMode'],
        'overflowed': modbus.data['overflowed'],
        'maxVolume': modbus.data['maxVolume'],
        'lowLevelAlarm': modbus.data['lowLevelAlarm'],
        'operatorErrorAlarm': modbus.data['operatorErrorAlarm'],
        'pumpStatus': modbus.data['pumpStatus']
    })


@app.route('/write', methods=['POST'])
def write():
    if not request.is_json:
        return jsonify({"error": "Expected JSON data"}), 400

    control = request.json.get('control')
    if control is None:
        return jsonify({"error": "Missing control parameter"}), 400

    value = request.json.get('value')
    if value is None:
        return jsonify({"error": "Missing value parameter"}), 400
        
    if control in ['pumpSwitch', 'emergencyStop', 'inflowMode', 'inflowRate', 'outflowRate']:
        try:
            return modbus.writeData(control, value)
        except Exception as e:
            print(f"Error sending command: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid control type"}), 400


if __name__ == '__main__':
    app.run(host=flaskServerIp, port=flaskServerPort)