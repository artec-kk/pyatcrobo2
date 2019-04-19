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
from pystubit.terminal import StuduinoBitTerminal 
from pystubit.bus import StuduinoBitI2C


class InPin():
    def __init__(self, tp):
        self._teraminalpin = tp

    @property
    def terminalpin(self):
        return self._teraminalpin


class OutPin():
    def __init__(self, tp):
        self._teraminalpin = tp

    @property
    def terminalpin(self):
        return self._teraminalpin


class MotorPin():
    def __init__(self, pin):
        self._i2c = pin


class I2CPin():
    def __init__(self, pin):
        self._i2c = pin

p0 = InPin(StuduinoBitTerminal('P0'))
p1 = InPin(StuduinoBitTerminal('P1'))
p2 = InPin(StuduinoBitTerminal('P2'))
p13 = OutPin(StuduinoBitTerminal('P13'))
p14 = OutPin(StuduinoBitTerminal('P14'))
p15 = OutPin(StuduinoBitTerminal('P15'))
p16 = OutPin(StuduinoBitTerminal('P16'))
m1 = MotorPin(StuduinoBitI2C())
m2 = MotorPin(StuduinoBitI2C())
i2c = I2CPin(StuduinoBitI2C())
