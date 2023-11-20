#!/usr/bin/env python3

from urllib.request import urlopen
from inky.auto import auto
from datetime import datetime
from CONFIG import APP_ID, APP_KEY, BUS_CODE, FLIP
from time import sleep
from math import ceil, floor
from PIL import Image, ImageDraw, ImageFont
from os import system
import RPi.GPIO as GPIO
import logging
import json
import time
import PIL

logging.basicConfig(format='%(levelname)s >>> %(message)s', level=logging.DEBUG)

# Constants.
JSON_FILE = "response.json"
IMG_FILE = "image.jpg"
URL = "https://transportapi.com/v3/uk/bus/stop_timetables/" + BUS_CODE +  ".json?app_id=" + APP_ID + "&app_key=" + APP_KEY
LINE = 1
AIMED_ARRIVAL_TIME = 8
EPOCH_TIME = datetime(1970, 1, 1)

# Fonts.
Roboto_Black = "Roboto/Roboto-Black.ttf"
Roboto_BlackItalic = "Roboto/Roboto-BlackItalic.ttf"
Roboto_Bold = "Roboto/Roboto-Bold.ttf"
Roboto_BoldItalic = "Roboto/Roboto-BoldItalic.ttf"
Roboto_Italic = "Roboto/Roboto-Italic.ttf"
Roboto_Light = "Roboto/Roboto-Light.ttf"
Roboto_LightItalic = "Roboto/Roboto-LightItalic.ttf"
Roboto_Medium = "Roboto/Roboto-Medium.ttf"
Roboto_MediumItalic = "Roboto/Roboto-MediumItalic.ttf"
Roboto_Regular = "Roboto/Roboto-Regular.ttf"
Roboto_Thin = "Roboto/Roboto-Thin.ttf"
Roboto_ThinItalic = "Roboto/Roboto-ThinItalic.ttf"

# Font styles.
title = ImageFont.truetype(Roboto_Black, 45)
busNumber = ImageFont.truetype(Roboto_MediumItalic, 45)
busTime = ImageFont.truetype(Roboto_Bold, 45)
noBuses = ImageFont.truetype(Roboto_BoldItalic, 50)
buttons = ImageFont.truetype(Roboto_BlackItalic, 15)
pauseFont = ImageFont.truetype(Roboto_BlackItalic, 30)

# Colours.
BLACK  = (   0,  0,  0 )
WHITE  = ( 255,255,255 )
GREY_D = (  50, 50, 50 )
GREY_L = ( 200,200,200 )

# Button setup.
BUTTONS = [24, 16, 6, 5]
LABELS = ['Refresh', 'B', 'C', 'Pause']
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
PAUSE = False
REFRESH = False


# Button handler.
def buttonHandler(pin):
    global PAUSE, REFRESH

    label = LABELS[BUTTONS.index(pin)]
    if label == 'Refresh' :
        PAUSE = False
        REFRESH = True
        logging.warning(f"{label} button pressed.")
    if label == 'Pause' :
        PAUSE = not PAUSE
        logging.warning(f"{label} button pressed. Value: {PAUSE}")
        

# Get the departure information.
def getDepartureInfo(departure, printInfo):

    mode = departure["mode"]
    line = departure["line"]
    line_name = departure["line_name"]
    dir = departure["dir"]
    direction = departure["direction"]
    operator = departure["operator"]
    operator_name = departure["operator_name"]
    aimed_departure_time = departure["aimed_departure_time"]
    aimed_arrival_time = departure["aimed"]["arrival"]["time"]
    aimed_departure_time2 = departure["aimed"]["departure"]["time"]
    best_departure_estimate = departure["best_departure_estimate"]
    expected_departure_time = departure["expected_departure_time"]
    expected_arrival_time = departure["expected"]["arrival"]["time"]
    expected_departure_time2 = departure["expected"]["departure"]["time"]

    if printInfo : # Print the information or not.
        print()
        print("[\"mode\"]", mode)
        print("[\"line\"]", line)
        print("[\"line_name\"]", line_name)
        print("[\"dir\"]", dir)
        print("[\"direction\"]", direction)
        print("[\"operator\"]", operator)
        print("[\"operator_name\"]", operator_name)
        print("[\"aimed_departure_time\"]", aimed_departure_time)
        print("[\"aimed\"][\"arrival\"][\"time\"]", aimed_arrival_time)
        print("[\"aimed\"][\"departure\"][\"time\"]", aimed_departure_time2)
        print("[\"best_departure_estimate\"]", best_departure_estimate)
        print("[\"expected_departure_time\"]", expected_departure_time)
        print("[\"expected\"][\"arrival\"][\"time\"]", expected_arrival_time)
        print("[\"expected\"][\"departure\"][\"time\"]", expected_departure_time2)
        print()

    return [ mode, line, line_name, dir, direction, operator, operator_name, aimed_departure_time, aimed_arrival_time, aimed_departure_time2, best_departure_estimate, expected_departure_time, expected_arrival_time, expected_departure_time2 ]

