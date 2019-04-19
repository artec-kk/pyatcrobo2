class Wire():
    __BUFFER_LENGTH = 32

    def __init__(self, i2c):
        self.__i2c = i2c
        self.rxBuffer = bytearray(Wire.__BUFFER_LENGTH)
        self.rxBufferIndex = 0
        self.rxBufferLength = 0

        self.txAddress = 0
        self.txBuffer = bytearray(Wire.__BUFFER_LENGTH)
        self.txBufferIndex = 0
        self.txBufferLength = 0

        self.transmitting = 0

    def begin(self):
        self.rxBufferIndex = 0
        self.rxBufferLength = 0
        self.txBufferIndex = 0
        self.txBufferLength = 0

    def requestFrom(self, address, quantity):
        # clamp to buffer length
        if(quantity > Wire.__BUFFER_LENGTH):
            quantity = Wire.__BUFFER_LENGTH

        # perform blocking read into buffer
        read = self.__i2c.readfrom(address, quantity)
        for i in range(quantity):
            self.rxBuffer[i] = read[i]

        # set rx buffer iterator vars
        self.rxBufferIndex = 0
        self.rxBufferLength = quantity

        return quantity

    def beginTransmission(self, address):
        # indicate that we are transmitting
        self.transmitting = 1
        # set address of targeted slave
        self.txAddress = address
        # reset tx buffer iterator vars
        self.txBufferIndex = 0
        self.txBufferLength = 0

    def endTransmission(self, sendStop=True):
        # transmit buffer (blocking)
        data = bytearray(self.txBufferLength)
        for i in range(self.txBufferLength):
            data[i] = self.txBuffer[i]
        self.__i2c.writeto(self.txAddress, data, sendStop)
        # reset tx buffer iterator vars
        self.txBufferIndex = 0
        self.txBufferLength = 0
        # indicate that we are done transmitting
        self.transmitting = 0

        return self.txBufferLength

    def write(self, data):
        """
        must be called in:
        slave tx event callback
        or after beginTransmission(address)
        """
        if self.transmitting:
            # in master transmitter mode
            # don't bother if buffer is full
            if (self.txBufferLength >= Wire.__BUFFER_LENGTH):
                raise SystemError('Tx buffer overflow')
            # put byte in tx buffer
            self.txBuffer[self.txBufferIndex] = data
            self.txBufferIndex += 1
            # update amount in buffer
            self.txBufferLength = self.txBufferIndex
        else:
            # in slave send mode
            # reply to master
            # twi_transmit(data, 1)
            pass

        return 1

    def available(self):
        """
        must be called in:
        slave rx event callback
        or after requestFrom(address, numBytes)
        """
        return self.rxBufferLength - self.rxBufferIndex

    def read(self):
        """
        must be called in:
        slave rx event callback
        or after requestFrom(address, numBytes)
        """
        value = -1

        # get each successive byte on each call
        if(self.rxBufferIndex < self.rxBufferLength):
            value = self.rxBuffer[self.rxBufferIndex]
        self.rxBufferIndex += 1

        return value
