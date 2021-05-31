import RPi.GPIO as io


def rain():
    pin = 23

    io.setmode(io.BCM)
    io.setup(pin, io.IN)  # устанавливаем пин на вход


    signal = io.input(pin)  # считываем сигнал
    if signal == 1:
        pass
        #print("датчик сухой")
    elif signal == 0:
        print("на датчике обнаружена вода!")
    else:
        print("ошибка!")
    return signal
