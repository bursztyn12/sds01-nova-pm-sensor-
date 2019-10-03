import array
import mysql.connector
import serial
import struct
import time
import datetime
from datetime import date

ser = serial.Serial()
ser.port = "COM3"
ser.baudrate = 9600

# commands
measure = "\xaa\xb4\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x02\xab"
sleep = "\xaa\xb4\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x05\xab"
work = "\xaa\xb4\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x06\xab"

# amount of measurers
amount = 20

# amount of time during sensor is inactive(in seconds)
sleep_duration = 3600

ser.open()
ser.flushInput()


def measurement():

    print("measurement fun")

    ser.write(measure)

    time.sleep(1)

    response = ser.read(size=10)
    print("odpowiedz : ", response)

    tab = struct.unpack('BBBBxxBB', response[2:])
    pm25low = tab[0]
    pm25high = tab[1]

    pm10low = tab[2]
    pm10high = tab[3]

    pm25 = float((pm25high * 256) + pm25low) / 10
    pm10 = float((pm10high * 256) + pm10low) / 10

    tab1 = array.array('f', [0, 0])

    tab1[0] = pm25
    tab1[1] = pm10

    print("tab[0] : ", tab1[0])
    print("tab[1] : ", tab1[1])

    print("pm25 : ", pm25)
    print("pm10 : ", pm10)

    return tab1


def work_state():
    print("work_state fun")

    ser.write(sleep)

    response = ser.read(size=10)
    print("response sleep : ", response)

    time.sleep(sleep_duration)

    print("work")

    ser.write(work)
    response = ser.read(size=10)
    print("response : ", response)

    time.sleep(30)


def average(avg1, avg2):

    print("all sum pm25 : ", avg1)
    print("all sum pm10 : ", avg2)

    average_pm25 = avg1 / amount
    average_pm10 = avg2 / amount

    average_pm25 = float("{0:.2f}".format(average_pm25))
    average_pm10 = float("{0:.2f}".format(average_pm10))

    print("pm 2.5 average : ", average_pm25)
    print("pm 10 average : ", average_pm10)

    mysql_database(average_pm25, average_pm10)


def mysql_database(p25, p10):
    conn = mysql.connector.connect(user='-', password='-', host='-', database='-')

    cursor = conn.cursor()

    query = ("INSERT INTO table "
              "(col1, col2, col3, col4) "
              "VALUES (%(-)s, %(-)s, %(-)s, %(-)s)")

    now = datetime.datetime.now()
    time_ = datetime.time(now.hour, now.minute, now.second)
    date_ = date(now.year, now.month, now.day)

    values = {
        '-': -,
        '-': -,
        '-': -,
        '-': -,
    }

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    print("30 sec delay")
    time.sleep(30)
    tab = array.array('f', [0, 0])
    sum_pm25 = 0
    sum_pm10 = 0
    var = 0
    while True:
        if var == amount:
            average(sum_pm25, sum_pm10)
            work_state()
            var = 0
            sum_pm25 = 0
            sum_pm10 = 0
        else:
            tab = measurement()
            sum_pm25 += tab[0]
            print("sum_pm25 : ", sum_pm25)
            sum_pm10 += tab[1]
            print("sum_pm10 : ", sum_pm10)
        var += 1
        print("var : ", var)
