# RaspiInkyBusSchedule
Raspberry Pi based Bus Schedule using Pimoroni's Inky Impression 7.3" eInk Display.


### Setup
Create a file named CONFIG.py with the contents below:
```
APP_ID = "" # https://www.transportapi.com
APP_KEY = "" # https://www.transportapi.com
BUS_CODE = "" # https://www.openstreetmap.org/node/0
FLIP = False # Flip the display 180 degress.
```


### To Do
- [x] Pause functionality.
- [ ] Increase customisability in ```CONFIG.py``` file.
- [ ] Add dynamic sizing for Pimoroni's other Inky Impressions ( e.g. 4", 5.7" ).
- [ ] Compatibility with Pimoroni's Pico-based Inky Frames.
