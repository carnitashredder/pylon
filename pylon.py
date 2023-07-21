import urllib.request, json, os
from PIL import Image, ImageFont, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time

initialized = False

canvas_width = 128
canvas_height = 32
white = (255,255,255)
font = ImageFont.truetype("fonts/tiny.otf", 5)

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 2
options.parallel = 1
options.brightness = 100
#options.pixel_mapper_config = "U-mapper;Rotate:90"
options.gpio_slowdown = 1
options.pwm_lsb_nanoseconds = 80
options.limit_refresh_rate_hz = 150
options.hardware_mapping = 'adafruit-hat'
options.drop_privileges = False
matrix = RGBMatrix(options = options)

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

    if flag_state == "2":
        flagFill = "yellow"
        lapsColor = (0,0,0)

    if flag_state == "3":
        flagFill = "red"
        lapsColor = (255,255,255)

    if flag_state == "4":
        flagFill = "white"
        lapsColor = (0,0,0)

    if flag_state == "9":
        flagFill = "grey"
        lapsColor = (0,0,0)

    flagOutline = flagFill
    
    size = (20,20)
    shape = [(127,0), (127-6, 31)]
    black_screen = Image.new("RGB", (canvas_width, canvas_height), (0,0,0))
    pos1 = Image.open("./badge/" + str(driverList[0])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos2 = Image.open("./badge/" + str(driverList[1])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos3 = Image.open("./badge/" + str(driverList[2])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos4 = Image.open("./badge/" + str(driverList[3])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos5 = Image.open("./badge/" + str(driverList[4])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos6 = Image.open("./badge/" + str(driverList[5])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos7 = Image.open("./badge/" + str(driverList[6])+ ".jpg").convert("RGB").resize(size).rotate(270)
    pos8 = Image.open("./badge/" + str(driverList[7])+ ".jpg").convert("RGB").resize(size).rotate(270)
    frame = black_screen.copy()
    frame.paste(pos1, (100+4,11))
    frame.paste(pos2, (85+4,11))
    frame.paste(pos3, (70+4,11))
    frame.paste(pos4, (55+4,11))
    frame.paste(pos5, (40+4,11))
    frame.paste(pos6, (25+4,11))
    frame.paste(pos7, (10+4,11))
    frame.paste(pos8, (-5+4,11))
    draw = ImageDraw.Draw(frame)
    draw.rectangle(shape, fill =flagFill, outline =flagOutline)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), lapsString, lapsColor, font=font)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (97,2), tim)
    
    posfont = ImageFont.truetype("fonts/tiny.otf", 10)
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "1", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (85+4,2), tim)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "2", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (70+4,2), tim)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "3", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (55+4,2), tim)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "4", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (40+4,2), tim)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "5", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (25+4,2), tim)
   
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "6", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (10+4,2), tim)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "7", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (-5+4,2), tim)
    
    tim = Image.new('RGBA', (30,30), (0,0,0,0))
    dr = ImageDraw.Draw(tim)
    dr.text((0,0), "8", white, font=posfont)
    tim = tim.rotate(270,  expand=1)
    frame.paste(tim, (-20+4,2), tim)
    
    frame.rotate(180)

    matrix.SetImage(frame)
    time.sleep(0.5)
