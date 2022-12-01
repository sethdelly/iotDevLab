import json, machine, time, network
from servo import Servo
from machine import PWM, Pin,ADC
from time import sleep,time
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
import urequests as requests
from sht3x import SHT3X


SHT30 = SHT3X()
temp, humid = SHT30.getTempAndHumi()
np=NeoPixel(Pin(21), 1)
relay=Pin(26,Pin.OUT)
TIMEOUT = None
adc= ADC(Pin(36))
buzzer=Pin(18,Pin.OUT)
buzz=PWM(buzzer)
buzz.deinit()
CAYENNE_UNAME="e1cb11e0-9ec5-11eb-b767-3f1a8f1211ba"
CAYENNE_PASSWORD="17348611765ab65c62c5bebfeb99e9ca41bee8f6"
CAYENNE_CLIENT= "e47d2360-f505-11eb-b767-3f1a8f1211ba"   
server="mqtt.mydevices.com"
#iftt api variables
webhook_url="https://maker.ifttt.com/trigger/FIRE/with/key/d4-rwPEBcD6dTNo-DD6o8hopYUDioCLOi8Fro1qDvVb"
WEBHOOK_URL=" https://maker.ifttt.com/trigger/FIRE/with/key/d4-rwPEBcD6dTNo-DD6o8hopYUDioCLOi8Fro1qDvVb "



connecting to the internet
station=network.WLAN(network.STA_IF)
station.active( True)
station.connect("jay", "123456789")
print(station.isconnected())
print(station.ifconfig())


connecting to the cayenne site
c = MQTTClient(CAYENNE_CLIENT, server,user=CAYENNE_UNAME, password=CAYENNE_PASSWORD)
try:
     c.connect()
     print("connection Success...")
except Exception as e:
     print(e)
     print("connection Error...")
    

#POST data to the cayenne 
topic="v1/"+CAYENNE_UNAME+"/things/"+CAYENNE_CLIENT+"/data/json"
bytes_topic=bytes(topic,'utf-8')


#functions

#notify the user
def notify():
    try:
        r=requests.get(webhook_url)
        print(r.text)
    except Exception as e:
        print(e)
        
#call the user
def call():
    try:
        r=requests.get(WEBHOOK_URL)
        print(r.text)
    except Exception as e:
        print(e)
        
#buzzer functions
def buz():
    buzz.init()
    buzz.freq(500)
    buzz.duty(50)
    sleep(2)
    buzz.duty(0)
    
def buzzz():
    buzz.init()
    buzz.freq(2000)
    buzz.duty(50)
    sleep(2)
    buzz.duty(0)
        
#POST data to the cayenne site

data=[
    {
       "channel": 1,
       "value": temp,
       "type": "temp",
       "unit": "c"
    },
    {
       "channel": 2,
       "value": humid,
       "type": "rel_hum",
       "unit": "p"
    }
]

def sendData(data):
    Data=json.dumps(data)
    c.publish(bytes_topic,Data)

def ledoff():
    np[0]=(0,0,0)
    np.write()
    
#neopixel functions
def redlight():
    np[0]=(255,0,0)
    np.write()
    sleep(1)
    np[0]=(255,0,0)
    np.write()
    
def bluelight():
    np[0]=(0,255,0)
    np.write()
    
def greenlight():
    np[0]=(0,0,255)
    np.write()

#detect smoke
def senseSmoke():
    value=adc.read()
    print(value)
    
#pumpwater 
def pumpWater():
    relay.value(1)
    sleep(3)
    relay.value(0)
    sleep(2)



    
while True:
    try:
        sendData(data)
        ledoff()
        senseSmoke()
        if value <=2700:
            greenlight()
        elif value>2700 and value<3000:
            bluelight()
            buzzz()
        else:
            redlight()
            pumpWater()
            buz()
            if TIMEOUT is None:
                    TIMEOUT =  time()
                    call()
                    notify()
                elif time() - TIMEOUT >= 30:
                    TIMEOUT =  time()
                    call()
                    notify()
                print('Time lapse ',  time() - TIMEOUT)
    except Exception as e:
        print(e)
        with open('error_logs.txt', 'a') as err_log:
            err_log.write(str(e)+'\n')
    print()
        

        



   
    
    
    

