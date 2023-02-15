import time
import threading
import os

top_text = " Beam Sec v1.4.1 by George Hotten (and partially Thomas R) |"
middle_text = ""
bottom_text = ""

hasActivated = False

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

        os.system("clear")
        print("")
        print("")
        print(" " + top_text[:16])
        print(" " + middle_text[:16])
        print(" " + bottom_text[:16])
        print("")

        if hasActivated:
            if middle_text == "!! ALARM TRIP !!":
                middle_text = ""
            else:
                middle_text = "!! ALARM TRIP !!"


time.sleep(0.5)
display_thread = threading.Thread(target=update_display)
display_thread.start()

middle_text = "Waiting WiFi..."
time.sleep(2)
middle_text = "WiFi: True 3"
time.sleep(2)

middle_text = "Arming Beam..."
time.sleep(0.5)
middle_text = "Armed."

time.sleep(4)
hasActivated = True
bottom_text = "> takeoff"
time.sleep(2)
bottom_text = "> up 75"
time.sleep(3)
bottom_text = "> speed 100"
time.sleep(0.5)
bottom_text = "> forward 300"
time.sleep(3)
bottom_text = "< ok (forward 300) "
time.sleep(2)
bottom_text = "> back 300"
time.sleep(3)
bottom_text = "> land"
time.sleep(3)
bottom_text = "< ok (land)"
time.sleep(5)
bottom_text = " Resetting in 3 seconds |"
