
import os, sys, time
from datetime import datetime, date

# the csv header for temp
CSV_HEADER_TEMPERATURE       = "timestamp,temperature_in_celsius\n"
# the csv header for humidity
CSV_HEADER_HUMIDITY          = "timestamp,relative_humidity\n"
# the csv entry format to use to get the string
CSV_ENTRY_FORMAT             = "{:%Y-%m-%d %H:%M:%S},{:0.1f}\n"


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
  line = CSV_ENTRY_FORMAT.format(datetime, value)
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


def write_hist_value_callback(f_hist_temp,f_hist_hum,latest_value_datetime, latest_temperature,latest_humidity ):
  '''
  Write temp and hum into hist file
   use global variable
   
  '''   
  with open_file_ensure_header(f_hist_temp, 'a', CSV_HEADER_TEMPERATURE) as f_hist_temp_f:  #open and truncate
    write_value(f_hist_temp_f, latest_value_datetime, latest_temperature)
    f_hist_temp_f.close()
  with open_file_ensure_header(f_hist_hum, 'a', CSV_HEADER_HUMIDITY) as f_hist_hum_f:  #open and truncate
    write_value(f_hist_hum_f, latest_value_datetime, latest_humidity)
    f_hist_hum_f.close()


def write_latest_value(latest_temperature_file_path,latest_humidity_file_path,latest_value_datetime,latest_temperature, latest_humidity):
  '''
  Write temp and hum into latest file
   use global variable
  
  '''      
  with open_file_ensure_header(latest_temperature_file_path, 'w', CSV_HEADER_TEMPERATURE) as f_latest_value:  #open and truncate
    write_value(f_latest_value, latest_value_datetime, latest_temperature)
  with open_file_ensure_header(latest_humidity_file_path, 'w', CSV_HEADER_HUMIDITY) as f_latest_value:  #open and truncate
    write_value(f_latest_value, latest_value_datetime, latest_humidity)

