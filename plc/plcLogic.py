# Key fuel system parameters
TANK_MAX = 10000      # Maximum fuel capacity in units
RATE_MIN = 500        # Minimum fuel flow rate in units/second

# Register addresses for our fuel system data
HOLDING_REGISTER_LEVEL = 0      # Current fuel level
HOLDING_REGISTER_ESTOP = 1      # Emergency stop button 
HOLDING_REGISTER_SWITCH = 2     # Main power switch
HOLDING_REGISTER_MOTOR = 3      # Fuel system status
HOLDING_REGISTER_IN_SENS = 4    # Fuel inlet sensor
HOLDING_REGISTER_OUT_SENS = 5   # Fuel outlet sensor
HOLDING_REGISTER_IN_RATE = 6    # Fuel inlet flow rate
HOLDING_REGISTER_OUT_RATE = 7   # Fuel outlet flow rate
HOLDING_REGISTER_AUTO = 8       # Mode (0=auto, 1=manual)
HOLDING_REGISTER_SPILL = 9      # Fuel spill detector

# Switch/control addresses
COIL_ESTOP = 0      # Emergency stop button
COIL_SWITCH = 1     # Main power switch
COIL_MOTOR = 2      # Motor/pump
COIL_IN_SENS = 3    # Inlet sensor
COIL_OUT_SENS = 4   # Outlet sensor
COIL_AUTO = 5       # Mode switch (0=auto, 1=manual)
COIL_SPILL = 6      # Spill indicator

# Keep track of the fuel volume between cycles
tankVolume = 0

def plcLogic(discrete_inputs, coils, holding_registers, input_registers):
    """
    Main fuel system control logic - reads sensors, controls the system, and updates the fuel level.
    
    This is like a human operator who:
    1. Checks fuel sensor readings
    2. Makes decisions about the fuel system
    3. Keeps track of the fuel level
    """
    global tankVolume
    
    # Target volume for auto mode (keep fuel about 2/3 full)
    REGISTER_COUNT = 10
    TARGET_VOLUME = int(2/3 * TANK_MAX)

    # Read the current tank state
    hr_values = holding_registers.getValues(1, REGISTER_COUNT)
    level = hr_values[HOLDING_REGISTER_LEVEL]
    estop = hr_values[HOLDING_REGISTER_ESTOP]
    switch = hr_values[HOLDING_REGISTER_SWITCH]
    in_sens = hr_values[HOLDING_REGISTER_IN_SENS]
    out_sens = hr_values[HOLDING_REGISTER_OUT_SENS]
    in_rate = hr_values[HOLDING_REGISTER_IN_RATE]
    out_rate = hr_values[HOLDING_REGISTER_OUT_RATE]
    auto_mode = hr_values[HOLDING_REGISTER_AUTO]
    spill = hr_values[HOLDING_REGISTER_SPILL]
    
    # Read switch positions
    coil_values = coils.getValues(1, 7)
    coil_estop = coil_values[COIL_ESTOP]
    coil_switch = coil_values[COIL_SWITCH]
    coil_auto = coil_values[COIL_AUTO]
    
    # Make sure switches and indicators match
    if estop != coil_estop:
        holding_registers.setValues(HOLDING_REGISTER_ESTOP + 1, [coil_estop])
        estop = coil_estop
    
    if switch != coil_switch:
        holding_registers.setValues(HOLDING_REGISTER_SWITCH + 1, [coil_switch])
        switch = coil_switch
    
    if auto_mode != coil_auto:
        holding_registers.setValues(HOLDING_REGISTER_AUTO + 1, [coil_auto])
        auto_mode = coil_auto
    
    # Decide if the fuel system should be running
    motor = 0  # Start with system off
    
    # Only run if emergency stop is not active and main switch is on
    if switch and not estop:
        motor = in_sens = out_sens = 1  # Turn on fuel system and sensors
        
        if auto_mode == 0:  # Auto mode (0=auto, 1=manual)
            # In auto mode, we control both fuel flow rates to maintain target level
            out_rate = RATE_MIN  # Fixed fuel outflow in auto mode
            spill = 0
            
            if level < TARGET_VOLUME:
                # We're below target, increase fuel inflow based on how empty we are
                in_rate = int(RATE_MIN + (TARGET_VOLUME - level) * 0.1)
                in_rate = min(in_rate, TANK_MAX * 0.5)  # Don't flow fuel too fast
            else:
                # We're at or above target, stop fuel inflow
                in_rate = 0
        # In manual mode, use whatever fuel rates were set by the operator
    else:
        # Emergency stop or main switch off - fuel system stops
        motor = in_sens = out_sens = 0
        in_rate = out_rate = 0
    
    # Update the fuel level based on flow rates
    if motor == 1:  # If fuel system is running
        # Calculate new fuel level: current + (in - out)
        tankVolume = level + (in_rate - out_rate)
        
        # Handle boundary conditions
        if tankVolume < 0:
            tankVolume = 0
        elif tankVolume > TANK_MAX:
            # Fuel tank is overflowing!
            tankVolume = TANK_MAX
            spill = 1
            
            if auto_mode == 0:  # In auto mode, try to recover from fuel spill
                tankVolume = int(TANK_MAX * 0.95)  # Reduce fuel level a bit
        elif tankVolume < TANK_MAX:
            spill = 0  # No fuel spill if below max
    else:
        # Fuel system is off, level stays the same
        tankVolume = level
    
    # Update all our indicators and values
    holding_registers.setValues(HOLDING_REGISTER_MOTOR + 1, [motor])
    coils.setValues(COIL_MOTOR + 1, [motor])
    
    holding_registers.setValues(HOLDING_REGISTER_LEVEL + 1, [tankVolume])
    holding_registers.setValues(HOLDING_REGISTER_IN_SENS + 1, [in_sens])
    holding_registers.setValues(HOLDING_REGISTER_OUT_SENS + 1, [out_sens])
    holding_registers.setValues(HOLDING_REGISTER_IN_RATE + 1, [in_rate])
    holding_registers.setValues(HOLDING_REGISTER_OUT_RATE + 1, [out_rate])
    holding_registers.setValues(HOLDING_REGISTER_SPILL + 1, [spill])
    
    coils.setValues(COIL_IN_SENS + 1, [in_sens])
    coils.setValues(COIL_OUT_SENS + 1, [out_sens])
    coils.setValues(COIL_SPILL + 1, [spill])