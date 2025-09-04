
import sys
import time
import threading
from threading import Thread
import serial
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
import serial.tools.list_ports
import logging
import keyboard as kb

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

target_manufacturer = 'wch.cn'
target_hwid = 'USB VID:PID=1A86:7523 SER= LOCATION=1-2'

def find_port(target_vid, target_pid):
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        device_info = port.hwid
        if f"{target_vid}" in device_info and f"{target_pid}" in device_info:
            return port.device
    return None

target_pid = "1A86"
target_vid = "7523"

com_port = find_port(target_vid, target_pid)

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

"""Битовые строки, которые идут от насоса"""

state_work = b'\xff/0@\x03\r\n'     #В процессе работы
state_free = b'\xff/0`\x03\r\n'     #Свободен

"""Строки ошибок"""

init_error = b'\xff/0a\x03\r\n'     #Ошибка инициализации
invalid_param = b'\xff/0c\x03\r\n'   #Недопустимые параметры
# EEPROM_failure = b'\xff/0f\x03\r\n'     #Проблемы с EEPROM
not_init = b'\xff/0g\x03\r\n'   #Попытка начать работу без инициализации
internal_failure = [b'\xff/0h\x03\r\n', b'\xff/0l\x03\r\n']  #Внутренний сбой
plunger_overload = b'\xff/0i\x03\r\n'   #Перегрузка поршня
valve_overload = b'\xff/0j\x03\r\n'     #Перегрузка клапана
plunger_move = b'\xff/0k\x03\r\n'   #Движение поршня ограниченно
AD_failure = b'\xff/0n\x03\r\n'     #Неисправность аналого-цифрового преобразователя
# command_overflow = b'\xff/0O\x03\r\n'   #Переполнена очередь команд

"""Некоторые команды в ASCII"""

state = '/1QR' + '\r\n' #для проверки состояния
stop = '/1TR' + '\r\n'  #для экстренной остановки
report = '/1?R' + '\r\n'    #запрашивает текущий объём

"""Декоратор, который навешиваетя на некоторые функции в библиотеке. Он позволяет определять состояние выполнения функций насоса."""

def check_state_pump(func):
    def wrapper(*args, **kwargs):
                stop_thread = threading.Thread(target=args[0].stop_device, daemon = True)
                stop_thread.start()
                ser.write(str.encode(state, encoding='ascii'))
                N = ser.read(7)
                while N == state_work and not mypump.terminate:
                    ser.write(str.encode(state, encoding='ascii'))
                    N = ser.read_until(expected = state_work)
                if N == plunger_overload or N == valve_overload:
                    logging.error('Overload of plunger or valve')
                    raise Warning('Перегрузка поршня или клапанов. Рекомендуется сделать инициализацию')
                elif N in internal_failure:
                    logging.error('Internal failure of device.')
                    raise Warning('Внутренний сбой устройства. Рекомендуется обратиться к производителям')
                elif N == AD_failure:
                    logging.error('A/D converter failure.')
                    raise Warning('Неисправность A/D-преобразователя.')
                if mypump.terminate:
                    raise Warning('Остановка. Нажата клавиша t')
                return func(*args, **kwargs)
    return wrapper

"""Библиотека функций по управлению насосами Runze Fluid"""

