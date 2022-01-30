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

#this server will send new account information to the server and wait for server authentication
def createsend_recv(lists):
    lists = json.dumps(lists)
    client.sendall(bytes(lists,encoding="utf-8"))
    receive_msg = client.recv(10000).decode(FORMAT)
    if receive_msg:
        if receive_msg == "yes":
            print("\nAccount Created Successfully\n")
        else:
            print("\nAccount with That Username Already Registered!\n")
    else:
        print("\n[SERVER] SERVER DOWN\n")


#this function is for user interface where customer can select which operation they want to use
def userInterface(username):
    repeat = True
    while repeat:
        print("\nUSER INTERFACE")
        print("\n1. Order Menu")
        print("2. Order History")
        print("3. Change Delivery Address")
        print("\nPress CTRL + C To Exit The Program\n")
        interface = input("Please Select: ")
        if interface == "1":
            message = ["menu", username]
            message = json.dumps(message)
            client.sendall(bytes(message,encoding="utf-8"))
            receive_msg = client.recv(10000).decode(FORMAT)
            if receive_msg:
                receive_msg = json.loads(receive_msg)
                menu(receive_msg)
            else:
                print("\n[SERVER] SERVER DOWN\n")
        elif interface == "2":
            message = ["history", username]
            message = json.dumps(message)
            client.sendall(bytes(message,encoding="utf-8"))
            receive_msg = client.recv(10000).decode(FORMAT)
            if receive_msg:
                receive_msg = json.loads(receive_msg)
                history(receive_msg)
            else:
                print("\n[SERVER] SERVER DOWN\n")
        elif interface == "3":
            message = ["change", username]
            message = json.dumps(message)
            client.sendall(bytes(message,encoding="utf-8"))
            changeAddress()

#this function is for admin interface where admin can choose what operation they want to do
def adminInterface(username):
    repeat = True
    while repeat:
        print("\nADMIN INTERFACE")
        print("\n1. Add New Menu")
        print("2. Customer Order History")
        print("3. Sales of The Day")
        print("\nPress CTRL + C To Exit The Program\n")
        interface = input("Please Select: ")
        if interface == "1":
            message = ["add", username]
            message = json.dumps(message)
            client.sendall(bytes(message,encoding="utf-8"))
            addMenu()
        
        elif interface == "2":
            message = ["customer", username]
            message = json.dumps(message)
            client.sendall(bytes(message,encoding="utf-8"))
            receive_msg = client.recv(5000).decode(FORMAT)
            if receive_msg:
                receive_msg = json.loads(receive_msg)
                customerHistory(receive_msg)
            else:
                print("\n[SERVER] SERVER DOWN\n")

        elif interface == "3":
            message = ["sales", username]
            message = json.dumps(message)
            client.sendall(bytes(message,encoding="utf-8"))
            receive_msg = client.recv(10000).decode(FORMAT)
            if receive_msg:
                receive_msg = json.loads(receive_msg)
                salesDay(receive_msg)
            else:
                print("\n[SERVER] SERVER DOWN\n")
