from port import write_port, ser

ser.open()

t = ""

while True:
    c = str(input()) + '\r\n'
    if c:
        t += c + " "
        write_port(c)        
    else:
        print('Неизвестная команда')
        break

ser.close()