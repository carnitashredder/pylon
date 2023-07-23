import urllib.request, json, os
from PIL import Image, ImageFont, ImageDraw
import time

initialized = False

canvas_width = 32*10
canvas_height = 128*10
white = (255,255,255)
size = int(canvas_width/1.4)
badgeSize = (size,size)
headerSize = int(canvas_height/15)
headerShape = [(0,0), (canvas_width, headerSize)]
font = ImageFont.FreeTypeFont("fonts/tiny.otf", int(headerSize*0.7))
posfont = ImageFont.FreeTypeFont("fonts/tiny.otf", int(size*0.2))

while True:

    #with urllib.request.urlopen("https://cf.nascar.com/live/feeds/series_2/4933/live_feed.json") as url:
    with urllib.request.urlopen("https://cf.nascar.com/live/feeds/live-feed.json") as url:
        data = json.load(url)
        #print(data["vehicles"][0]["driver"]["driver_id"])

        flag_state = str(data["flag_state"])
        lap_number = str(data["lap_number"])
        laps_in_race = str(data["laps_in_race"])
        driverList = list()
        for i in data["vehicles"]:
            driverList.append(i["driver"]["driver_id"])  
        #print (driverList)

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
    lapsColor = (255,255,255)
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
        badge = Image.open("./badge/" + str(driverList[k])+ ".jpg").resize(badgeSize)
        frame.paste(badge, (int((canvas_width - size)/2),int(1+headerSize+space*k)),mask=badge)

        draw.rectangle([(0,1+headerSize+space*k), (canvas_width,1+headerSize+space*k)], fill =white)

        tim = Image.new('RGBA', (size,size), (0,0,0,0))
        dr = ImageDraw.Draw(tim)
        ow, oh, w, h = draw.textbbox((0,0), str(k+1), font=posfont)
        dr.text((int(canvas_width/20),(size-h)/4), str(k+1), white, font=posfont)
        frame.paste(tim, (0,headerSize+space*k), tim)
    
    tim = Image.new('RGBA', (canvas_width,headerSize), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    ow, oh, w, h = draw.textbbox((0,0), lapsString, font=font)
    dr.text((((canvas_width-w)/2),(headerSize-h)/2), lapsString, lapsColor, font=font)
    frame.paste(tim, (0,0), tim)
    
    #frame.rotate(90)

    frame.save("screen.jpg")
    time.sleep(1)
