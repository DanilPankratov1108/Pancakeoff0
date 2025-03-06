import config_sy
import sys
import time
import serial
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
import serial.tools.list_ports
import config_sy
import logging
import queue
import threading

"""Логирование"""

logging.basicConfig(level=logging.INFO, filename="runze_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

"""Настройки порта"""

baudrate = 9600
stopbits = STOPBITS_ONE
timeout = 1
bytesize = EIGHTBITS
parity = PARITY_NONE

try:
    ports = serial.tools.list_ports.comports()
    port = next((p.device for p in ports), None)
    if port is None:
        raise ValueError("No COM port found.")

    ser = serial.Serial(port,
                        baudrate=baudrate,
                        timeout=1,
                        stopbits=stopbits,
                        parity=parity,
                        bytesize=bytesize
                        )

except ValueError as ve:
    print("Error:", str(ve))

except serial.SerialException as se:
    print("Serial port error:", str(se))

except Exception as e:
    print("An error occurred:", str(e))

"""Чем оборудован насос?"""

PUMP = 'SY-01B'     # модель насоса Runze Fluid
HEAD = 'M12'        # головка в насосе
VALVE = 12          # число клапанов в головке
VOLUME = 125        # объём в мкл
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

REAL_NOM_STEP = 30
REAL_MAX_STEP = 125         # максимальный ход
REAL_MIN_STEP = 1/200       # минимальный ход
REAL_MAX_VEL = 960          # максимальная скорость
REAL_MIN_VEL = 6.25         # минимальная скорость
REAL_DEFAULT_VEL = 640      # скорость по умолчанию

"""Коэффициенты перевода"""
k1 = (1.25 * 10 ** -7) / (1.3 * 10 ** -9)       # Перевод объёма из мкл в шаги
k2 = 6.25                                       # Перевод скорости из мкл/мин в шаги/сек

"""Состояния"""
state_work = b'\xff/0@\x03\r\n'
state_free = b'\xff/0`\x03\r\n'
state = '/1QR' + '\r\n'

"""Декоратор, который мы навешиваем на каждую функцию в библиотеке, и он проверяет состояние выполнения команд"""

"""""
def check_state_pump(func):
            try:
                ser.write(str.encode(state, encoding='ascii'))
                if ser.read() == state_work:
                    func()
            except serial.SerialException as e:
                logging.error(f"Error writing on {ser.port}.\nErr: {e}")
            return func
"""""


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

    """Остановка выполнения команды"""

    def stop():
        stoop = '/1TR' + '\r\n'
        ser.write(str.encode(stoop, encoding='ascii'))
        print('Остановка. Рекомендуется сделать реинициализацию')
        logging.info('Stopping with /1TR command')

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

    def pause(T: float):
        t = T * 60
        print(f'Пауза {T} мин')
        time.sleep(t)

    """Инициализация"""

    #@check_state_pump
    def init():
        i = b''
        try:
            i = ser.read_until(expected=state_work)
            while i == state_work:
                ser.write(str.encode(state, encoding='ascii'))
                i = ser.read_until(expected=state_work)
            print('Инициализация')
            logging.info('Initialization.')
            init = str('/1ZR') + '\r\n'
            ser.write(str.encode(init, encoding = 'ascii'))
        except serial.SerialException as se:
            print(f"Error write to {port}", str(se))
            logging.warning('Error of initialization.')

    """Ввод объёма в мкл с заданной скоростью в мкл/мин из определённого клапана"""

    #@check_state_pump
    def set_volume(volume1, speed: float, n1: int):
        s = b''
        v1 = int(volume1 * k1)
        sp1 = int(speed * k2)
        try:
            s = ser.read_until(expected=state_work)
            while s == state_work:
                ser.write(str.encode(state, encoding='ascii'))
                s = ser.read_until(expected=state_work)
            if (MAX_STEP >= v1 >= MIN_STEP) or (MAX_VEL >= sp1 >= MIN_VEL) or (n1 in range(0, VALVE+1)):
                        print(f'Введён объём {volume1} мкл из {n1}-ого клапана\n'
                              f'Скорость: {speed} мкл/мин\n'
                              )
                        command1 = f'/1I{n1}V{sp1}IA{v1}R' + '\r\n'
                        ser.write(str.encode(command1, encoding ='ascii'))
                        logging.info(f'Volume input: {volume1} mkl, valve: {n1}, velocity: {speed} mkl/min.')
            else:
                print(f'Указаны недопустимые параметры, читайте инструкцию.')
                logging.warning(f'Invalid values specified:{volume1} mcl, {speed} mcl/min, {n1} valve. Read info about acceptable values.\n')
        except serial.SerialException as se:
            print(f"Error write to {port}", str(se))
            logging.warning('Error of initialization.')
    """Добавление объёма к уже установленному из выбранного клапана с заданной скоростью"""

    #@check_state_pump
    def add_volume(Volume1, speed: float, n2: int):
        v2 = int(Volume1 * k1)
        sp2 = int(speed * k2)
        if (MAX_STEP >= v2 >= MIN_STEP) or (MAX_VEL >= sp2 >= MIN_VEL) or (n2 in range(0, VALVE+1)):
            print(f'Введён объём {Volume1} мкл\n'
                  f'Скорость: {speed} мкл/мин\n'
                  )
            command2 = f'/1V{sp2}I{n2}P{v2}R' + '\r\n'
            ser.write(str.encode(command2, encoding='ascii'))
        else:
            print(f'Указаны недопустимые параметры, читайте инструкцию.')
            logging.warning(f'Invalid values specified:{Volume1} mcl, {speed} mcl/min, {n2} valve')

    """Вывод объёма в мкл c заднной скоростью в выбранный клапан"""

    #@check_state_pump
    def output_volume(volume2, speed: float, n3: int):
        o = b''
        o += ser.readline()
        v3 = int(volume2 * k1)
        sp3 = int(speed * k2)
        if (MAX_STEP >= v3 >= MIN_STEP) or (MAX_VEL >= sp3 >= MIN_VEL) or (n3 in range(0, VALVE+1)):
            print(f'Введён объём {volume2} мкл\n'
                  f'Скорость: {speed} мкл/мин\n'
                  )
            command3 = f'/1V{sp3}O{n3}A{v3}R' + '\r\n'
            ser.write(str.encode(command3, encoding='ascii'))
        else:
            print(f'Указаны недопустимые параметры, читайте инструкцию.')
            logging.warning(f'Invalid values specified:{volume2} mcl, {speed} mcl/min, {n3} valve')