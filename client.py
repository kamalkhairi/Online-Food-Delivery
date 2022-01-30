import socket
import json
import sys
import os
from datetime import date


SERVER = "192.168.56.101"
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#connect to server socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#this function is the interface that allow user to login or create new account
def login():
     repeat = True
     while repeat:   
        print("\n1. Already Registered")
        print("2. New User")
        login = input("Please select 1 or 2: ")
        if login == "1":
            username, password = None, None
            while not username or not password:
                username = input('\nEnter username: ')
                password = input('Enter password: ')
            loginList = ["1",username,password]
            status = loginsend_recv(loginList)
            if status[0] == "yes":
                if status[1] == 2:
                    userInterface(username)
                    repeat = False
                elif status[1] == 1:
                    adminInterface(username)
                    repeat = False

        elif login == "2":
            username, password, address = None, None, None
            while not username or not password or not address:
                username = input('\nEnter username: ')
                password = input('Enter password: ')
                address = input('Enter address: ')
                username = username.strip()
                password = password.strip()
                address = address.strip()
            loginList = ["2",username,password,address]
            createsend_recv(loginList)

#this function will send the login information to the server and wait for server authentication.
def loginsend_recv(lists):
    lists = json.dumps(lists)
    client.sendall(bytes(lists,encoding="utf-8"))
    receive_msg = client.recv(10000).decode(FORMAT)
    status = None
    if receive_msg:
        receive_msg = json.loads(receive_msg)
        if receive_msg[0] == "yes":
            print("\nSuccessfully Logged In\n")
            status = receive_msg
            return status
        else:
            print("\nWrong Username or Password\n")
            status = receive_msg
            return status
    else:
        print("\n[SERVER] SERVER DOWN\n")
        status = "no"
        return status
