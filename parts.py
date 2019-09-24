"""
------------------------------------------------------------------------------
The MIT License (MIT)
Copyright (c) 2016 Newcastle University
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.import time
------------------------------------------------------------------------------
Author
Kenji Kawase, Artec Co., Ltd.
------------------------------------------------------------------------------
"""
from micropython import const
from . import body, wire
from .const import Tone, DCCntrl, ACCConfig, ColorSensorConfig
import time
import ustruct
import machine
import sys


class InputParts():
    def __init__(self, pin):
        if type(pin) is str:
            if pin is 'P0':
                pin = body.p0
            elif pin is 'P1':
                pin = body.p1
            elif pin is 'P2':
                pin = body.p2
            else:
                raise TypeError("This parts can connect only 'P0','P1','P2'")
        else:
            if not isinstance(pin, body.InPin):
                raise TypeError('This parts can connect only p0,p1,p2')
        self._terminalpin = pin.terminalpin


class OutputParts():
    def __init__(self, pin):

        if type(pin) is str:
            if pin is 'P13':
                pin = body.p13
            elif pin is 'P14':
                pin = body.p14
            elif pin is 'P15':
                pin = body.p15
            elif pin is 'P16':
                pin = body.p16
            else:
                raise TypeError("This parts can connect only 'P13','P14','P15','P16'")
        else:
            if not isinstance(pin, body.OutPin):
                raise TypeError('This parts can connect only p13,p14,p15,p16')
        self._terminalpin = pin.terminalpin


class DCMParts():
    def __init__(self, pin):
        if type(pin) is str:
            if pin is 'M1':
                pin = body.m1
            elif pin is 'M2':
                pin = body.m2
            else:
                raise TypeError("This parts can connect only 'M1','M2'")
        else:
            if not isinstance(pin, body.MotorPin):
                raise TypeError('This parts can connect only m1,m2')
        self._i2c = pin._i2c


class I2CParts():
    def __init__(self, pin):
        if type(pin) is str:
            if pin is 'I2C':
                pin = body.i2c
            else:
                raise TypeError("This parts can connect only 'I2C'")
        else:
            if not isinstance(pin, body.I2CPin):
                raise TypeError('This parts can connect only i2c')
        self._i2c = pin._i2c


class DCMotor(DCMParts, DCCntrl):
    __ADDRESS = 0x3e
    __COMMAND = [[0x00, 0x01, 0x02, 0x03, 0x04],
                 [0x08, 0x09, 0x0A, 0x0B, 0x0C]]

    def __init__(self, pin):
        super().__init__(pin)
        if (pin is body.m1) or (pin is 'M1'):
            self.__p = 0
        if (pin is body.m2) or (pin is 'M2'):
            self.__p = 1

        self.__CTRLBUF = bytearray(1)
        self.__POWRBUF = bytearray(2)

    def cw(self):
        self.action(DCMotor.CW)

    def ccw(self):
        self.action(DCMotor.CCW)

    def stop(self):
        self.action(DCMotor.STOP)

    def brake(self):
        self.action(DCMotor.BRAKE)

    def action(self, motion):
        if ((motion != DCMotor.CW) and
           (motion != DCMotor.CCW) and
           (motion != DCMotor.STOP) and
           (motion != DCMotor.BRAKE)):
            raise ValueError('motion: DCMotor.CW/CCW/STOP/BREAK')
        ustruct.pack_into("<b", self.__CTRLBUF, 0,
                          DCMotor.__COMMAND[self.__p][motion])
        self._i2c._i2c.writeto(DCMotor.__ADDRESS, self.__CTRLBUF)

    def power(self, power):
        if (power > 255) or (power < 0):
            raise ValueError('power is in range 0-255')
        ustruct.pack_into("<bb", self.__POWRBUF, 0,
                          DCMotor.__COMMAND[self.__p][4],
                          power)
        self._i2c._i2c.writeto(DCMotor.__ADDRESS, self.__POWRBUF)


