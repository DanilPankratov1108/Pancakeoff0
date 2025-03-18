
import sys
import time
from threading import Thread

import serial
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
import serial.tools.list_ports
import logging
import keyboard as kb
import threading

"""Логирование"""

logging.basicConfig(level=logging.INFO, filename="runze_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

"""Настройки порта"""

baudrate = 9600
stopbits = STOPBITS_ONE
timeout = 1
bytesize = EIGHTBITS
parity = PARITY_NONE

"""Подключение и выбор порта"""

ports = list(serial.tools.list_ports.comports())
target_manufacturer = 'wch.cn'
target_pid = 29987
target_vid = 6790
com_port = None
print("Доступные ком порты:")
for port in ports:
    print(port.device)

if port.pid == target_pid:
    com_port = port.device
    print(f'Подключение к {com_port}')
else:
    raise ValueError('No required Com port found')

if port is None:
    raise ValueError('No COM port found')

try:
            ser = serial.Serial(com_port,
                        baudrate=baudrate,
                        timeout=1,
                        stopbits=stopbits,
                        parity=parity,
                        bytesize=bytesize
                        )
except ValueError as ve:
    print("Error:", str(ve))
    logging.error('Serial port error.')

except serial.SerialException as se:
    print("Serial port error:", str(se))
    logging.error('Serial port error.')

except Exception as e:
    print("An error occurred:", str(e))

except KeyboardInterrupt:
    pass

"""Чем оборудован насос?"""

PUMP = 'SY-01B'     # модель насоса Runze Fluid
HEAD = 'M12'        # головка в насосе
VALVE = 12          # число клапанов в головке
VOLUME = 125        # объём шприца в мкл
SQUARE = 2.083      # площадь сечения шприца в мм^2

"""Важные константы"""

"""1)В единицах кода(в шагах)"""

NOM_STEP = 6000     # номинальный ход
MAX_STEP = 12000    # максимальный ход
MIN_STEP = 1        # минимальный ход
MAX_VEL = 1000      # максимальная скорость
MIN_VEL = 1         # минимальная скорость
DEFAULT_VEL = 4000  # скорость по умолчанию

"""2)В абсолютных единицах(мкл и мкл/мин)"""

REAL_NOM_STEP = 30          # номинальный ход
REAL_MAX_STEP = 125         # максимальный ход
REAL_MIN_STEP = 1/200       # минимальный ход
REAL_MAX_VEL = 960          # максимальная скорость
REAL_MIN_VEL = 6.25         # минимальная скорость
REAL_DEFAULT_VEL = 640      # скорость по умолчанию

"""Коэффициенты перевода"""

k1 = (1.25 * 10 ** -7) / (1.3 * 10 ** -9)       # Перевод объёма из мкл в шаги
k2 = 6.25                                       # Перевод скорости из мкл/мин в шаги/сек

"""Битовые строки, которые идут от насоса"""

state_work = b'\xff/0@\x03\r\n'     #В процессе работы
state_free = b'\xff/0`\x03\r\n'     #Свободен

"""Нулевые строки"""

N = b''                             #Пустая битовая строка
M = ""                              #Пустая строка

"""Некоторые команды в ASCII"""

state = '/1QR' + '\r\n' #для проверки состояния
stop = '/1TR' + '\r\n'  #для экстренной остановки

"""Прекращение работы при нажатии на клавишу t"""

check = True

def stop_device():
    global check
    ser.write(str.encode(stop, encoding='ascii'))
    print('Остановка. Рекомендуется сделать реинициализацию')
    logging.info('Stopping with /1TR command. It is recommended to do initialization.')
    check = False

def check_stop():
    kb.wait('t')
    stop_device()

# """Время работы кода"""
#
# def time_work(T: long):
#     com = list()
#     global running
#     while
#         running = True

# """Флаг для запуска работы на время"""
#
running = False

"""Декоратор, который навешиваетя на некоторые функции в библиотеке. Он позволяет определять состояние выполнения функций насоса."""

def check_state_pump(func):
    def wrapper(*args, **kwargs):
                # ser.write(str.encode(state, encoding='ascii'))
                N = ser.read_until(expected=state_work)
                stop_thread = threading.Thread(target=check_stop)
                stop_thread.daemon = True
                stop_thread.start()
                # time_thread = threading.Thread(target=time_work)
                # time_thread.daemon = True
                # time_thread.start()
                while N == state_work and check:
                    ser.write(str.encode(state, encoding='ascii'))
                    N = ser.read_until(expected=state_work)
                return func(*args, **kwargs)
    return wrapper

"""Библиотека функций по управлению насосами Runze Fluid"""

class mypump:

    """Опрос состояния выполнения команд в насосе: Free - свободен, Busy - занят"""

    def state():
        check_state = '/1QR' + '\r\n'
        ser.write(str.encode(check_state, encoding='ascii'))
        STATE = b''
        while ser.inWaiting() > 0:
                STATE += ser.readline()
                if STATE == state_work:
                    print('Busy')
                else:
                    print('Free')

    """Помощь"""

    def help():
        print('Список команд, доступных для управления насосом:\n'
              'stop - остановка работы\n'
              'info - техническая информация\n'
              'state - проверка состояния выполнения команды\n'
              'init - инициализация\n'
              'set_volume - установка объёма в мкл с параметрами скоростей и ускорения\n'
              'add_volume - добавить объём к уже установленному\n'
              'output_volume - вывод объёма\n'
              )

    """Остановка выполнения команд"""

    def stop():
        kb.wait('t')
        stop_device()

    """Некоторая техническая информация"""

    def info():
        print(f'Модель шприцевого насоса: {PUMP}\n'
              f'Объём шприца: {VOLUME} мкл\n'
              f'Головка шприца: {HEAD}\n'
              f'Номинальный ход: {REAL_NOM_STEP} мкл\n'
              f'Максимальный ход: {REAL_MAX_STEP} мкл\n'
              f'Минимальный ход: {REAL_MIN_STEP} мкл\n'
              f'Cкорость по умолчанию: {REAL_DEFAULT_VEL} мкл/мин\n'
              f'Максимальная скорость: {REAL_MAX_VEL} мкл/мин\n'
              f'Минимальная скорость: {REAL_MIN_VEL} мкл в мин\n')

    """Тайм слип в минутах"""

    @check_state_pump
    def pause(self, T: float):
        t = T * 60
        print(f'Пауза {T} мин')
        time.sleep(t)

    """Инициализация"""

    @check_state_pump
    def init(self):
            init = str('/1ZR') + '\r\n'
            try:
                ser.write(str.encode(init, encoding = 'ascii'))
                print('Инициализация')
                logging.info('Initialization.')
            except serial.SerialException as se:
                print(f"Error write to {port}", str(se))
                logging.error(f'Error write to {port} during initialization.')

    """Ввод объёма в мкл с заданной скоростью в мкл/мин из определённого клапана"""

    @check_state_pump
    def refill_volume(self, volume1, speed: float, n1: int):
        self.volume1 = volume1
        v1 = int(volume1 * k1)
        sp1 = int(speed * k2)
        command1 = f'/1I{n1}V{sp1}IA{v1}R' + '\r\n'
        if MAX_STEP >= v1 >= MIN_STEP or MAX_VEL >= sp1 >= MIN_VEL and n1 in range(0, VALVE + 1):
            ser.write(str.encode(command1, encoding='ascii'))
            print(f'Введён объём {volume1} мкл в шприц из {n1}-го клапана\n'
                  f'Скорость: {speed} мкл/мин\n'
                  )
            logging.info(f'Volume input: {volume1} ul, valve: {n1}, velocity: {speed} ul/min.')
        else:
            logging.error(f'Invalid values specified:{volume1} ul, {speed} ul/min, {n1} valve. Read info about acceptable values.\n')
            raise ValueError('Указаны недопустимые параметры, читайте инструкцию.')

    """Добавление объёма к уже установленному из выбранного клапана с заданной скоростью. Используется, если до этого набирался какой-либо объём командой set_volume()"""

    @check_state_pump
    def add_volume(self, Volume1, speed: float, n2: int):
        self.Volume1 = Volume1
        v2 = int(Volume1 * k1)
        sp2 = int(speed * k2)
        command2 = f'/1V{sp2}I{n2}P{v2}R' + '\r\n'
        if MAX_STEP-self.volume1 >= v2 >= MIN_STEP or MAX_VEL >= sp2 >= MIN_VEL or n2 in range(0, VALVE+1):
                print(f'Добавлен объём {Volume1} мкл в шприц с текущим объёмом {self.volume1} мкл из {n2}-го клапана\n'
                      f'Скорость: {speed} мкл/мин\n'
                      f'Конечный объём: {self.volume1+Volume1} мкл')
                ser.write(str.encode(command2, encoding='ascii'))
                logging.info(f'Volume add: {Volume1} ul, valve: {n2}, velocity: {speed} ul/min. Summary volume: {self.volume1+Volume1}')
                self.volume1 += Volume1
        else:
                logging.error(f'Invalid values specified:{Volume1} ul, {speed} ul/min, {n2} valve')
                raise ValueError('Указаны недопустимые параметры либо указан слишком большой объём, читайте инструкцию.')

    """Вывод объёма в мкл c заданной скоростью в выбранный клапан"""

    @check_state_pump
    def infuse_volume(self, volume2, speed: float, n3: int):
        self.volume2 = volume2
        x = self.volume1 - volume2
        v3 = int(x * k1)
        sp3 = int(speed * k2)
        command3 = f'/1V{sp3}O{n3}A{v3}R' + '\r\n'
        if int(self.volume1*k1) >= v3 >= MIN_STEP or MAX_VEL >= sp3 >= MIN_VEL or n3 in range(0, VALVE+1):
                print(f'Выводится объём {volume2} мкл в {n3}-й клапан\n'
                      f'Скорость: {speed} мкл/мин\n'
                      )
                ser.write(str.encode(command3, encoding='ascii'))
                logging.info(f'Volume output: {volume2} ul, valve: {n3}, velocity: {speed} ul/min.')
                self.volume1 = volume2
        else:
                logging.error(f'Invalid values specified:{volume2} ul, {speed} ul/min, {n3} valve')
                raise ValueError('Указаны недопустимые параметры или слишком большой объём, читайте инструкцию.')

"""Объект класса"""

mp = mypump()