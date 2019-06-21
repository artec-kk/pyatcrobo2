class ColorSensorConfig:
    I2C_ADDR = 0x36
    GET_COLOR_RGB = 0x63
    LED_ENABLE_R = 0x52
    LED_ENABLE_G = 0x47
    LED_ENABLE_B = 0x42
    LED_DISABLE = 0x44

    # Color code
    COLOR_UNDEF = 0
    COLOR_RED = 1
    COLOR_GREEN = 2
    COLOR_BLUE = 3
    COLOR_WHITE = 4
    COLOR_YELLOW = 5
    COLOR_ORANGE = 6
    COLOR_PURPLE = 7

    # for Artec Block

    LOST_THRESHOLD = 25  #  8bit
    MIN_X_RED    = 0.37
    MAX_X_RED    = 0.48
    MIN_Y_RED    = 0.28
    MAX_Y_RED    = 0.36
    MIN_X_GREEN  = 0.23
    MAX_X_GREEN  = 0.33
    MIN_Y_GREEN  = 0.35
    MAX_Y_GREEN  = 0.46
    MIN_X_BLUE   = 0.20
    MAX_X_BLUE   = 0.31
    MIN_Y_BLUE   = 0.20
    MAX_Y_BLUE   = 0.28
    MIN_X_WHITE  = 0.30
    MAX_X_WHITE  = 0.37

    MIN_Y_WHITE  = 0.30
    MAX_Y_WHITE  = 0.35
    MIN_X_YELLOW = 0.34
    MAX_X_YELLOW = 0.47
    MIN_Y_YELLOW = 0.36
    MAX_Y_YELLOW = 0.45
    MIN_X_ORANGE = 0.44
    MAX_X_ORANGE = 0.55
    MIN_Y_ORANGE = 0.33
    MAX_Y_ORANGE = 0.38
    MIN_X_PURPLE = 0.22
    MAX_X_PURPLE = 0.31
    MIN_Y_PURPLE = 0.28
    MAX_Y_PURPLE = 0.32
  

class ACCConfig:
    G_2 = 2
    G_4 = 4
    G_8 = 8
    HIGH_RESOLUTION = True
    LOW_RESOLUTION = False


class DCCntrl:
    CW = 0
    CCW = 1
    STOP = 2
    BRAKE = 3


class Tone:
    C3 = 130
    CS3 = 139
    D3 = 147
    DS3 = 156
    E3 = 165
    F3 = 175
    FS3 = 185
    G3 = 196
    GS3 = 208
    A3 = 220
    AS3 = 233
    B3 = 247
    C4 = 262
    CS4 = 277
    D4 = 294
    DS4 = 311
    E4 = 330
    F4 = 349
    FS4 = 370
    G4 = 392
    GS4 = 415
    A4 = 440
    AS4 = 466
    B4 = 494
    C5 = 523
    CS5 = 554
    D5 = 587
    DS5 = 622
    E5 = 659
    F5 = 698
    FS5 = 740
    G5 = 784
    GS5 = 831
    A5 = 880
    AS5 = 932
    B5 = 988
    C6 = 1047
    CS6 = 1109
    D6 = 1175
    DS6 = 1245
    E6 = 1319
    F6 = 1397
    FS6 = 1480
    G6 = 1568
    GS6 = 1661
    A6 = 1760
    AS6 = 1865
    B6 = 1976
    C7 = 2093
    CS7 = 2217
    D7 = 2349
    DS7 = 2489
    E7 = 2637
    F7 = 2794
    FS7 = 2960
    G7 = 3136
    GS7 = 3322
    A7 = 3520
    AS7 = 3729
    B7 = 3951
    C8 = 4186
    

