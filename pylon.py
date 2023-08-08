debug = False

import urllib.request, json, os
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from dateutil import tz
import time
if debug == False:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions

initialized = False
previousTime = -1

tankRange = 100
canvas_width = 32
canvas_height = 128
size = 20
badgeSize = (size,size)
headerSize = 11
headerShape = [(0,0), (canvas_width, headerSize)]
lapFont = ImageFont.FreeTypeFont("fonts/tiny.otf", 5)
posfont = ImageFont.FreeTypeFont("fonts/tiny.otf", int(size*0.3))
numfont = ImageFont.FreeTypeFont("fonts/tiny.otf", int(size*0.6))
clockFont = ImageFont.FreeTypeFont("fonts/tiny.otf", int(size*0.9))

if debug == False:
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 2
    options.parallel = 1
    options.brightness = 75
    options.gpio_slowdown = 1
    options.pwm_lsb_nanoseconds = 300
    options.limit_refresh_rate_hz = 400
    options.hardware_mapping = 'adafruit-hat-pwm'
    options.drop_privileges = False
    matrix = RGBMatrix(options = options)

def padToTwoDigit(num):
    if num < 10:
        return "0" + str(num)
    else:
        return str(num)

def nascar(data):
    bg = Image.open("./bgs/test.png").convert("RGB")
    frame.paste(bg,(0,0))
    
    lap_number = str(data["lap_number"])
    track_length = data["track_length"]
    laps_in_race = str(data["laps_in_race"])
    driverList = list()
    numList = list()
    lapTimeList = list()
    pitLapList = list()
    for i in data["vehicles"]:
        driverList.append(i["driver"]["driver_id"])
        numList.append(i["vehicle_number"])
        lapTimeList.append(i["last_lap_time"])
        try:
            pitLapList.append(i["pit_stops"][-1]["pit_in_lap_count"])
        except:
            pitLapList.append(0)
                
    updateFlag = False
    flagFill = "purple"
    lapsColor = "white"
    lapsString = lap_number + "/" + laps_in_race
    initialized = False
    
    if flag_state == "1":
        flagFill = "green"
        lapsColor = "white"

    elif flag_state == "2":
        flagFill = "yellow"
        lapsColor = "black"

    elif flag_state == "3":
        flagFill = "red"
        lapsColor = "white"

    elif flag_state == "4":
        flagFill = "white"
        lapsColor = "black"

    elif flag_state == "9":
        flagFill = "grey"
        lapsColor = "black"
    else:
        initialized = False

    if initialized == False:
        initialized = True
        try:
           os.makedirs("./badge")
        except FileExistsError:
           # directory already exists
           pass
        
        with urllib.request.urlopen("http://cf.nascar.com/cacher/drivers.json") as url:
            data = json.load(url)
            for i in data["response"]:
                for j in driverList:
                    if j == i["Nascar_Driver_ID"]:
                        path = "./badge/" + str(i["Nascar_Driver_ID"]) + ".jpg"
                        if not os.path.isfile(path):
                            try:
                                urllib.request.urlretrieve(i["Badge_Image"], path)
                            except:
                                print("failed to get image for " + str(i["Nascar_Driver_ID"]))
                                break
    #flag status indicator
    flagOutline = flagFill
    draw = ImageDraw.Draw(frame)
    draw.rectangle(headerShape, fill =flagFill, outline =flagOutline)
    tim = Image.new('RGBA', (canvas_width,headerSize), (0,0,0,0))

    #lap string
    dr = ImageDraw.Draw(tim)
    ow, oh, w, h = draw.textbbox((0,0), lapsString, font=lapFont)
    dr.text((((canvas_width-w)/2),1+(headerSize-h)/2), lapsString, lapsColor, font=lapFont)
    frame.paste(tim, (0,0), tim)

    number = 5
    space = 23
    for k in range(number):
        try:
            badge = Image.open("./badge/" + str(driverList[k])+ ".jpg").convert("RGBA").resize(badgeSize)
            frame.paste(badge,(6,14 + space*k), mask=badge)
        except:
            tim = Image.new('RGBA', (size,size), (0,0,0,0))
            dr = ImageDraw.Draw(tim)
            ow, oh, w, h = draw.textbbox((0,0), numList[k], font=numfont)
            dr.text((int((size-w)/2),int((size-h)/2)), numList[k], 'white', font=numfont)
            frame.paste(tim, (int((canvas_width - size + 6)/2),int(4+headerSize+space*k)), tim)

        #lap comparison icons
        up = Image.open("./bgs/up.png").convert("RGB")
        even = Image.open("./bgs/even.png").convert("RGB")
        down = Image.open("./bgs/down.png").convert("RGB")
        if lapTimeList[k] < lapTimeList[0]:
            frame.paste(up,(1,21 + k*space))
        elif lapTimeList[k] > lapTimeList[0]:
            frame.paste(down,(1,30 + k*space))
        else:
            frame.paste(even,(1,27 + k*space))

        #fuel indicator
        percentage = 1-(float(lap_number) - pitLapList[k])*float(track_length)/tankRange
        meterHeight = int(21*percentage)
        if percentage > 0.50:
            meterColor = "green"
        elif percentage > 0.25:
            meterColor = "orange"
        else:
            meterColor = "red"
             
        draw.rectangle([(27,34 - meterHeight + k*space),(28,34 + k*space)], fill=meterColor)
        
    return frame

while True:
    time.sleep(1)
    frame = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))
    with urllib.request.urlopen("https://cf.nascar.com/live/feeds/live-feed.json") as url:
        data = json.load(url)
    
    flag_state = str(data["flag_state"])

    if flag_state != "9":
        frame = nascar(data)
        
    if flag_state == "9":
        currentTime = datetime.now(tz=tz.tzlocal())
        month = currentTime.month
        day = currentTime.day
        dayOfWeek = currentTime.weekday() + 1
        hours = currentTime.hour
        if hours > 12:
            hours = hours - 12
        minutes = currentTime.minute

        number = 5
        space = int((canvas_height - headerSize)/number)
        draw = ImageDraw.Draw(frame)
        ow, oh, w, h = draw.textbbox((0,0), padToTwoDigit(hours), font=clockFont)
        draw.text((int((size-w+14)/2),int(4+headerSize+space*1)), padToTwoDigit(hours), "white", font=clockFont)
        draw.text((int((size-w+14)/2),int(4+headerSize+space*2)), padToTwoDigit(minutes), "white", font=clockFont)

        draw.text((8,20), padToTwoDigit(month), "white", font=font)
        draw.text((18,20), padToTwoDigit(day), "white", font=font)

    if debug == False:
        matrix.SetImage(frame.rotate(270, expand=True))
    else:
       frame.save("screen.jpg") 