class Servomotor(OutputParts):
    __FREQ = 50
    __1DEG = 0.0555556
    __DEG_0 = 2.5
    __PWMTIMER_FIXED_ID = None
    __SVM_USED = [False, False, False, False]

    def __init__(self, pin):
        super().__init__(pin)
        if Servomotor.__PWMTIMER_FIXED_ID is None:
            self.tid = self._terminalpin.get_pwm_timer()
            Servomotor.__PWMTIMER_FIXED_ID = self.tid
        else:
            self.tid = Servomotor.__PWMTIMER_FIXED_ID

        if self._terminalpin.pin == 18:
            self.svm_num = 0
        if self._terminalpin.pin == 19:
            self.svm_num = 1
        if self._terminalpin.pin == 23:
            self.svm_num = 2
        if self._terminalpin.pin == 13:
            self.svm_num = 3

        self._terminalpin.set_analog_hz(Servomotor.__FREQ, self.tid)
        Servomotor.__SVM_USED[self.svm_num] = True

    def set_angle(self, degree):
        self._terminalpin.write_analog(degree * Servomotor.__1DEG + Servomotor.__DEG_0)

    def release(self):
        Servomotor.__SVM_USED[self.svm_num] = False
        self._terminalpin.release_pwm()
        for f in Servomotor.__SVM_USED:
            if f:
                return
        self._terminalpin.rel_pwm_timer(self.tid)
        Servomotor.__PWMTIMER_FIXED_ID = None


class Buzzer(OutputParts, Tone):

    def __init__(self, pin):
        super().__init__(pin)
        self.tid = self._terminalpin.get_pwm_timer()

    def on(self, sound, *, volume=None, duration=None):
        tone = None
        vol = None
        if type(sound) == str:

            if sound.isdigit():
                # MIDI noto number
                nn = int(sound)
                if nn < 48 or nn > 127:
                    raise ValueError("Note number must be '48'-'127'")
                s = Buzzer.NOTE_NUM[nn-48]
            else:
                # Letter notation
                s = sound

            tone = Buzzer.TONE_MAP[s]
            vol = Buzzer.VOLUME_MAP[s]
        elif type(sound) == int:
            if sound < 0:
                raise ValueError("Frequency must be more than 0")
            tone = sound
            vol = 30
        else:
            raise TypeError('sound must be int or string')

        if (volume is not None):
            if (volume >= 0) and (volume <= 99):
                vol = volume
            else:
                raise ValueError('volume must be 0-99')

        self._terminalpin.set_analog_hz(tone, self.tid)
        self._terminalpin.write_analog(vol)

        if duration is not None:
            if duration < 0:
                self.off()
                raise ValueError("duration must be more than 0")
            time.sleep_ms(duration)
            self.off()

    def off(self):
        self._terminalpin.write_analog(0)

    def release(self):
        # print(self._terminalpin.pin)
        self._terminalpin.write_analog(0)
        self._terminalpin.rel_pwm_timer(self.tid)
        self._terminalpin.release_pwm()


Buzzer.TONE_MAP = {
    'C3': 131, 'CS3': 139, 'D3': 147, 'DS3': 156, 'E3': 165, 'F3': 175,
    'FS3': 185, 'G3': 196, 'GS3': 208, 'A3': 220, 'AS3': 233, 'B3': 247,
    'C4': 262, 'CS4': 277, 'D4': 294, 'DS4': 311, 'E4': 330, 'F4': 349,
    'FS4': 370, 'G4': 392, 'GS4': 415, 'A4': 440, 'AS4': 466, 'B4': 494,
    'C5': 523, 'CS5': 554, 'D5': 587, 'DS5': 622, 'E5': 659, 'F5': 699,
    'FS5': 740, 'G5': 784, 'GS5': 831, 'A5': 880, 'AS5': 932, 'B5': 988,
    'C6': 1047, 'CS6': 1109, 'D6': 1175, 'DS6': 1245, 'E6': 1319, 'F6': 1397,
    'FS6': 1480, 'G6': 1568, 'GS6': 1661, 'A6': 1760, 'AS6': 1865, 'B6': 1976,
    'C7': 2093, 'CS7': 2218, 'D7': 2349, 'DS7': 2489, 'E7': 2637, 'F7': 2794,
    'FS7': 2960, 'G7': 3136, 'GS7': 3322, 'A7': 3520, 'AS7': 3729, 'B7': 3951,
    'C8': 4186, 'CS8': 4435, 'D8': 4699, 'DS8': 4978, 'E8': 5274, 'F8': 5588,
    'FS8': 5920, 'G8': 6272, 'GS8': 6645, 'A8': 7040, 'AS8': 7459, 'B8': 7902,
    'C9': 8372, 'CS9': 8870, 'D9': 9397, 'DS9': 9956, 'E9': 10548, 'F9': 11175,
    'FS9': 11840, 'G9': 12544
}