class mypump:

    """Чем оборудован насос?"""

    PUMP = 'SY-01B'  # модель насоса Runze Fluid
    HEAD = 'M12'  # головка в насосе
    VALVE = 12  # число клапанов в головке

    """Важные константы"""

    """1)В единицах кода(в шагах)"""

    NOM_STEP = 6000  # номинальный ход
    MAX_STEP = 12000  # максимальный ход
    MIN_STEP = 1  # минимальный ход
    MAX_VEL = 6000  # максимальная скорость
    MIN_VEL = 1  # минимальная скорость
    DEFAULT_VEL = 4000  # скорость по умолчанию

    """2)В абсолютных единицах(мкл и мкл/мин) для шприца 125 мкл"""

    REAL_NOM_STEP_1 = 62.5  # номинальный ход
    REAL_MAX_STEP_1 = 125  # максимальный ход
    REAL_MIN_STEP_1 = 1 / 96  # минимальный ход
    REAL_MAX_VEL_1 = 3750  # максимальная скорость
    REAL_MIN_VEL_1 = 1.6  # минимальная скорость
    REAL_DEFAULT_VEL_1 = 2500  # скорость по умолчанию

    """3)В абсолютных единицах(мкл и мкл/мин) для шприца 500 мкл"""

    REAL_NOM_STEP_2 = 250  # номинальный ход
    REAL_MAX_STEP_2 = 500  # максимальный ход
    REAL_MIN_STEP_2 = 1 / 24  # минимальный ход
    REAL_MAX_VEL_2 = 3750  # максимальная скорость
    REAL_MIN_VEL_2 = 1.6  # минимальная скорость
    REAL_DEFAULT_VEL_2 = 2500  # скорость по умолчанию

    terminate = False   #Флаг остановки насоса

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

    """Остановка клавишей t"""

    def stop_device(self):
            kb.wait('t')
            global terminate
            ser.write(str.encode(stop, encoding='ascii'))
            print('Остановка. Рекомендуется сделать реинициализацию')
            logging.info('Stopping with /1TR command. It is recommended to do initialization.')
            terminate = True

    """Это остановка командой stop"""

    def stop(self):
        ser.write(str.encode(stop, encoding='ascii'))
        self.running = False
        print('Остановка. Рекомендуется сделать реинициализацию')
        logging.info('Stopping with /1TR command. It is recommended to do initialization.')

    """Тайм слип в минутах"""

    @check_state_pump
    def pause(self, T: float):
        t = T * 60
        print(f'Пауза {T} мин')
        time.sleep(t)

    """Установка максимального объёма"""
    def set_volume(self, V):
        if V == 125 or V == 500:
            k1 = mypump.MAX_STEP / V  # Перевод объёма из мкл в шаги
            k2 = k1 / 60    # Перевод скорости из мкл/мин в шаги/сек
            self.k1 = k1
            self.k2 = k2
            print(f'Вы установили объём шприца {V} мкл')
            logging.info(f'Max syringe volume set: {V} ul')
        else:
            raise ValueError('Шприцов с таким объёмом не существует')

    """Инициализация"""

    @check_state_pump
    def init(self):
            init = str('/1ZR') + '\r\n'
            ser.write(str.encode(init, encoding = 'ascii'))
            I = ser.read(7)
            if I == init_error:
                raise Exception('Ошибка инициализации. Попробуйте повторить попытку')
            else:
                print('Инициализация')
                logging.info('Initialization.')


    """Всасывание объёма в мкл в шприц с заданной скоростью в мкл/мин из определённого клапана"""

    @check_state_pump
    def refill(self, Volume1, speed: float, n2: int):
        v2 = int(Volume1 * self.k1)
        sp2 = int(speed * self.k2)
        command2 = f'/1V{sp2}I{n2}P{v2}R' + '\r\n'
        ser.write(str.encode(command2, encoding='ascii'))
        I = ser.read(7)
        if I == not_init:
            raise Warning('Попытка начать работу без инициализации.')
        elif I == invalid_param:
            logging.error(
                f'Invalid value(-s) specified:{Volume1} ul, {speed} ul/min, {n2} valve. Read info about acceptable values.\n')
            raise ValueError('Указаны недопустимые параметры, читайте инструкцию.')
        elif I == plunger_move:
            raise ValueError('Движение поршня невозможно из-за ограничений по объёму.')
        print(f'Добавлен объём {Volume1} мкл в шприц из {n2}-го клапана\n'
              f'Скорость: {speed} мкл/мин\n')
        logging.info(f'The volume {Volume1} ul was added, valve: {n2}, velocity: {speed} ul/min.')
        self.report_volume()

    """Вывод объёма в мкл c заданной скоростью в выбранный клапан"""

    @check_state_pump
    def infuse(self, volume2, speed: float, n3: int):
        v3 = int(volume2 * self.k1)
        sp3 = int(speed * self.k2)
        command3 = f'/1V{sp3}O{n3}D{v3}R' + '\r\n'
        ser.write(str.encode(command3, encoding='ascii'))
        I = ser.read(7)
        if I == not_init:
            raise Warning('Попытка начать работу без инициализации.')
        elif I == invalid_param:
            logging.error(f'Invalid value(-s) specified:{volume2} ul, {speed} ul/min, {n3} valve')
            raise ValueError('Указаны недопустимые параметры. читайте инструкцию.')
        elif I == plunger_move:
            raise ValueError('Движение поршня невозможно из-за ограничений по объёму.')
        print(f'Выводится объём {volume2} мкл в {n3}-й клапан\n'
              f'Скорость: {speed} мкл/мин\n'
              )
        logging.info(f'The {volume2} ul was infused, valve: {n3}, velocity: {speed} ul/min.')
        self.report_volume()

    """Функция для вывода текущего объёма в шприце"""

    @check_state_pump
    def report_volume(self):
        ser.write(str.encode(report, encoding='ascii'))
        R = ser.read(12)
        start_index = R.index(b'`') + 1
        end_index = R.index(b'\x03')
        number_bytes = R[start_index:end_index]
        number_str = number_bytes.decode('utf-8')
        number = int(number_str)
        final_volume = number / self.k1
        print(f"Текущий объём в шприце: {final_volume} мкл\n")
        logging.info(f'Report command was send. There is {final_volume} ul in the syringe.')
        ser.send_break(2)

    """Функция для смены шприца"""

    @check_state_pump
    def change_syringe(self):
        change = f'/1V4000A12000R' + '\r\n'
        ser.write(str.encode(change, encoding = 'ascii'))
        r = ser.read(7)
        if r == not_init:
            raise Warning('Попытка начать работу без инициализации.')
        else:
            print('Замените шприц')
            logging.info('Сommand was entered to replace syringe.')

if __name__ == "__main__":
    mypump = mypump()
