# Haybales — Pwny-CTF (script de solve)
import ssd1306
from machine import Pin, SoftI2C, I2C

class PullupButton:
    def __init__(self, pin):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        """
        Maintain a buffer of the last two states
        buffer[0] is the current state
        buffer[1] is the previous state
        """
        self.buffer = [False, False]

    @property
    def value(self):
        """
        Gets current state of button. Pullup means 1 when not pressed and 0 when it is, so we invert it.
        """
        return not self.button.value()

    @property
    def pressed(self):
        """
        Detects a rising press, I.E. the button was not pressed before, but is now
        """
        return self.buffer[0] and not self.buffer[1]

    @property
    def released(self):
        """
        Detects a falling press, I.E. the button was pressed before, but is not now
        """
        return not self.buffer[0] and self.buffer[1]

    def tick(self):
        self.buffer[1] = self.buffer[0]
        self.buffer[0] = self.value

class BadgeIO:
    def __init__(self):
        i2c = SoftI2C(scl=Pin(19), sda=Pin(18), freq=400000)
        self.display = ssd1306.SSD1306_I2C(128, 64, i2c)
        self.up = PullupButton(6)
        self.left = PullupButton(7)
        self.right = PullupButton(4)
        self.down = PullupButton(5)
        self.A = PullupButton(2)
        self.B = PullupButton(3)
        self.TX = Pin(21, Pin.OUT)
        self.RX = Pin(16, Pin.IN)
        self.sao = I2C(0, scl=Pin(13, pull=Pin.PULL_UP), sda=Pin(12, pull=Pin.PULL_UP), freq=400000)

    def tick(self):
        """
        Save the state of all buttons.
        """
        self.up.tick()
        self.left.tick()
        self.right.tick()
        self.down.tick()
        self.A.tick()
        self.B.tick()

# GLOBALLY INITIALIZE BADGE IO
badge = BadgeIO()