Buzzer.NOTE_NUM = [
    'C3', 'CS3', 'D3', 'DS3', 'E3', 'F3', 'FS3', 'G3', 'GS3', 'A3', 'AS3', 'B3',
    'C4', 'CS4', 'D4', 'DS4', 'E4', 'F4', 'FS4', 'G4', 'GS4', 'A4', 'AS4', 'B4',
    'C5', 'CS5', 'D5', 'DS5', 'E5', 'F5', 'FS5', 'G5', 'GS5', 'A5', 'AS5', 'B5',
    'C6', 'CS6', 'D6', 'DS6', 'E6', 'F6', 'FS6', 'G6', 'GS6', 'A6', 'AS6', 'B6',
    'C7', 'CS7', 'D7', 'DS7', 'E7', 'F7', 'FS7', 'G7', 'GS7', 'A7', 'AS7', 'B7',
    'C8', 'CS8', 'D8', 'DS8', 'E8', 'F8', 'FS8', 'G8', 'GS8', 'A8', 'AS8', 'B8',
    'C9', 'CS9', 'D9', 'DS9', 'E9', 'F9', 'FS9', 'G9'
]


Buzzer.VOLUME_MAP = {
  'C3': 20, 'CS3': 20, 'D3': 20, 'DS3': 20, 'E3': 20, 'F3': 20, 'FS3': 20,
  'G3': 20, 'GS3': 20, 'A3': 20, 'AS3': 20, 'B3': 30,
  'C4': 30, 'CS4': 30, 'D4': 30, 'DS4': 30, 'E4': 30, 'F4': 30, 'FS4': 30,
  'G4': 30, 'GS4': 30, 'A4': 30, 'AS4': 30, 'B4': 40,
  'C5': 40, 'CS5': 40, 'D5': 40, 'DS5': 40, 'E5': 40, 'F5': 40, 'FS5': 40,
  'G5': 40, 'GS5': 40, 'A5': 40, 'AS5': 40, 'B5': 50,
  'C6': 50, 'CS6': 50, 'D6': 50, 'DS6': 50, 'E6': 40, 'F6': 40, 'FS6': 40,
  'G6': 40, 'GS6': 50, 'A6': 50, 'AS6': 50, 'B6': 60,
  'C7': 60, 'CS7': 60, 'D7': 60, 'DS7': 60, 'E7': 10, 'F7': 10, 'FS7': 10,
  'G7': 10, 'GS7': 60, 'A7': 60, 'AS7': 60, 'B7': 70,
  'C8': 70, 'CS8': 70, 'D8': 70, 'DS8': 70, 'E8': 60, 'F8': 60, 'FS8': 70,
  'G8': 60, 'GS8': 60, 'A8': 60, 'AS8': 60, 'B8': 70,
  'C9': 80, 'CS9': 80, 'D9': 80, 'DS9': 80, 'E9': 60, 'F9': 60, 'FS9': 60,
  'G9': 60
}


class LED(OutputParts):
    def __init__(self, pin):
        super().__init__(pin)

    def on(self):
        return self._terminalpin.write_digital(1)

    def off(self):
        return self._terminalpin.write_digital(0)


class IRPhotoReflector(InputParts):
    def __init__(self, pin):
        super().__init__(pin)

    def get_value(self):
        return int(self._terminalpin.read_analog())


class LightSensor(InputParts):
    def __init__(self, pin):
        super().__init__(pin)

    def get_value(self):
        return int(self._terminalpin.read_analog())


class SoundSensor(InputParts):
    def __init__(self, pin):
        super().__init__(pin)

    def get_value(self):
        return int(self._terminalpin.read_analog())


class TouchSensor(InputParts):
    def __init__(self, pin):
        super().__init__(pin)

    def get_value(self):
        return self._terminalpin.read_digital()

    def is_pressed(self):
        """If the button is pressed down, is_pressed() is True, else False.
        """
        if self.get_value() == 1:
            flag = False
        else:
            flag = True
        return flag


class Temperature(InputParts):
    def __init__(self, pin):
        super().__init__(pin)

    def get_value(self):
        return int(self._terminalpin.read_analog())

    def get_celsius(self):
        return (self._terminalpin.read_analog(mv=True) - 500) / 10


