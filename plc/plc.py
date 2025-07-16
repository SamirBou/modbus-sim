#!/usr/bin/env python3
"""
Aloha Water Treatment Plant PLC Simulation
Modbus TCP server simulating a water treatment plant control system.
"""

import os
import signal
import sys
import time
from multiprocessing import Process
from threading import Thread, Event

from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from plcLogic import plcLogic

modbusHost = "0.0.0.0"
modbusPort = 502
modbusRegisterCount = 15
tankMax = 10000
rateMin = 50
treatmentCapacity = 8000

initLevel = 0
initEstop = 0
initSwitch = 0
initPump = 0
initInValve = 0
initOutValve = 0
initInFlow = 0
initOutFlow = 0
initAuto = 0
initAlarm = 0

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

isActive = True
serverStarted = Event()


def setupModbusServer():
    holdingRegisterValues = [
        initLevel, initEstop, initSwitch, initPump,
        initInValve, initOutValve, initInFlow, 
        initOutFlow, initAuto, initAlarm
    ]
    
    coilValues = [
        initEstop, initSwitch, initPump,
        initInValve, initOutValve, initAuto, initAlarm,
        0, 0
    ]
    
    holdingRegisters = ModbusSequentialDataBlock(
        0x00, 
        [0] + holdingRegisterValues + [0] * (modbusRegisterCount - len(holdingRegisterValues))
    )
    
    coils = ModbusSequentialDataBlock(
        0x00, 
        [0] + coilValues + [0] * (modbusRegisterCount - len(coilValues))
    )
    
    inputRegisters = ModbusSequentialDataBlock(0x00, [0] * modbusRegisterCount)
    discreteInputs = ModbusSequentialDataBlock(0x00, [0] * modbusRegisterCount)

    device = ModbusDeviceIdentification()
    device.VendorName = "Aloha Water Treatment"
    device.ProductCode = "AWT-3000"
    device.VendorUrl = "https://alohawater.com"
    device.ProductName = "WaterMaster Pro"
    device.ModelName = "Series 3000"
    device.MajorMinorRevision = "2.1.5"

    modbusStore = ModbusSlaveContext(
        di=discreteInputs,
        co=coils,
        hr=holdingRegisters,
        ir=inputRegisters
    )

    modbusContext = ModbusServerContext(slaves=modbusStore, single=True)
    
    return modbusContext, device, discreteInputs, coils, holdingRegisters, inputRegisters


def handleSignal(sig, frame):
    global isActive
    print("\nShutting down water treatment system simulation...")
    isActive = False
    sys.exit(0)


def runModbusServer():
    global isActive
    
    signal.signal(signal.SIGINT, handleSignal)
    signal.signal(signal.SIGTERM, handleSignal)
    
    modbusContext, device, discreteInputs, coils, holdingRegisters, inputRegisters = setupModbusServer()

    serverThread = Thread(
        target=StartTcpServer,
        kwargs={
            'context': modbusContext,
            'identity': device,
            'address': (modbusHost, modbusPort),
        },
        daemon=True
    )
    serverThread.start()
    
    time.sleep(1)
    
    serverStarted.set()
    print("Water treatment system simulation running on port", modbusPort)
    
    try:
        while isActive:
            try:
                discreteInputs.setValues(0, discreteInputs.getValues(0, modbusRegisterCount + 1))
                coils.setValues(0, coils.getValues(0, modbusRegisterCount + 1))
                holdingRegisters.setValues(0, holdingRegisters.getValues(0, modbusRegisterCount + 1))
                inputRegisters.setValues(0, inputRegisters.getValues(0, modbusRegisterCount + 1))

                plcLogic(discreteInputs, coils, holdingRegisters, inputRegisters)
            except Exception as e:
                print(f"System error: {e}")
                
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping simulation...")
    except Exception as e:
        print(f"Critical system failure: {e}")


def main():
    runModbusServer()


if __name__ == "__main__":
    main()
