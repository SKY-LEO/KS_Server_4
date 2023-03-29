import os
import pickle
import socket
from multiprocessing import shared_memory, Array, Manager
import sys
import multiprocessing


def server():
    vectors = [[6, 8, 9, 67, -7], [6, 9, 0], [1, 2, 3, 4, 0]]
    shared_vectors = Manager().list(vectors)
    a = Manager().Value('i', 0)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 7000))  # Привязываем серверный сокет к localhost и 3030 порту.
    backlog = 10  # Размер очереди входящих подключений, т.н. backlog
    s.listen(backlog)

    while True:
        conn, addr = s.accept()  # Метод, который принимает входящее соединение.
        # a[0] = a[0] + 1
        a.set(a.get() + 1)
        print("активных клиентов:", a.get())
        proc = multiprocessing.Process(target=child_server, args=(conn, addr, a, shared_vectors, s))
        proc.start()
        # pid = os.fork()
        # if pid == 0:
        # s.close()
        # child_server(conn, addr, a, shared_vectors)
        # sys.exit(0)
        # else:
        conn.close()


def child_server(conn, addr, b, shared_vectors, s):
    s.close()
    message = ""
    # b = shared_memory.ShareableList(name=share_name)
    print("Это ведомый поток")
    print("Создано соединение между сервером и клиентом")
    while True:
        data = conn.recv(10000)  # Получаем данные из сокета.
        if not data:
            break
        data = pickle.loads(data)
        print("Получено сообщение от клиента", b.get(), addr, ":", data)
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
            shared_vectors.pop(int(split_data[1]) - 1)
            message = "Успешно"
        elif split_data[0] == "*":
            coefficient = int(split_data[1])
            for i in range(len(shared_vectors)):
                temp = []
                for j in range(len(shared_vectors[i])):
                    temp.append(shared_vectors[i][j] * coefficient)
                shared_vectors[i] = temp
            message = "Успешно"
        elif split_data[0] == "/":
            coefficient = int(split_data[1])
            for i in range(len(shared_vectors)):
                temp = []
                for j in range(len(shared_vectors[i])):
                    temp.append(shared_vectors[i][j] / coefficient)
                shared_vectors[i] = temp
            message = "Успешно"
        elif split_data[0] == "min":
            for vector in shared_vectors:
                collection_to_send.append(min(vector))
            message = collection_to_send
        elif split_data[0] == "max":
            for vector in shared_vectors:
                collection_to_send.append(max(vector))
            message = collection_to_send
        elif split_data[0] == "asc":
            for i in range(len(shared_vectors)):
                shared_vectors[i] = sorted(shared_vectors[i])
            message = "Успешно"
        elif split_data[0] == "desc":
            for i in range(len(shared_vectors)):
                shared_vectors[i] = sorted(shared_vectors[i], reverse=True)
            message = "Успешно"
        elif split_data[0] == "sum":
            index_vector_1 = int(split_data[1]) - 1
            index_vector_2 = int(split_data[2]) - 1
            length_of_vectors = len(shared_vectors)
            if index_vector_1 in range(length_of_vectors) or index_vector_2 in range(length_of_vectors):
                if len(shared_vectors[index_vector_1]) == len(shared_vectors[index_vector_2]):
                    for i in range(len(shared_vectors[index_vector_1])):
                        collection_to_send.append(shared_vectors[index_vector_1][i] + shared_vectors[index_vector_2][i])
                    message = collection_to_send
                else:
                    message = "Длина векторов не совпадает!"
            else:
                message = "Таких элементов не существует!"
        elif split_data[0] == "dif":
            index_vector_1 = int(split_data[1]) - 1
            index_vector_2 = int(split_data[2]) - 1
            length_of_vectors = len(shared_vectors)
            if index_vector_1 in range(length_of_vectors) or index_vector_2 in range(length_of_vectors):
                if len(shared_vectors[index_vector_1]) == len(shared_vectors[index_vector_2]):
                    for i in range(len(shared_vectors[index_vector_1])):
                        collection_to_send.append(shared_vectors[index_vector_1][i] - shared_vectors[index_vector_2][i])
                    message = collection_to_send
                else:
                    message = "Длина векторов не совпадает!"
            else:
                message = "Таких элементов не существует!"
        print("Сервер отправил сообщение", message)
        conn.sendall(pickle.dumps(message))  # Отправляем данные в сокет.
    print("Клиент", b.get(), "отключился")
    conn.close()
    b.set(b.get() - 1)
    print("Активных клиентов:", b.get())
    sys.exit(0)


if __name__ == '__main__':
    server()
