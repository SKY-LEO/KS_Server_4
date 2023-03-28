import os
import pickle
import socket
from multiprocessing import shared_memory, Array, Manager
import sys

words = ("нуль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять")


def server():
    vectors = [[6, 8, 9, 67, -7], [6, 9, 0], [1, 2, 3, 4, 0]]
    shared_vectors = Manager().list(vectors)
    a = shared_memory.ShareableList([0, ])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 7000))  # Привязываем серверный сокет к localhost и 3030 порту.
    backlog = 10  # Размер очереди входящих подключений, т.н. backlog
    s.listen(backlog)

    while True:
        conn, addr = s.accept()  # Метод, который принимает входящее соединение.
        a[0] = a[0] + 1
        print("активных клиентов:", a[0])
        pid = os.fork()
        if pid == 0:
            s.close()
            child_server(conn, addr, a.shm.name, shared_vectors)
        else:
            conn.close()
            print(shared_vectors)


def child_server(conn, addr, share_name, shared_vectors):
    message = ""
    b = shared_memory.ShareableList(name=share_name)
    print("Это ведомый поток")
    print("Создано соединение между сервером и клиентом")
    while True:
        data = conn.recv(10000)  # Получаем данные из сокета.
        if not data:
            break
        data = pickle.loads(data)
        print("Получено сообщение от клиента", b[0], addr, ":", data)
        split_data = data.split()
        collection_to_send = []
        if data == "view":
            for disk in shared_vectors:
                collection_to_send.append(disk)
            message = collection_to_send
        elif split_data[0] == "add":
            for element in range(1, len(split_data)):
                collection_to_send.append(int(split_data[element]))
            shared_vectors.append(collection_to_send)
            message = "Успешно"
        elif split_data[0] == "edit":
            for element in range(2, len(split_data)):
                collection_to_send.append(int(split_data[element]))
            shared_vectors[int(split_data[1]) - 1] = collection_to_send
            message = "Успешно"
        elif split_data[0] == "delete":
            shared_vectors.pop(int(split_data[1]))
            message = "Успешно"
        elif split_data[0] == "*":
            coefficient = int(split_data[1])
            print(coefficient)
            for vector in shared_vectors:
                temp = []
                for el in vector:
                    temp.append(el * coefficient)
                collection_to_send.append(temp)
            message = "Успешно"
            shared_vectors = collection_to_send
        print("Сервер отправил сообщение", message)
        conn.sendall(pickle.dumps(message))  # Отправляем данные в сокет.
    print("Клиент", b[0], "отключился")
    conn.close()
    b[0] = b[0] - 1
    print("Активных клиентов:", b[0])
    b.shm.close()
    sys.exit()


if __name__ == '__main__':
    server()