# >>> Pull the bus times from the api.
def pullBusTimes():
    logging.info("Pull bus times.")

    response = urlopen(URL) # Get the json response.
    jsonDict = json.loads(response.read()) # Load response into dictionary.
    jsonString = json.dumps(jsonDict, indent=2) # Format the json for file output.

    # Write the response to file.
    with open(JSON_FILE, "w") as writer:
        writer.write(jsonString)

# >>> Read the bus times from json file.
def readBusTimes():
    logging.info("Read bus times.")

    f = open(JSON_FILE) # Open the file.
    jsonDict = json.load(f) # Load the values into the dictionary.
    f.close() # Close the file.
    return jsonDict

# >>> Extract the useful data from the json file.
def extractData(jsonDict, TESTING_MODE):
    logging.info("Extracting the useful json data.")

    departuresArray = [] # Reset the departures array table.
    departures = jsonDict["departures"]["all"] # Get the departures from the json dictionary.
    for i in range(len(departures)) : # For every departure, up to a maximum of EIGHT.
        row = getDepartureInfo(departures[i], False) # <- Print out info.
        departuresArray.append(row) # Add the departure information to the departures array.

    for row in departuresArray: # For every row,
        if TESTING_MODE : print(row) # print the row.

    if len(departuresArray) == 0:
        #logging.warning("No departures.")
        pass
    else:
        logging.info(f"{len(departuresArray)} departures found.")

    return departuresArray

# >>> Create image.
def createImage(departuresArray):
    logging.info("Creating the image.")

    global PAUSE

    img = Image.new(mode="RGB", size=(480,800), color=WHITE) # Create blank image.
    imgD = ImageDraw.Draw(img) # Prepare to draw text.

    # Header for buttons.
    imgD.rectangle((0, 0, 480, 10), fill=BLACK) # Main line.
    imgD.rectangle((30, 0, 102, 20), fill=BLACK) # Box for 'Refresh'.
    imgD.text((35,2), "REFRESH", font=buttons, fill=WHITE) # Text for 'Refresh'.
    imgD.rectangle((390, 0, 447, 20), fill=BLACK) # Box for 'Pause'.
    imgD.text((395,2), "PAUSE", font=buttons, fill=WHITE) # Text for 'Pause'.

    y = 10 # Set 'y' value.

    # Card for title.
    imgD.text((100, y+20), "Bus Schedule", font=title, fill=BLACK) # Text for 'Bus Schedule'.

    # Header for departures table.
    imgD.line((0, y+90, 480, y+90), fill=BLACK, width=10) # Line for bottom of 'Bus Schedule'.

    # Departures table.
    y = y + 175
    toggle = True
    for i in departuresArray:
        if departuresArray.index(i) > 6 : break # If there are EIGHT rows, break.
        #if toggle: imgD.rectangle((20, y-15, 460, y+65), fill=(230, 230, 230)) # Row background.
        imgD.rectangle((20, y-15, 460, y+65), fill=GREY_L if toggle else WHITE) # Row background.
        imgD.ellipse((30, y, 80, y+50), fill=WHITE if toggle else GREY_L) # Bus number background.

        imgD.text((42, y), i[LINE], font=busNumber, fill=BLACK) # Bus number.
        imgD.text((335, y), i[AIMED_ARRIVAL_TIME], font=busTime, fill=BLACK) # Aimed arrival time.

        y += 80 # Increase the y value.
        toggle = not toggle # Flip the toggle.

    if len(departuresArray) == 0 :
        imgD.text((42, y), "No Buses\n    Scheduled", font=noBuses, fill=BLACK) # Text if no buses are scheduled.

    if PAUSE :
        imgD.rectangle((180, 750, 295, 785), fill=BLACK)
        imgD.ellipse((163, 750, 198, 785), fill=BLACK)
        imgD.ellipse((277, 750, 312, 785), fill=BLACK)
        imgD.text((180,751), "PAUSED", font=pauseFont, fill=WHITE)

    img = img.rotate(270 if FLIP else 90, expand=1) # Rotate the image.
    img.save(IMG_FILE) # Export the image.

