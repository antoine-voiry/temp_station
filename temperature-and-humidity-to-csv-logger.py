#!/usr/bin/env python3

# Written by David Neuy
# Version 0.1.0 @ 03.12.2014
# This script was first published at: http://www.home-automation-community.com/
# You may republish it as is or publish a modified version only when you 
# provide a link to 'http://www.home-automation-community.com/'. 

#install dependency with 'sudo easy_install apscheduler' NOT with 'sudo pip install apscheduler'
import os, sys, time
import Adafruit_DHT
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from lcd_support import get_device
from file_logger import write_latest_value, write_hist_value_callback,open_file_ensure_header,write_value,write_header
from luma.core.render import canvas
from PIL import ImageFont

# the variable name
# the type of sensor
SENSOR_TYPE                       = Adafruit_DHT.AM2302 #DHT11/DHT22/AM2302 
# the GPIO pin
PIN_HUM_TEMP_SENSOR                          = 4
# the name of the room monitored
SENSOR_NAME                  = "living-room"
# the historical temp file path
hist_temperature_file_path   = "sensor-values/temperature_" + SENSOR_NAME + "_log_" + str(date.today().year) + ".csv"
# the latest temp file path 
latest_temperature_file_path = "sensor-values/temperature_" + SENSOR_NAME + "_latest_value.csv"
# the historical humidity file path
hist_humidity_file_path      = "sensor-values/humidity_" + SENSOR_NAME + "_log_" + str(date.today().year) + ".csv"
# the latest humidity file path
latest_humidity_file_path    = "sensor-values/humidity_" + SENSOR_NAME + "_latest_value.csv"
# the csv header for temp
csv_header_temperature       = "timestamp,temperature_in_celsius\n"
# the csv header for humidity
csv_header_humidity          = "timestamp,relative_humidity\n"
# the csv entry format to use to get the string
#csv_entry_format             = "{:%Y-%m-%d %H:%M:%S},{:0.1f}\n"
TIME_FORMAT             = "{ %H:%M:%S},{:0.1f}\n"

# the frequency in sec
sec_between_log_entries      = 60
# starting value
latest_humidity              = 0.0
latest_temperature           = 0.0
latest_value_datetime        = None




def temperature_display():
  '''
  get string to display temp on LCD  
  '''      
  return "    Temperature : %.2f" \
        % (latest_temperature)


def humidity_display():
  '''
  get string to display HUMIDITY on LCD  
  '''        
  return "    Humidity : %.2f" \
        % (latest_humidity)

def time_display():
  '''
  get string to display HUMIDITY on LCD  
  '''        
  return "    time : %s" \
        % (datetime.now().strftime("%H:%M:%S"))
	
def stats(device):
  '''
  WRITE THE Hum and temp on LCD  
  :param device the lcd device
  '''          
   # use custom font
  font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'FreePixel.ttf'))
  font2 = ImageFont.truetype(font_path, 9)

  with canvas(device) as draw:
        draw.text((8, 0), " --------------------", font=font2, fill="white")
        draw.text((0, 15), temperature_display(), font=font2, fill="white")
        draw.text((0, 25), humidity_display(), font=font2, fill="white")
        draw.text((0, 35), time_display(), font=font2, fill="white")
        draw.text((8, 45), " -------------------", font=font2, fill="white")

def starting(device):
  '''
  WRITE THE starting message  
  :param device the lcd device
  '''            
    # use custom font
  font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
  font2 = ImageFont.truetype(font_path, 14)

  with canvas(device) as draw:
    draw.text((0, 0),  " ------------------------", font=font2, fill="white")
    draw.text((3, 25), " ----- Starting.. -------" , font=font2, fill="white")
    draw.text((0, 51), " ------------------------", font=font2, fill="white")

		

# This is the main program
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")	

f_hist_temp = open_file_ensure_header(hist_temperature_file_path, 'a', csv_header_temperature)
f_hist_hum  = open_file_ensure_header(hist_humidity_file_path, 'a', csv_header_humidity)
print("STARTING")
device = get_device()
print("STARTING device")
starting(device)

print("Ignoring first 2 sensor values to improve quality...")
for x in range(2):
  Adafruit_DHT.read_retry(SENSOR_TYPE, PIN_HUM_TEMP_SENSOR)

print("Creating interval timer. This step takes almost 2 minutes on the Raspberry Pi...")
#create timer that is called every n seconds, without accumulating delays as when using sleep
#scheduler = BackgroundScheduler()
#scheduler.add_job(write_hist_value_callback, 'interval', seconds=sec_between_log_entries)
#scheduler.start()
#print("Started interval timer which will be called the first time in {0} seconds.".format(sec_between_log_entries))


try:
  while True:
    hum, temp = Adafruit_DHT.read_retry(SENSOR_TYPE, PIN_HUM_TEMP_SENSOR)
    if hum is not None and temp is not None:
      latest_humidity, latest_temperature = hum, temp
      latest_value_datetime = datetime.today()
      stats(device)
      write_latest_value(latest_temperature_file_path,latest_humidity_file_path,latest_value_datetime,latest_temperature, latest_humidity)
      write_hist_value_callback(hist_temperature_file_path, hist_humidity_file_path,latest_value_datetime, latest_temperature,latest_humidity )
	  
	  
    time.sleep(10)
except (KeyboardInterrupt, SystemExit):
  pass