class UltrasonicSensor(InputParts):
    def __init__(self, pin):
        if type(pin) is str:
            if not((pin is 'P0') or (pin is 'P1')):
                raise TypeError("This parts can connect only 'P0','P1'")

        super().__init__(pin)
        self._terminalpin.write_digital(0)
        self.echo_timeout_us = 30000

    def get_pulse_time(self):
        self._terminalpin.write_digital(0)
        time.sleep_us(10)
        self._terminalpin.write_digital(1)
        time.sleep_us(20)
        self._terminalpin.write_digital(0)
        time.sleep_us(100)
        try:
            pin = machine.Pin(self._terminalpin.pin, mode=machine.Pin.IN, pull=None)
            pulse_time = machine.time_pulse_us(pin, 1, self.echo_timeout_us)
        except OSError as e:
            if e.arge[0] == 110:
                raise OSError('Out of range')
            raise e
            
        self._terminalpin.write_digital(0)
        return pulse_time

    def get_distance(self):
        pulse_time = self.get_pulse_time()
        range = pulse_time / 58.0   # 29us = 1cm
        range = int(range * 100) / 100.0
        return range


class ColorSensor(I2CParts, ColorSensorConfig):

    def __init__(self, pin):
        super().__init__(pin)
        self.__addr = ColorSensor.I2C_ADDR
        self.__wire = wire.Wire(self._i2c._i2c)
        self._i2c._i2c.init(scl=machine.Pin(22), sda=machine.Pin(21), freq=250000, timeout=0xfffff)
        self.__i2c_send(ColorSensor.GET_COLOR_RGB)
        self.red = 0
        self.green = 0
        self.blue = 0
        self.readingdata = [0,0,0,0]

    def get_values(self, tt=5):
        try_count = 0
        while True:
            if (try_count > tt):
                raise RuntimeError("ColorSensor can't get valid values")
          
            try:
                self.__i2c_send(ColorSensor.GET_COLOR_RGB)
                time.sleep_us(50)
                self.__wire.requestFrom(self.__addr, 4)
            except Exception as e:
                try_count += 1
                continue

            if self.__wire.available():
                for i in range(4):
                    self.readingdata[i] = self.__wire.read()

                
                if self.readingdata == [255,255,255,255]:
                    try_count += 1
                    continue

                self.red = self.readingdata[0]
                self.green = self.readingdata[1]
                self.blue = self.readingdata[2]
            
                return self.readingdata
            else:
                try_count += 1
                continue

    def get_colorcode(self):
        self.get_values()
        self.__clac_xy_code()

        if (self.red <= ColorSensor.LOST_THRESHOLD) and (self.green <= ColorSensor.LOST_THRESHOLD) and \
            (self.blue <= ColorSensor.LOST_THRESHOLD):
            return ColorSensor.COLOR_UNDEF
        if (self.x >= ColorSensor.MIN_X_RED) and (self.x <= ColorSensor.MAX_X_RED) and \
            (self.y >= ColorSensor.MIN_Y_RED) and (self.y <= ColorSensor.MAX_Y_RED):
            return ColorSensor.COLOR_RED
        if (self.x >= ColorSensor.MIN_X_GREEN) and (self.x <= ColorSensor.MAX_X_GREEN) and \
            (self.y >= ColorSensor.MIN_Y_GREEN) and (self.y <= ColorSensor.MAX_Y_GREEN):
            return ColorSensor.COLOR_GREEN
        if (self.x >= ColorSensor.MIN_X_BLUE) and (self.x <= ColorSensor.MAX_X_BLUE) and \
            (self.y >= ColorSensor.MIN_Y_BLUE) and (self.y <= ColorSensor.MAX_Y_BLUE):
            return ColorSensor.COLOR_BLUE
        if (self.x >= ColorSensor.MIN_X_WHITE) and (self.x <= ColorSensor.MAX_X_WHITE) and \
            (self.y >= ColorSensor.MIN_Y_WHITE) and (self.y <= ColorSensor.MAX_Y_WHITE):
            return ColorSensor.COLOR_WHITE
        if (self.x >= ColorSensor.MIN_X_YELLOW) and (self.x <= ColorSensor.MAX_X_YELLOW) and \
            (self.y >= ColorSensor.MIN_Y_YELLOW) and (self.y <= ColorSensor.MAX_Y_YELLOW):
            return ColorSensor.COLOR_YELLOW
        if (self.x >= ColorSensor.MIN_X_ORANGE) and (self.x <= ColorSensor.MAX_X_ORANGE) and \
            (self.y >= ColorSensor.MIN_Y_ORANGE) and (self.y <= ColorSensor.MAX_Y_ORANGE):
            return ColorSensor.COLOR_ORANGE
        if (self.x >= ColorSensor.MIN_X_PURPLE) and (self.x <= ColorSensor.MAX_X_PURPLE) and \
            (self.y >= ColorSensor.MIN_Y_PURPLE) and (self.y <= ColorSensor.MAX_Y_PURPLE):
            return ColorSensor.COLOR_PURPLE
            
        return ColorSensor.COLOR_UNDEF

    def __clac_xy_code(self):
        X = (0.576669) * self.red + (0.185558) * self.green + (0.188229) * self.blue
        Y = (0.297345) * self.red + (0.627364) * self.green + (0.075291) * self.blue
        Z = (0.027031) * self.red + (0.070689) * self.green + (0.991338) * self.blue
        self.x = X / (X + Y + Z)
        self.y = Y / (X + Y + Z)

    def __i2c_send(self, command):
        # Set to status reg
        self.__wire.beginTransmission(self.__addr)
        self.__wire.write(command)
        self.__wire.endTransmission()