# >>> Show the image on Inky.
def showImage():
    logging.info("Outputting image to Inky.")

    inky = auto(ask_user=True, verbose=True)
    saturation = 0.5

    image = Image.open(IMG_FILE)
    resizedimage = image.resize(inky.resolution)

    inky.set_image(resizedimage, saturation=saturation)
    inky.show()

# >>> Reset time to Zero Seconds.
def waitForZeroSeconds():
    return
    while True:
        secs = float(datetime.now().strftime("%S.%f"))
        if secs < 0.1 : break
        logging.info(f"Waiting for ZERO, sleeping {60-secs} seconds...")
        sleep(60-secs)

# >>> Refresh the screen.
def refreshScreen(TESTING_MODE):
    global PAUSE
    
    if not TESTING_MODE and not PAUSE : pullBusTimes()
    jsonDict = readBusTimes()
    departuresArray = extractData(jsonDict, TESTING_MODE)
    if not TESTING_MODE: waitForZeroSeconds()
    createImage(departuresArray)
    showImage()
    return departuresArray


# Setup for buttons.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, buttonHandler, bouncetime=250)

# ! >>> MAIN  <<< ! #
TESTING_MODE = False
departuresArray = refreshScreen(TESTING_MODE)

while not TESTING_MODE:
    try:
        currentTime_S = datetime.now().strftime("%H:%M") # Get the current time as a string.
        currentTime_D = datetime.strptime(currentTime_S, "%H:%M") # Get the current time as a datetime.
        currentTime_T = int( ( EPOCH_TIME - currentTime_D ).total_seconds() / 60 ) # Get the current time since epoch.

        updateTime_S = datetime.strptime(departuresArray[floor(len(departuresArray)/2)][AIMED_ARRIVAL_TIME], "%H:%M").strftime("%H:%M") # Get the update time as a string.
        updateTime_D = datetime.strptime(departuresArray[floor(len(departuresArray)/2)][AIMED_ARRIVAL_TIME], "%H:%M") # Get the update time as a datetime.
        updateTime_T = int( ( EPOCH_TIME - updateTime_D ).total_seconds() / 60 ) # Get the update time since epoch.

        timeDifference = currentTime_T - updateTime_T # Get the total seconds until refresh.

        print()
        print("Current -> Next Update")
        print("%7s -> %s" % (currentTime_S, updateTime_S))
        logging.info(f"Sleeping for {timeDifference} minutes.")

        for _ in range(timeDifference * 60) : # Loop so that we can always escape with the buttons.
            if REFRESH == True:
                departuresArray = refreshScreen(TESTING_MODE)
                REFRESH = False
                break
            sleep(1)

        if currentTime_T <= updateTime_T and not PAUSE : # If current time is greater than the update time,
            logging.info("Current time == MiddleCeiling Row -> Refreshing Screen")
            logging.info(f"{currentTime_T} == {updateTime_T}")
            departuresArray = refreshScreen(TESTING_MODE) # refresh the display,
            waitForZeroSeconds() # and wait for ZERO seconds again.
            
        while PAUSE:
            sleep(1)

    except IndexError:
        logging.warning("No buses scheduled, sleeping for three hours.")
        for _ in range(3 * 60 * 60):
            if PAUSE == True:
                while PAUSE:
                    sleep(1)
                break
            if REFRESH == True:
                REFRESH = False
                break
            sleep(1)
        departuresArray = refreshScreen(TESTING_MODE)
    except Exception as e:
        logging.error(e)
        quit()
