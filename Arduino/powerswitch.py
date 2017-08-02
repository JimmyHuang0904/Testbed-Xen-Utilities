import serial
import time

z1port = raw_input('location of device (/dev/ttyUSB*)? ')

z1baudrate = 115200
#z1port = '/dev/ttyUSB2'  # set the correct port before run it
print( z1port)

serialref = serial.Serial(
    port=z1port,
    baudrate=z1baudrate,
    timeout=5
)

def bootswitch():
    serialref.write('x03\n')
    time.sleep(1)
    serialref.write('x02\n')
    return

if __name__ == "__main__":
    hexwrite = raw_input('Enter hex value (eg. x0E) or boot:  ')
    if hexwrite == 'boot':
        bootswitch()
    else:
        serialref.write(hexwrite+'\n')
    serialref.close()

