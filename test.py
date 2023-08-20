import urllib.request, json, os
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
from dateutil import tz
import time

initialized = False

tankRange = 100
canvas_width = 32
canvas_height = 128
size = int(canvas_width/1.4)
badgeSize = (size,size)
headerSize = int(canvas_height/15)
headerShape = [(0,0), (canvas_width, headerSize)]
font = ImageFont.FreeTypeFont("fonts/tiny.otf", int(headerSize*0.7))
posfont = ImageFont.FreeTypeFont("fonts/tiny.otf", int(size*0.3))
numfont = ImageFont.FreeTypeFont("fonts/tiny.otf", int(size*0.6))

while True:
    currentTime = datetime.now(tz=tz.tzlocal())
    month = currentTime.month
    day = currentTime.day
    dayOfWeek = currentTime.weekday() + 1
    hours = currentTime.hour
    minutes = currentTime.minute

    #https://cf.nascar.com/live/feeds/series_2/5325/live_feed.json
    #https://cf.nascar.com/live/feeds/live-feed.json
    #with urllib.request.urlopen("https://cf.nascar.com/live/feeds/series_2/4933/live_feed.json") as url:
    with urllib.request.urlopen("https://cf.nascar.com/live/feeds/live-feed.json") as url:
        data = json.load(url)
        #print(data["vehicles"][0]["driver"]["driver_id"])

        flag_state = str(data["flag_state"])
        lap_number = str(data["lap_number"])
        laps_in_race = str(data["laps_in_race"])
        track_length = data["track_length"]
        driverList = list()
        numList = list()
        lapTimeList = list()
        pitLapList = list()
        for i in data["vehicles"]:
            driverList.append(i["driver"]["driver_id"])
            numList.append(i["vehicle_number"])
            lapTimeList.append(i["last_lap_time"])
            pitLapList.append(i["pit_stops"][-1]["pit_in_lap_count"])
            #pitLapList.append(120)
        #print (pitLapList)

    if initialized == False:
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
            initialized = True

    flagFill = "purple"
    lapsColor = "white"
    lapsString = lap_number + "/" + laps_in_race
    
    if flag_state == "1":
        flagFill = "green"
        lapsColor = (255,255,255)

    elif flag_state == "2":
        flagFill = "yellow"
        lapsColor = (0,0,0)

    elif flag_state == "3":
        flagFill = "red"
        lapsColor = (255,255,255)

    elif flag_state == "4":
        flagFill = "white"
        lapsColor = (0,0,0)

    elif flag_state == "9":
        flagFill = "grey"
        lapsColor = (0,0,0)
    else:
        initialized = False

    flagOutline = flagFill

    frame = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))
    draw = ImageDraw.Draw(frame)
    draw.rectangle(headerShape, fill =flagFill, outline =flagOutline)

    number = 5
    space = int((canvas_height - headerSize)/number)
    for k in range(number):
        try:
            badge = Image.open("./badge/" + str(driverList[k])+ ".jpg").convert("RGBA").resize(badgeSize)
            frame.paste(badge, (int((canvas_width - size)/2),int(2+headerSize+space*k)))
        except:
            tim = Image.new('RGBA', (size,size), (0,0,0,0))
            dr = ImageDraw.Draw(tim)
            ow, oh, w, h = draw.textbbox((0,0), numList[k], font=numfont)
            dr.text((int((size-w)/2),int((size-h)/2)), numList[k], 'white', font=numfont)
            frame.paste(tim, (int((canvas_width - size + 6)/2),int(4+headerSize+space*k)), tim)

        draw.rectangle([(0,1+headerSize+space*k), (canvas_width,1+headerSize+space*k)], fill='white')

        draw.rectangle([(0,1+headerSize+space*k), (canvas_width,1+headerSize+space*k)], fill ='white')

        tim = Image.new('RGBA', (size,size), (0,0,0,0))
        dr = ImageDraw.Draw(tim)
        ow, oh, w, h = draw.textbbox((0,0), str(k+1), font=posfont)
        dr.text((int(canvas_width/20),(size-h)/4), str(k+1), 'white', font=posfont)
        frame.paste(tim, (0,headerSize+space*k), tim)

        if lapTimeList[k] < lapTimeList[0]:
            draw.polygon([(2,20+space*k),(1,22+space*k),(3,22+space*k)], fill = 'green')
        elif lapTimeList[k] > lapTimeList[0]:
            draw.polygon([(1,26+space*k),(3,26+space*k),(2,28+space*k)], fill = 'red')
        else:
            draw.rectangle([(1,24+space*k),(3,24+space*k)], fill='white')

        percentage = 1-(float(lap_number) - pitLapList[k])*float(track_length)/tankRange
        meterHeight = int((33-10)*percentage)
        if percentage > 0.75:
            meterColor = "green"
        elif percentage > 0.50:
            meterColor = "orange"
        else:
            meterColor = "red"
            
        #pixles 10 to 33  
        draw.rectangle([(canvas_width-2,33-meterHeight+space*k),(canvas_width-1,33+space*k)], fill =meterColor)
    
    tim = Image.new('RGBA', (canvas_width,headerSize), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    ow, oh, w, h = draw.textbbox((0,0), lapsString, font=font)
    dr.text((((canvas_width-w)/2),1+(headerSize-h)/2), lapsString, lapsColor, font=font)
    frame.paste(tim, (0,0), tim)
    
    #frame.rotate(90)

    frame.save("screen.jpg")
    time.sleep(1)
