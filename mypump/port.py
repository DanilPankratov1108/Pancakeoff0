""" Работа с COM PORT """
import threading
import time

import requests
import serial
import serial.tools.list_ports

import config_bot
import config_sy

"""Выбор порта и скорости"""
ser = serial.Serial()
ser.port = config_sy.PORT
ser.baudrate = config_sy.BAUDRATE

def write_port(code):
    """ Отправляем данные в порт и получаем ответ"""
    if ser.is_open:
            ascii = str(code) + "\r\n"
            ser.write(str.encode(ascii, encoding='ascii'))
            time.sleep(0.1)
            msg = read_port()
            return msg

def read_port():
    """ Считываем данные с COM PORT """
    if ser.is_open:
            msg = b''
            while ser.inWaiting() > 0:
                msg += ser.readline()

def port_pull():
    """ Опрос порта """
    if ser.is_open:
        if ser.inWaiting() > 0:
            msg = read_port()
            print(msg)
        threading.Timer(1, port_pull).start()
    else:
        print('Отключение от ком-порта...')
         

