import os
import socket
from multiprocessing import shared_memory, Array
import sys

words = ("нуль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять")


def server():
    vectors = [0, [6, 8, 9, 67, -7], [6, 9, 0], [1, 2, 3, 4, 0]]
    arr = Array('i', (1, 2))

    a = shared_memory.ShareableList(arr)
    #aa = shared_memory.ShareableList(xxx)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 4000))  # Привязываем серверный сокет к localhost и 3030 порту.
    backlog = 10  # Размер очереди входящих подключений, т.н. backlog
    s.listen(backlog)

    while True:
        conn, addr = s.accept()  # Метод, который принимает входящее соединение.
        a[0] = a[0] + 1
        print("активных клиентов:", a[0])
        pid = os.fork()
        if pid == 0:
            s.close()
            child_server(conn, addr, a.shm.name)
        else:
            conn.close()


def child_server(conn, addr, share_name):
    message = ""
    b = shared_memory.ShareableList(name=share_name)
    b[3] = 4
    print("Это ведомый поток")
    print("Создано соединение между сервером и клиентом")
    while True:
        data = conn.recv(1024)  # Получаем данные из сокета.
        if not data:
            break
        data = data.decode('utf-8')
        print("Получено сообщение от клиента", b[0], addr, ":", data)
        split_data = data.split()
        if split_data == "view":
            message = b[1]
            conn.sendall(message)
        if data.isdigit() is False:
            print("Получены не цифры!")
        else:
            data = int(data)
            if data == -1:
                print("Получен запрос на уничтожение связи")
                break
            if -1 < data < len(words):
                message = words[data].encode('utf-8')
                conn.sendall(message)  # Отправляем данные в сокет.
                print("Сервер отправил сообщение", words[data])
    print("Клиент отключился")
    conn.close()
    b[0] = b[0] - 1
    print("Активных клиентов:", b[0])
    b.shm.close()
    sys.exit(0)


if __name__ == '__main__':
    server()
