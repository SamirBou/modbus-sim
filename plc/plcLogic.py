"""
Aloha Water Treatment Plant PLC Control Logic
Water treatment system control algorithms for automatic and manual modes.
"""

tankMax = 10000
rateMin = 50

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

coilEstop = 0
coilSwitch = 1
coilPump = 2
coilInValve = 3
coilOutValve = 4
coilAuto = 5
coilAlarm = 6
coilLowLevelAlarm = 7
coilOperatorErrorAlarm = 8

tankVolume = 0


def plcLogic(discreteInputs, coils, holdingRegisters, inputRegisters):
    global tankVolume
    
    registerCount = 10
    targetVolume = int(2/3 * tankMax)

    hrValues = holdingRegisters.getValues(1, registerCount)
    level = hrValues[holdingRegisterLevel]
    estop = hrValues[holdingRegisterEstop]
    switch = hrValues[holdingRegisterSwitch]
    inValve = hrValues[holdingRegisterInValve]
    outValve = hrValues[holdingRegisterOutValve]
    inFlow = hrValues[holdingRegisterInFlow]
    outFlow = hrValues[holdingRegisterOutFlow]
    autoMode = hrValues[holdingRegisterAuto]
    alarm = hrValues[holdingRegisterAlarm]
    
    coilValues = coils.getValues(1, 10)
    coilEstopValue = coilValues[coilEstop]
    coilSwitchValue = coilValues[coilSwitch]
    coilAutoValue = coilValues[coilAuto]
    
    if estop != coilEstopValue:
        holdingRegisters.setValues(holdingRegisterEstop + 1, [coilEstopValue])
        estop = coilEstopValue
    
    if switch != coilSwitchValue:
        holdingRegisters.setValues(holdingRegisterSwitch + 1, [coilSwitchValue])
        switch = coilSwitchValue
    
    if autoMode != coilAutoValue:
        holdingRegisters.setValues(holdingRegisterAuto + 1, [coilAutoValue])
        autoMode = coilAutoValue
    
    pump = 0
    
    if switch and not estop:
        pump = inValve = outValve = 1
        
        if autoMode == 0:
            outFlow = rateMin
            
            if level <= 1000 and outFlow > 0:
                outFlow = 0
                outValve = 0
            
            if level < targetVolume:
                deficit = targetVolume - level
                if deficit > 3000:
                    inFlow = rateMin + 80
                elif deficit > 1500:
                    inFlow = rateMin + 40
                elif deficit > 500:
                    inFlow = rateMin + 20
                else:
                    inFlow = rateMin
            else:
                if level > targetVolume + 500:
                    inFlow = 0
                else:
                    inFlow = rateMin
        else:
            pass
    else:
        pump = inValve = outValve = 0
        inFlow = outFlow = 0
    
    if pump == 1:
        tankVolume = level + (inFlow - outFlow)
        
        if tankVolume < 0:
            tankVolume = 0
        elif tankVolume > tankMax:
            alarm = 1
            
            if autoMode == 0:
                tankVolume = tankMax
                inFlow = 0
                holdingRegisters.setValues(holdingRegisterInFlow + 1, [0])
            else:
                tankVolume = tankMax
        elif tankVolume < tankMax:
            alarm = 0
    else:
        tankVolume = level
    
    holdingRegisters.setValues(holdingRegisterPump + 1, [pump])
    coils.setValues(coilPump + 1, [pump])
    
    holdingRegisters.setValues(holdingRegisterLevel + 1, [tankVolume])
    holdingRegisters.setValues(holdingRegisterInValve + 1, [inValve])
    holdingRegisters.setValues(holdingRegisterOutValve + 1, [outValve])
    holdingRegisters.setValues(holdingRegisterInFlow + 1, [inFlow])
    holdingRegisters.setValues(holdingRegisterOutFlow + 1, [outFlow])
    holdingRegisters.setValues(holdingRegisterAlarm + 1, [alarm])
    
    coils.setValues(coilInValve + 1, [inValve])
    coils.setValues(coilOutValve + 1, [outValve])
    coils.setValues(coilAlarm + 1, [alarm])
    
    lowLevelAlarm = 1 if (tankVolume <= 1000 and outFlow > 0) else 0
    coils.setValues(coilLowLevelAlarm + 1, [lowLevelAlarm])
    
    operatorErrorAlarm = 0
    if autoMode == 1:
        requestedInFlow = hrValues[holdingRegisterInFlow]
        requestedOutFlow = hrValues[holdingRegisterOutFlow]
        
        if tankVolume <= 1000 and requestedOutFlow > 0:
            operatorErrorAlarm = 1
        elif tankVolume >= 9000 and requestedInFlow > 0:
            operatorErrorAlarm = 1
    
    coils.setValues(coilOperatorErrorAlarm + 1, [operatorErrorAlarm])