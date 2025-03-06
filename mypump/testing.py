import signal
from signal import SIGALRM, SIGABRT

def handler(signum, frame):
    raise TimeoutError("Execution time limit exceeded")

def limited_execution_time(func, time_limit):
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(time_limit)
    try:
        result = func()
    except TimeoutError:
        result = None
    finally:
        signal.alarm(0)
    return result

def my_function():
    print("Hello world!")
    pass

result = limited_execution_time(my_function, 5) # Устанавливаем время ожидания в 5 секунд
if result is None:
    print("Функция превысила ограничение времени выполнения")
else:
    print("Результат выполнения функции:", result)