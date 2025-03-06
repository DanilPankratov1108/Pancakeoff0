from runze import mypump, ser, write_port
import time
import threading
import config_sy

ser.open()

p = (1.25 * 10 ** -7) / (1.3 * 10 ** -9)
p1 = 6.25

print(f'Привет! Это программа для управления насосом {config_sy.PUMP}. Если есть вопросы по командам - пиши help.')
print(f'Рекомендуется начинать работу с инициализации: init.')

while True:
    
    c = str(input('Введите команду:'))

    if c == 'pull':
        pul = mypump()
        pul.on_off_state()

    elif c == 'off':
        off = mypump()
        off.off()

    elif c == 'pull':
        port_pull()

    elif c == 'check':
        check = mypump()
        check.check()

    elif c == 'open_port':
        start = mypump()
        start.open_port()

    elif c == 'close_port':
        close = mypump()
        close.close_port()

    elif c == 'stop':
        stop = mypump()
        stop.stop()
        while True:
            question = str(input('Хотите ли вы сразу сделать реинициализацию?(да/нет):'))
            if question == 'yes' or question == 'да' or question == 'y':
                write_port('/1ZR')
                break
            elif question == 'no' or question == 'нет' or question == 'n':
                print('Понял')
                break
            else:
                print('Не понял, что это значит')

    elif c == 'info':
        info = mypump()
        info.info()

    elif c == 'init':
        init = mypump()
        init.init()

    elif c == 'valve':
        while True:
            n = int(input('Выберете номер клапана(их всего 12):'))
            if n <= 12 and n > 0:
                valve = mypump()
                valve.valve(number=n)
                print(f'Переключаюсь на клапан {n}')
                break
            else:
                print('Такого номера клапана не существует, выберете другой')

    elif c == 'input':
        while True:
            i = float(input('Укажите объём, который нужно набрать шприцу(в мкл):'))
            print(f'Установлен объём {i} мкл')
            q1 = str(input('Уверены, что хотите продолжить?(да/нет):'))
            if q1 == 'да':
                inp = mypump()
                if i <= config_sy.VOLUME and i >= 0:
                    inp.inp(volume1=int(i * p))
                elif i > config_sy.VOLUME:
                    print(f'Вы выбрали большой объём. Максимальный объём {config_sy.VOLUME} мкл')
                elif i < 0:
                    print('Вы ввели отрицательный объём')
                break
            else:
                print('Распознаю как откат действий')
                break


    elif c == 'output':
        o = float(input('Укажите объём, который нужно выпрыснуть из шприца(в мкл):'))
        print(f'Установлен объём {o} мкл')
        outp = mypump()
        if o <= config_sy.VOLUME and o >= 0:
            outp.outp(volume2=int(o * p))
            print('Если ничего не произошло, вы указали объём, который больше текущего.')
        elif o > config_sy.VOLUME:
            print(f'Вы выбрали большой объём. Максимальный объём {config_sy.VOLUME} мкл')
        elif o < 0:
            print('Вы ввели отрицательный объём')

    elif c == 'inout':
        val1 = int(input('Из какого клапана вы хотите набрать объём(укажите номер):'))
        print(f'Выбран начальный клапан под номером {val1}')
        val2 = int(input('В какой клапан вы хотите подать объём(укажите номер):'))
        print(f'Выбран конечный клапан под номером {val2}')
        v1 = float(input('Укажите объём, который нужно набрать шприцу(в мкл):'))
        print(f'Установлен начальный объём {v1} мкл')
        v2 = float(input('Укажите объём, который нужно выпрыснуть из шприца(в мкл):'))
        print(f'Установлен конечный объём {v2} мкл')
        time1 = int(input(f'Укажите паузу во время одного хода(максимум {config_sy.TIMING} миллисекунд:)'))
        print(f'Пауза: {time1} мс')
        cic1 = int(input('Укажите количество повторов:'))
        print(f'Количество повторов: {cic1}')
        volume = mypump()
        if v1 <= config_sy.VOLUME and v1 >= 0:
            if v2 <= config_sy.VOLUME and v2 >= 0 and v2 <= v1:
                if val1 > 0 and val1 <= 12:
                    if val2 > 0 and val2 <= 12:
                        if time1 in range(0, 30000):
                            if cic1 >= 0:
                                volume.inout(volume=int(v1 * p), Volume=int(v2 * p), c1=cic1, t1=time1, valin1=val1,
                                             valout1=val2)
                            else:
                                print('Указано отрицательное количество повторов')
                        else:
                            print('Указана большая пауза')
                    else:
                        print('Указан несуществующий номер конечного клапана')
                else:
                    print('Указан несуществующий номер начального клапана')
            else:
                print(
                    f'Вы выбрали большой конечный объём либо ввели отрицательное значение. Максимальный объём {config_sy.VOLUME} мкл')
        else:
            print(
                f'Вы выбрали большой начальный объём, либо ввели отрицательное значение, либо конечный объём оказался меньше начального. Максимальный объём {config_sy.VOLUME} мкл')

    elif c == 'velocity':
        vel = float(input('Укажите скорость введения или подачи(мкл в мин):'))
        print(f'Установлена скорость {vel} мкл в мин')
        velocity = mypump()
        if vel <= 960 and vel >= 0:
            velocity.velocity(speed=int(p1 * vel))
        elif vel < 0:
            print('Вы ввели отрицательную скорость')
        elif vel > 1280:
            print('Вы указали очень высокую скорость(максимум: 960 мкл в мин)')

    elif c == 'invelocity':
        x1 = float(input('Укажите объём, который хотите установить в шприце(в мкл):'))
        print(f'Установлен объём {x1} мкл')
        x2 = float(input('Укажите скорость введения или подачи(мкл в мин):'))
        print(f'Установлена скорость {x2} мкл в мин')
        invel = mypump()
        if x2 <= 960 and x2 >= 0:
            if x1 <= config_sy.VOLUME and x1 >= 0:
                invel.invelocity(sp1=int(p1 * x2), vol1=int(x1 * p))
            else:
                print(
                    f'Вы выбрали большой объём либо ввели отрицательное значение. Максимальный объём {config_sy.VOLUME} мкл')
        else:
            print('Вы указали очень высокую скорость(максимум: 960 мкл в мин) либо отрицательную скорость')

    elif c == 'outvelocity':
        x3 = float(input('Укажите объём, который хотите установить в шприце(в мкл):'))
        print(f'Установлен объём {x1} мкл')
        x4 = float(input('Укажите скорость введения или подачи(мкл в мин):'))
        print(f'Установлена скорость {x2} мкл в мин')
        outvel = mypump()
        if x4 <= 960 and x4 >= 0:
            if x3 <= config_sy.VOLUME and x3 >= 0:
                outvel.outvelocity(sp2=int(p1 * x3), vol2=int(x4 * p))
            else:
                print(
                    f'Вы выбрали большой объём либо ввели отрицательное значение. Максимальный объём {config_sy.VOLUME} мкл')
        else:
            print('Вы указали очень высокую скорость(максимум: 1280 мкл в мин) либо отрицательную скорость')

    elif c == 'inoutvelocity':
        val3 = int(input('Из какого клапана вы хотите набрать объём(укажите номер):'))
        print(f'Выбран начальный клапан под номером {val3}')
        val4 = int(input('В какой клапан вы хотите подать объём(укажите номер):'))
        print(f'Выбран конечный клапан под номером {val4}')
        z1 = float(input('Укажите объём, который хотите набрать(в мкл):'))
        print(f'Установлен начальный объём {z1} мкл')
        z2 = float(input('Укажите объём, который хотите оставить в шприце(в мкл):'))
        print(f'Установлен конечный объём {z2} мкл')
        z3 = float(input('Укажите скорость набора в шприц(мкл в мин):'))
        print(f'Установлена начальная скорость {z3} мкл в мин')
        z4 = float(input('Укажите скорость подачи(мкл в мин):'))
        print(f'Установлена конечная скорость {z4} мкл в мин')
        time2 = int(input(f'Укажите паузу во время одного хода(максимум {config_sy.TIMING} миллисекунд:)'))
        print(f'Пауза: {time2} мс')
        cic2 = int(input('Укажите количество повторов:'))
        print(f'Количество повторов: {cic2}')
        inoutvel = mypump()
        if z1 <= config_sy.VOLUME and z1 >= 0:
            if z2 <= config_sy.VOLUME and z2 >= 0 and z2 < z1:
                if z3 <= 960 and z3 >= 0:
                    if z4 <= 960 and z4 >= 0:
                        if val3 > 0 and val3 <= 12:
                            if val4 > 0 and val4 <= 12:
                                if time2 in range(0, 30000):
                                    if cic2 > 0:
                                        inoutvel.inoutvelocity(sp3=int(p1 * z3), vol3=int(z1 * p), vol4=int(z2 * p),
                                                               sp4=int(p1 * z4), valin2=val3, valout2=val4)
                                    else:
                                        print('Указано отрицательное число повторов')
                                else:
                                    print('Указана пауза за пределами допустимых значений')
                            else:
                                print('Указан несуществующий номер конечного клапана')
                        else:
                            print('Указан несуществующий номер начального клапана')
                    else:
                        print(
                            'Вы указали очень высокую скорость подачи(максимум: 960 мкл в мин) либо отрицательную скорость')
                else:
                    print(
                        'Вы указали очень высокую скорость набора(максимум: 960 мкл в мин) либо отрицательную скорость')
            else:
                print(
                    f'Вы выбрали большой начальный объём, либо ввели отрицательное значение, либо конечный объём оказался меньше начального. Максимальный объём {config_sy.VOLUME} мкл')
        else:
            print(
                f'Вы выбрали большой объём либо ввели отрицательное значение. Максимальный объём {config_sy.VOLUME} мкл')

    elif c == 'slope':
        slope1 = float(input('Укажите ускорение:'))
        print(f'Установлено ускорение {slope1}')
        sl = mypump()
        if slope1 <= 20 or slope1 > 0:
            sl.slope(acc=slope1)

    else:
        print('Неизвестная команда')
