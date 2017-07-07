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

if __name__ == "__main__":
    hexwrite = raw_input('Enter hex value (eg. x0E) ')
    serialref.write(hexwrite+'\n')
    serialref.close()

#serialref.write(bytes(b'asdf'))
#out = ''
# let's wait one second before reading output (let's give device time to answer)
#time.sleep(1)
#while serialref.inWaiting() > 0:
#    out += ser.read(40)

#if out != '':
#    print(">>" + out)


#serialref.close()

# print z1serial  # debug serial.

#def relay_1():
#    serialref.write("00".encode)
#    time.sleep(1)
#    serialref.write("01".encode)

#print serialref.is_open  # True for opened
#if serialref.is_open:
#    serialref.write('0f')
#    while True:
#        size = z1serial.inWaiting()
#        if size:
#            data = z1serial.read(size)
#            print data
#        else:
#            print 'no data'
#        time.sleep(1)
#else:
#    print 'z1serial not open'

#if __name__ == "__main__":
#    relay_1()

