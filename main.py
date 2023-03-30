import pickle
import socket
import multiprocessing
from multiprocessing import Manager
import sys


def server():
    print("Сервер запущен")
    vectors = [[6, 8, 9, 67, -7], [6, 9, 0], [1, 2, 3, 4, 0]]
    shared_vectors = Manager().list(vectors)
    num_of_active_clients = Manager().Value('i', 0)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 7000))
    server_socket.listen(1)

    while True:
        client_socket, client_address = server_socket.accept()
        num_of_active_clients.set(num_of_active_clients.get() + 1)
        print("Подключен новый клиент", client_address, "\nАктивных клиентов:", num_of_active_clients.get(), "\n")
        process = multiprocessing.Process(target=child_server, args=(client_socket, client_address,
                                                                     num_of_active_clients, shared_vectors,
                                                                     server_socket))
        process.start()
        client_socket.close()


def child_server(client_socket, client_address, num_of_active_clients, shared_vectors, server_socket):
    server_socket.close()
    print("Это ведомый процесс")
    while True:
        received_message = client_socket.recv(4096)
        if not received_message:
            break
        received_message = pickle.loads(received_message)
        print("Получено сообщение от клиента", num_of_active_clients.get(), client_address, ":", received_message)
        split_data = received_message.split()
        collection_to_send = []
        match(split_data[0]):
            case "view":
                for disk in shared_vectors:
                    collection_to_send.append(disk)
                message_to_send = collection_to_send
            case "add":
                for element in range(1, len(split_data)):
                    collection_to_send.append(int(split_data[element]))
                shared_vectors.append(collection_to_send)
                message_to_send = "Успешно"
            case "edit":
                for element in range(2, len(split_data)):
                    collection_to_send.append(int(split_data[element]))
                shared_vectors[int(split_data[1]) - 1] = collection_to_send
                message_to_send = "Успешно"
            case "delete":
                shared_vectors.pop(int(split_data[1]) - 1)
                message_to_send = "Успешно"
            case "*":
                coefficient = int(split_data[1])
                for i in range(len(shared_vectors)):
                    temp = []
                    for j in range(len(shared_vectors[i])):
                        temp.append(shared_vectors[i][j] * coefficient)
                    shared_vectors[i] = temp
                message_to_send = "Успешно"
            case "/":
                coefficient = int(split_data[1])
                for i in range(len(shared_vectors)):
                    temp = []
                    for j in range(len(shared_vectors[i])):
                        temp.append(shared_vectors[i][j] / coefficient)
                    shared_vectors[i] = temp
                message_to_send = "Успешно"
            case "min":
                for vector in shared_vectors:
                    collection_to_send.append(min(vector))
                message_to_send = collection_to_send
            case "max":
                for vector in shared_vectors:
                    collection_to_send.append(max(vector))
                message_to_send = collection_to_send
            case "asc":
                for i in range(len(shared_vectors)):
                    shared_vectors[i] = sorted(shared_vectors[i])
                message_to_send = "Успешно"
            case "desc":
                for i in range(len(shared_vectors)):
                    shared_vectors[i] = sorted(shared_vectors[i], reverse=True)
                message_to_send = "Успешно"
            case "sum":
                index_vector_1 = int(split_data[1]) - 1
                index_vector_2 = int(split_data[2]) - 1
                length_of_vectors = len(shared_vectors)
                if index_vector_1 in range(length_of_vectors) or index_vector_2 in range(length_of_vectors):
                    if len(shared_vectors[index_vector_1]) == len(shared_vectors[index_vector_2]):
                        for i in range(len(shared_vectors[index_vector_1])):
                            collection_to_send.append(shared_vectors[index_vector_1][i] + shared_vectors[index_vector_2][i])
                        message_to_send = collection_to_send
                    else:
                        message_to_send = "Длина векторов не совпадает!"
                else:
                    message_to_send = "Таких элементов не существует!"
            case "dif":
                index_vector_1 = int(split_data[1]) - 1
                index_vector_2 = int(split_data[2]) - 1
                length_of_vectors = len(shared_vectors)
                if index_vector_1 in range(length_of_vectors) or index_vector_2 in range(length_of_vectors):
                    if len(shared_vectors[index_vector_1]) == len(shared_vectors[index_vector_2]):
                        for i in range(len(shared_vectors[index_vector_1])):
                            collection_to_send.append(shared_vectors[index_vector_1][i] - shared_vectors[index_vector_2][i])
                        message_to_send = collection_to_send
                    else:
                        message_to_send = "Длина векторов не совпадает!"
                else:
                    message_to_send = "Таких элементов не существует!"
            case _:
                message_to_send = "Ошибка"
        print("Сервер отправил сообщение:", message_to_send, "\n")
        client_socket.sendall(pickle.dumps(message_to_send))
    print("Клиент", client_address, "отключился")
    client_socket.close()
    num_of_active_clients.set(num_of_active_clients.get() - 1)
    print("Активных клиентов:", num_of_active_clients.get(), "\n")
    sys.exit(0)


if __name__ == '__main__':
    server()