__MMA_8653_ADDRESS = const(0x1d)

__MMA_8653_CTRL_REG1 = const(0x2A)
__MMA_8653_CTRL_REG1_VALUE_ACTIVE = const(0x01)
__MMA_8653_CTRL_REG1_VALUE_F_READ = const(0x02)

__MMA_8653_CTRL_REG2 = const(0x2B)
__MMA_8653_CTRL_REG2_RESET = const(0x40)

__MMA_8653_PL_STATUS = const(0x10)
__MMA_8653_PL_CFG = const(0x11)
__MMA_8653_PL_EN = const(0x40)

__MMA_8653_XYZ_DATA_CFG = const(0x0E)
__MMA_8653_2G_MODE = const(0x00)   # Set Sensitivity to 2g
__MMA_8653_4G_MODE = const(0x01)   # Set Sensitivity to 4g
__MMA_8653_8G_MODE = const(0x02)   # Set Sensitivity to 8g

__MMA_8653_FF_MT_CFG = const(0x15)
__MMA_8653_FF_MT_CFG_ELE = const(0x80)
__MMA_8653_FF_MT_CFG_OAE = const(0x40)

__MMA_8653_FF_MT_SRC = const(0x16)
__MMA_8653_FF_MT_SRC_EA = const(0x80)

__MMA_8653_PULSE_CFG = const(0x21)
__MMA_8653_PULSE_CFG_ELE = const(0x80)

__MMA_8653_PULSE_SRC = const(0x22)
__MMA_8653_PULSE_SRC_EA = const(0x80)

# Sample rate
__MMA_8653_ODR_800 = const(0x00)
__MMA_8653_ODR_400 = const(0x08)
__MMA_8653_ODR_200 = const(0x10)
__MMA_8653_ODR_100 = const(0x18)   # default ratio 100 samples per second
__MMA_8653_ODR_50 = const(0x20)
__MMA_8653_ODR_12_5 = const(0x28)
__MMA_8653_ODR_6_25 = const(0x30)
__MMA_8653_ODR_1_56 = const(0x38)


def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)


