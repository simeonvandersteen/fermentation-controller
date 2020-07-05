import os
import glob
import time

from RPLCD import CharLCD
from RPi import GPIO

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=22, pin_e=17, pins_data=[25, 24, 23, 18])
lcd.cursor_mode = 'hide'
degree = (
    0b00111,
    0b00101,
    0b00111,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
)
lcd.create_char(0, degree)

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def error(message):  
    print('Error reading data: ' + message)

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        error(lines[0])
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos == -1:
        error(lines[1])
    else:
        temp_string = lines[1][equals_pos+2:]
        temp_c = round(float(temp_string) / 1000.0, 1)
        return str(temp_c)

def lcd_print(message):
    lcd.clear()
    lcd.write_string(message)
    
def format_temp(temp):
    return 'Temperature is: ' + temp + '\x00C'

try:
    while True:
        lcd_print(format_temp(read_temp()))
        time.sleep(1)
finally:
    lcd.close(clear=True)

