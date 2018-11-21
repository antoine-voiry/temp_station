# Written by David Neuy
# Version 0.1.0 @ 03.12.2014
# This script was first published at: http://www.home-automation-community.com/
# You may republish it as is or publish a modified version only when you 
# provide a link to 'http://www.home-automation-community.com/'. 

#install dependency with 'sudo easy_install apscheduler' NOT with 'sudo pip install apscheduler'
import os, sys, Adafruit_DHT, time
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

# the variable name
# the type of sensor
sensor                       = Adafruit_DHT.AM2302 #DHT11/DHT22/AM2302 
# the GPIO pin
pin                          = 4
# the name of the room monitored
sensor_name                  = "living-room"
# the historical temp file path
hist_temperature_file_path   = "sensor-values/temperature_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
# the latest temp file path
latest_temperature_file_path = "sensor-values/temperature_" + sensor_name + "_latest_value.csv"
# the historical humidity file path
hist_humidity_file_path      = "sensor-values/humidity_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
# the latest humidity file path
latest_humidity_file_path    = "sensor-values/humidity_" + sensor_name + "_latest_value.csv"
# the csv header for temp
csv_header_temperature       = "timestamp,temperature_in_celsius\n"
# the csv header for humidity
csv_header_humidity          = "timestamp,relative_humidity\n"
# the csv entry format to use to get the string
csv_entry_format             = "{:%Y-%m-%d %H:%M:%S},{:0.1f}\n"
# the frequency in sec
sec_between_log_entries      = 60
# starting value
latest_humidity              = 0.0
latest_temperature           = 0.0
latest_value_datetime        = None


def write_header(file_handle, csv_header):
   '''
   Write the header of a file

   :param file_handle: The file handle of an open file
   :param csv_header: The csv header to write
   '''  
   file_handle.write(csv_header)

def write_value(file_handle, datetime, value):
  '''
  Write value into a file a file

  :param file_handle: The file handle of an open file
  :param datetime: a datetime
  :param value: the value to write (a string)
  '''  
  line = csv_entry_format.format(datetime, value)
  file_handle.write(line)
  file_handle.flush()


def open_file_ensure_header(file_path, mode, csv_header):
  '''
  Write value into a file a file
  :param file_path: The path of the file to open
  :param datetime: the mode 
  :param value: the csv header to write 
  :return the file hanle
  '''    
  f = open(file_path, mode, os.O_NONBLOCK)
  if os.path.getsize(file_path) <= 0:
    write_header(f, csv_header)
  return f


def write_hist_value_callback():
  '''
  Write temp and hum into hist file
   use global variable
   
  '''      
  write_value(f_hist_temp, latest_value_datetime, latest_temperature)
  write_value(f_hist_hum, latest_value_datetime, latest_humidity)



def write_latest_value():
  '''
  Write temp and hum into latest file
   use global variable
  
  '''      
  with open_file_ensure_header(latest_temperature_file_path, 'w', csv_header_temperature) as f_latest_value:  #open and truncate
    write_value(f_latest_value, latest_value_datetime, latest_temperature)
  with open_file_ensure_header(latest_humidity_file_path, 'w', csv_header_humidity) as f_latest_value:  #open and truncate
    write_value(f_latest_value, latest_value_datetime, latest_humidity)


def temperature_display():
  '''
  get string to display temp on LCD  
  '''      
  return " Temp : %.2f" \
        % (latest_temperature)


def humidity_display():
  '''
  get string to display HUMIDITY on LCD  
  '''        
  return " Hum : %.2f" \
        % (latest_humidity)
	
def stats(device):
  '''
  WRITE THE Hum and temp on LCD  
  :param device the lcd device
  '''          
   # use custom font
  font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                'fonts', 'C&C Red Alert [INET].ttf'))
  font2 = ImageFont.truetype(font_path, 14)

  with canvas(device) as draw:
        draw.text((0, 0), " ----------------", font=font2, fill="white")
        draw.text((0, 15), temperature_display(), font=font2, fill="white")
        draw.text((0, 30), humidity_display(), font=font2, fill="white")
        draw.text((0, 45), " ---------------", font=font2, fill="white")

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
    draw.text((0, 25), " ----- Starting.. -------" , font=font2, fill="white")
    draw.text((0, 51), " ------------------------", font=font2, fill="white")

		

# This is the main program
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")	

f_hist_temp = open_file_ensure_header(hist_temperature_file_path, 'a', csv_header_temperature)
f_hist_hum  = open_file_ensure_header(hist_humidity_file_path, 'a', csv_header_humidity)

device = get_device()
starting(device)

print("Ignoring first 2 sensor values to improve quality...")
for x in range(2):
  Adafruit_DHT.read_retry(sensor, pin)

print("Creating interval timer. This step takes almost 2 minutes on the Raspberry Pi...")
#create timer that is called every n seconds, without accumulating delays as when using sleep
scheduler = BackgroundScheduler()
scheduler.add_job(write_hist_value_callback, 'interval', seconds=sec_between_log_entries)
scheduler.start()
print("Started interval timer which will be called the first time in {0} seconds.".format(sec_between_log_entries))


try:
  while True:
    hum, temp = Adafruit_DHT.read_retry(sensor, pin)
    if hum is not None and temp is not None:
      latest_humidity, latest_temperature = hum, temp
      latest_value_datetime = datetime.today()
      stats(device)
      write_latest_value()
	  
	  
    time.sleep(1)
except (KeyboardInterrupt, SystemExit):
  scheduler.shutdown()
  pass