class Accelerometer(I2CParts, ACCConfig):

    def __init__(self, pin):
        super().__init__(pin)
        self.__wire = wire.Wire(self._i2c._i2c)
        self._begin(False, 2)

    def _whoami(self):
        pass

    def _read_register(self, offset):
        self.__wire.beginTransmission(__MMA_8653_ADDRESS)
        self.__wire.write(offset)
        self.__wire.endTransmission(False)

        self.__wire.requestFrom(__MMA_8653_ADDRESS, 1)

        if (self.__wire.available()):
            return self.__wire.read()
        return 0

    def _standby(self):
        reg1 = 0x00
        _addr = __MMA_8653_ADDRESS

        self.__wire.beginTransmission(_addr)    # Set to status reg
        self.__wire.write(__MMA_8653_CTRL_REG1)
        self.__wire.endTransmission()

        self.__wire.requestFrom(_addr, 1)
        if (self.__wire.available()):
            reg1 = self.__wire.read()

        self.__wire.beginTransmission(_addr)    # Reset
        self.__wire.write(__MMA_8653_CTRL_REG1)
        self.__wire.write(reg1 & ~__MMA_8653_CTRL_REG1_VALUE_ACTIVE)
        self.__wire.endTransmission()

    def _active(self):
        reg1 = 0x00
        _addr = __MMA_8653_ADDRESS

        self.__wire.beginTransmission(_addr)    # Set to status reg
        self.__wire.write(__MMA_8653_CTRL_REG1)
        self.__wire.endTransmission()

        self.__wire.requestFrom(_addr, 1)
        if (self.__wire.available()):
            reg1 = self.__wire.read()

        self.__wire.beginTransmission(_addr)    # Reset
        self.__wire.write(__MMA_8653_CTRL_REG1)
        if self._highres:
            f_read = 0
        else:
            f_read = __MMA_8653_CTRL_REG1_VALUE_F_READ
        self.__wire.write(reg1 | __MMA_8653_CTRL_REG1_VALUE_ACTIVE | f_read | __MMA_8653_ODR_100)
        self.__wire.endTransmission()

    def _begin(self, highres, scale):
        _addr = __MMA_8653_ADDRESS
        self._highres = highres
        # Base value at 2g setting
        if self._highres:
            self._step_factor = 0.0039
        else:
            self._step_factor = 0.0156

        if (scale == 4):
            self._step_factor *= 2
        elif (scale == 8):
            self._step_factor *= 4
        self.wai = self._read_register(0x0D)    # Get Who Am I from the device.

        self.__wire.beginTransmission(_addr)    # Reset
        self.__wire.write(__MMA_8653_CTRL_REG2)
        self.__wire.write(__MMA_8653_CTRL_REG2_RESET)
        self.__wire.endTransmission()
        time.sleep_ms(10)   # Give it time to do the reset

        self._standby()

        # Set Portrait/Landscape mode
        self.__wire.beginTransmission(_addr)
        self.__wire.write(__MMA_8653_PL_CFG)
        self.__wire.write(0x80 | __MMA_8653_PL_EN)
        self.__wire.endTransmission()

        self.__wire.beginTransmission(_addr)
        self.__wire.write(__MMA_8653_XYZ_DATA_CFG)
        if (scale == 4):
            self.__wire.write(__MMA_8653_4G_MODE)
        elif (scale == 8):
            self.__wire.write(__MMA_8653_8G_MODE)
        else:   # Default to 2g mode
            self.__wire.write(__MMA_8653_2G_MODE)
        self.__wire.endTransmission()
        self._active()

    def configuration(self, highres, scale):

        if type(scale) is int:
            if not (scale == 2 or scale == 4 or scale == 8):
                raise ValueError("scall param is 2, 4, or 8")
        else:
            raise TypeError("scall param is 2, 4, or 8")
            
        if type(highres) is not bool:
            raise TypeError('higres param is True / False')

        self._begin(highres, scale)

    def get_x(self):
        return self.get_values()[0]

    def get_y(self):
        return self.get_values()[1]

    def get_z(self):
        return self.get_values()[2]

    def get_values(self):
        self._update()
        return self._xg, self._yg, self._zg

    def _update(self):
        _addr = __MMA_8653_ADDRESS
        self.__wire.beginTransmission(_addr)    # Set to status reg
        self.__wire.write(0x00)
        self.__wire.endTransmission(False)

        if self._highres:
            q = 7
        else:
            q = 4
        self.__wire.requestFrom(_addr, q)
        if self.__wire.available():
            _stat = self.__wire.read()
            if(self._highres):
                # rx = (int16_t)((Wire.read() << 8) + Wire.read());
                self._x = s16((self.__wire.read() << 8) + self.__wire.read())
                self._xg = (self._x / 64) * self._step_factor
                # ry = (int16_t)((Wire.read() << 8) + Wire.read());
                self._y = s16((self.__wire.read() << 8) + self.__wire.read())
                self._yg = (self._y / 64) * self._step_factor
                # rz = (int16_t)((Wire.read() << 8) + Wire.read());
                self._z = s16((self.__wire.read() << 8) + self.__wire.read())
                self._zg = (self._z / 64) * self._step_factor
            else:
                """
                _xg = (int8_t)Wire.read() * _step_factor;
                _yg = (int8_t)Wire.read() * _step_factor;
                _zg = (int8_t)Wire.read() * _step_factor;
                _x = 0;
                _y = 0;
                _z = 0;
                """
                self._x = s16(self.__wire.read() << 8)
                self._x = self._x / 256
                self._y = s16(self.__wire.read() << 8)
                self._y = self._y / 256
                self._z = s16(self.__wire.read() << 8)
                self._z = self._z / 256
                self._xg = self._x * self._step_factor
                self._yg = self._y * self._step_factor
                self._zg = self._z * self._step_factor

# class Gyro(I2CParts):
#  def __init__(self, connector):
#    raise NotImplementedError
