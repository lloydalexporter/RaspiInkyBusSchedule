#!/usr/bin/env python3

from urllib.request import urlopen
from inky.auto import auto
from datetime import datetime
from CONFIG import APP_ID, APP_KEY, BUS_CODE, FLIP
from time import sleep
from math import ceil, floor
from PIL import Image, ImageDraw, ImageFont
from os import system
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

title = ImageFont.truetype(Roboto_Black, 45)
busNumber = ImageFont.truetype(Roboto_MediumItalic, 45)
busTime = ImageFont.truetype(Roboto_Bold, 45)
noBuses = ImageFont.truetype(Roboto_BoldItalic, 50)


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
    
    img = Image.new(mode="RGB", size=(480,800), color="white") # Create blank image.
    
    imgD = ImageDraw.Draw(img) # Prepare to draw text.
    imgD.text((30, 20), "Bus Schedule", font=title, fill=(50, 50, 50))
    imgD.line((20, 90, 460, 90), fill=(100, 100, 100), width=10)

    y = 140
    toggle = True
    for i in departuresArray:
        if departuresArray.index(i) > 8 : break # If there are EIGHT rows, break.
        #if toggle: imgD.rectangle((20, y-15, 460, y+65), fill=(230, 230, 230)) # Row background.
        imgD.rectangle((20, y-15, 460, y+65), fill=(200, 200, 200) if toggle else (255,255,255)) # Row background.
        imgD.ellipse((30, y, 80, y+50), fill=(255, 255, 255) if toggle else (200, 200, 200)) # Bus number background.

        imgD.text((42, y), i[LINE], font=busNumber, fill=(0, 0, 0)) # Bus number.
        imgD.text((335, y), i[AIMED_ARRIVAL_TIME], font=busTime, fill=(0, 0, 0)) # Aimed arrival time.

        y += 80 # Increase the y value.
        toggle = not toggle # Flip the toggle.
        
    if len(departuresArray) == 0 :
        imgD.text((42, y), "No Buses\n    Scheduled", font=noBuses, fill=(0, 0, 0)) # Text if no buses are scheduled.

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

    # script = "/home/pi/Pimoroni/inky/examples/7color/image.py " + imgFile # Pimoroni E-ink display string.
    # system(script) # Run the script to display the image.


# >>> Reset time to Zero Seconds.
def waitForZeroSeconds():
    while True:
        secs = float(datetime.now().strftime("%S.%f"))
        if secs < 0.1 : break
        logging.info(f"Waiting for ZERO, sleeping {60-secs} seconds...")
        sleep(60-secs)


def refreshScreen(TESTING_MODE):
    if not TESTING_MODE : pullBusTimes()
    jsonDict = readBusTimes()
    departuresArray = extractData(jsonDict, TESTING_MODE)
    waitForZeroSeconds()
    createImage(departuresArray)
    showImage()
    return departuresArray

# ! >>> MAIN  <<< ! #
TESTING_MODE = False
departuresArray = refreshScreen(TESTING_MODE)

while True:
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
        
        sleep(timeDifference * 60) # Sleep for all the minutes.
        
        if currentTime_T >= updateTime_T : # If current time is greater than the update time,
            logging.info("Current time == MiddleCeiling Row -> Refreshing Screen")
            departuresArray = refreshScreen(TESTING_MODE) # refresh the display,
            waitForZeroSeconds() # and wait for ZERO seconds again.
    
    except IndexError:
        logging.warning("No buses scheduled, sleeping for three hours.")
        sleep(3600)
        
    except Exception as e:
        logging.error(e)
        quit()


# Currently this wont work at the end of the day when there are few buses, nor at the start of the day when there are no buses, gonna involve some fun checks and that.
