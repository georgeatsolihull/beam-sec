# Imports
from machine import Pin, I2C, PWM
import time
from ssd1306 import SSD1306_I2C
import network
import threading
import socket

hasActivated = False
enableCommandText = True

# DISPLAY

# Set up I2C and the pins we're using for it
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Short delay to stop I2C falling over
time.sleep(1)

# Define the display and size (128x32)
display = SSD1306_I2C(128, 32, i2c)

top_text = "Beam Sec v1.4 by George Hotten (and partially Thomas R) | "
middle_text = ""
bottom_text = ""

display.fill(0)
display.text(''.join(top_text), 0, 0)
display.text(middle_text, 0, 12)
display.text(bottom_text, 0, 24)
display.show()


def scroll_variable(string):
    if len(string) <= 16:  # Don't scroll if we don't need to!
        return string

    scroll_list = list(string)

    first_char = scroll_list[0]
    scroll_list.pop(0)
    scroll_list.append(first_char)

    return ''.join(scroll_list)


def update_display():
    global top_text
    global middle_text
    global bottom_text

    while True:
        time.sleep(0.2)

        top_text = scroll_variable(top_text)
        middle_text = scroll_variable(middle_text)
        bottom_text = scroll_variable(bottom_text)

        display.fill(0)
        display.text(top_text, 0, 0)
        display.text(middle_text, 0, 12)
        display.text(bottom_text, 0, 24)
        display.show()

        if hasActivated:
            if middle_text == "!! ALARM TRIP !!":
                middle_text = ""
            else:
                middle_text = "!! ALARM TRIP !!"


time.sleep(0.5)
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
    bottom_text = " Restarting in 3 seconds |"
    time.sleep(3)
    machine.reset()
else:
    middle_text = "Arming Beam..."

# Setup link to tello
host = ''
port = 9000
locaddr = (host, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)
sock.bind(locaddr)


def tello_command(c):
    try:
        global bottom_text
        cmd = c
        # log the command received
        print("--> %s" % c)
        if enableCommandText:
            bottom_text = "> " + c
        # send the command to the drone
        c = c.encode()
        sock.sendto(c, tello_address)
        # wait for a response from the drone
        data, server = sock.recvfrom(255)
        data = data.decode().strip()
        # log the response from the drone
        print("<-- %s" % str(data))
        if enableCommandText:
            bottom_text = "< " + str(data) + " (" + str(cmd) + ")"
    except:
        print("<-- internal err %s" % str(data))
        if enableCommandText:
            bottom_text = "< internal err (" + str(cmd) + ")"


# Set the drone into SDK mode
tello_command("command")

middle_text = "Armed."
bottom_text = ""


# Activates the alarm!
def activate():
    global hasActivated
    global bottom_text
    if hasActivated is True:
        return

    hasActivated = True

    buzzer.duty_u16(10000)

    tello_command("takeoff")
    tello_command("up 75")
    tello_command("speed 100")
    tello_command("forward 300")
    time.sleep(2)
    tello_command("back 300")
    tello_command("land")
    time.sleep(5)

    bottom_text = " Resetting in 3 seconds | "

    time.sleep(3)
    machine.reset()


# Waiting for beam break
while True:  # Run forever

    time.sleep(0.1)  # Short delay

    if beam.value() == 0:  # If the beam is broken

        activate()
