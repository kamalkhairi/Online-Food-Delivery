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

#this function is the interface for the customer to see all of their menu and allow them to select the menu
def menu(receive_msg):
    print("\nWELCOME TO OUR RESTAURANT\n")
    a = 0
    y = 1
    for x in range(len(receive_msg)):
        print (f"{y}. {receive_msg[x][a]}, RM: {receive_msg[x][a+1]}")
        y = y+1

    order = []
    add = True
    while add:
        menu, quantity = None, None
        select = True  
        while select:
            repeat1 = True
            while repeat1:
                menu = input("\nPlease select menu: ")
                if menu.isnumeric() == True:
                    repeat1 = False
            menu=int(menu)
            for z in range(1, y):
                if(menu == z):
                    select = False
        repeat2 = True
        while repeat2:
            quantity = input("Quantity: ")
            if quantity.isnumeric() == True:
                if int(quantity) > 0:
                    repeat2 = False  
        quantity = int(quantity)          
        orderList = [menu, quantity]   
        order.extend(orderList)
        add = input("\nAdd More Order? y/n: ")
        if add == 'n' or add == 'N':
            add = False
        else:
            add = True
    lists = json.dumps(order)
    client.sendall(bytes(lists,encoding="utf-8"))

    result = client.recv(10000).decode(FORMAT)
    if result:
        result = json.loads(result)
        print(f"\n[SERVER] Total Price: RM{result[0]}")
        print(f"[SERVER] We Only Accept Cash On Delivery via Our Delivery Rider")
        print(f"[SERVER] We Will Sent Your Order Shortly at {result[1]}\n")

    else:
        print("\n[SERVER] SERVER DOWN\n")


#this function is the interface for customer to see their order history
def history(receive_msg):
    print("\nORDER HISTORY\n")
    z = 0
    y = 1
    for x in range(len(receive_msg)):
        print (f"{y}. {receive_msg[x][z]}, Quantity: {receive_msg[x][z+1]}, RM: {receive_msg[x][z+2]}, {receive_msg[x][z+3]} ")
        y = y+1

#this function is the interface for customer to change their delivery address
def changeAddress():
    print("\nCHANGE DELIVERY ADDRESS\n")
    repeat = True
    while repeat:
        address = input("New Address: ")
        if address:
            repeat = False
        else:
            repeat = True
    address = address.strip()
    lists = [address] 
    lists = json.dumps(address)
    client.sendall(bytes(lists,encoding="utf-8"))
    receive_msg = client.recv(10000).decode(FORMAT)
    if receive_msg:
        receive_msg = json.loads(receive_msg)
        print(receive_msg[0])
    else:
        print("\n[SERVER] SERVER DOWN\n")
