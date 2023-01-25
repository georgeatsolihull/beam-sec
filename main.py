# Imports
from machine import Pin, I2C, PWM
import time
from ssd1306 import SSD1306_I2C
import network
import threading
import socket
import sys

# DISPLAY

# Set up I2C and the pins we're using for it
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Short delay to stop I2C falling over
time.sleep(1)

# Define the display and size (128x32)
display = SSD1306_I2C(128, 32, i2c)

top_text = list("Beam Sec v1.2 by George Hotten (and partially Thomas) | ")  # if updated, must be a list
middle_text = ""
bottom_text = ""

display.fill(0)
display.text(''.join(top_text), 0, 0)
display.text(middle_text, 0, 12)
display.text(bottom_text, 0, 24)
display.show()


def update_display():
    global top_text

    global middle_text
    global bottom_text

    while True:
        time.sleep(0.2)

        first_char = top_text[0]
        top_text.pop(0)
        top_text.append(first_char)

        display.fill(0)
        display.text(''.join(top_text), 0, 0)
        display.text(middle_text, 0, 12)
        display.text(bottom_text, 0, 24)
        display.show()

        if hasActivated:
            if middle_text == "!! ALARM TRIP !!":
                middle_text = ""
            else:
                middle_text = "!! ALARM TRIP !!"


display_thread = threading.Thread(target=update_display)
display_thread.start()

# BEAM
beam = Pin(26, Pin.IN, Pin.PULL_DOWN)

# BUZZER
buzzer = PWM(Pin(5))  # Set the buzzer to PWM mode

# Set PWM frequency to 1000
buzzer.freq(1000)

# WIFI

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('TELLO-9F698D', '')

while not wlan.isconnected() and wlan.status() >= 0:
    middle_text = "Waiting WiFi..."
    time.sleep(1)

middle_text = "WiFi: " + str(wlan.isconnected()) + " " + str(wlan.status())

time.sleep(2)
if not wlan.isconnected():
    bottom_text = "Restarting in 3"
    time.sleep(3)
    machine.reset()
else:
    bottom_text = "Arming Beam..."

# Setup link to tello
host = ''
port = 9000
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(locaddr)


def tello_command(c):
    global bottom_text
    cmd = c
    # log the command recieved
    print("--> %s" % c)
    bottom_text = "> " + c
    # send the command to the drone
    c = c.encode()
    sock.sendto(c, tello_address)
    # wait for a response from the drone
    data, server = sock.recvfrom(255)
    data = data.decode().strip()
    # log the response from the drone
    bottom_text = "< " + str(data) + " (" + str(cmd) + ")"
    print("<-- %s" % str(data))


# Set the drone into SDK mode
tello_command("command")

middle_text = "Armed."
bottom_text = ""

# Activates the alarm!
hasActivated = False


def activate():
    global hasActivated
    if hasActivated is True:
        return

    hasActivated = True

    buzzer.duty_u16(10000)

    tello_command("takeoff")
    tello_command("up 75")
    tello_command("speed 100")
    tello_command("flip f")
    tello_command("forward 300")
    tello_command("land")
    print("hi")


# Waiting for beam break
while True:  # Run forever

    time.sleep(0.1)  # Short delay

    if beam.value() == 0:  # If the beam is broken

        activate()
