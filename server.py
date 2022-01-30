import socket
import json
import sys
import os
import threading
from datetime import date
import mysql.connector

#connect to database
database = mysql.connector.connect(user='user',
                               host='localhost',
                               password ='user12345')

mycursor = database.cursor()
#create database
mycursor.execute("CREATE DATABASE IF NOT EXISTS project;")
database = mysql.connector.connect(user='user',
                               host='localhost',
                               password ='user12345',
                               database ='project')
mycursor = database.cursor(buffered=True)
#create table user
mycursor.execute("CREATE TABLE IF NOT EXISTS user (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, username VARCHAR(20), password VARCHAR(20), address VARCHAR(70), role INT);")
admin = """iNSERT INTO user (username,password,address,role)
        SELECT * FROM (SELECT 'admin' AS username, 'admin123' AS password, NULL AS address, 1 AS role) AS temp
        WHERE NOT EXISTS (
        SELECT username FROM user WHERE username = 'admin'
        ) LIMIT 1;"""
mycursor.execute(admin)
database.commit()

#create table menu
mycursor.execute("CREATE TABLE IF NOT EXISTS menu (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, menu_name VARCHAR(50), price VARCHAR(20));")
for x in range(3):
    if x == 0:
        sql = """iNSERT INTO menu (menu_name,price)
        SELECT * FROM (SELECT 'Nasi Goreng' AS menu_name, '5.00' AS price) AS temp
        WHERE NOT EXISTS (
        SELECT menu_name FROM menu WHERE menu_name = 'Nasi Goreng'
        ) LIMIT 1;"""
    elif x == 1:
        sql = """iNSERT INTO menu (menu_name,price)
        SELECT * FROM (SELECT 'Mee Goreng' AS menu_name, '6.00' AS price) AS temp
        WHERE NOT EXISTS (
        SELECT menu_name FROM menu WHERE menu_name = 'Mee Goreng'
        ) LIMIT 1;"""
    elif x == 2:
        sql = """iNSERT INTO menu (menu_name,price)
        SELECT * FROM (SELECT 'Char kway teow' AS menu_name, '6.50' AS price) AS temp
        WHERE NOT EXISTS (
        SELECT menu_name FROM menu WHERE menu_name = 'Char kway teow'
        ) LIMIT 1;"""
    mycursor.execute(sql)
    database.commit()

#create table sales
mycursor.execute("CREATE TABLE IF NOT EXISTS sales (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, menu_id INT, user_id INT, quantity INT, total_price varchar(20), date DATE, FOREIGN KEY (menu_id) REFERENCES menu (id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE);")


SERVER = "192.168.56.101"
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#binding socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)


#this function check login user exist or not. If exist, allow the user to access the system
def checkUser(conn,addr,receive_msg):
    sql = "SELECT * FROM user where username = %s AND password = %s;"
    mycursor.execute(sql, (receive_msg[1],receive_msg[2]))
    row = mycursor.rowcount
    mycursor.execute(sql, (receive_msg[1],receive_msg[2]))
    user = mycursor.fetchone()

    if(row == 1):
        status = ["yes", user[4]]
        status = json.dumps(status)
        conn.sendall(bytes(status,encoding="utf-8"))
        print(f"[LOGIN] {user[1]} successfully login from {addr}")
        cont = True
        while cont:
            message = conn.recv(10000).decode(FORMAT)
            if message:
                message = json.loads(message)
                if message[0] == "menu":
                    sendMenu(conn,addr)
                    orderMessage = conn.recv(10000).decode(FORMAT)
                    if orderMessage:
                        orderMessage = json.loads(orderMessage)
                        calculate(conn,addr,orderMessage,message)
                    else:
                        print("[WARNING] No Data From User")

                elif message[0] == "history":
                    sendHistory(conn,addr,message)

                elif message[0] == "change":
                    address = conn.recv(10000).decode(FORMAT)
                    if address:
                        address = json.loads(address)
                        changeAddress(conn,addr,message,address)
                    else:
                        print("[WARNING] No Data From User")
                
                elif message[0] == "add":
                    newMenu = conn.recv(10000).decode(FORMAT)
                    if newMenu:
                        newMenu = json.loads(newMenu)
                        addMenu(conn,addr,newMenu)
                    else:
                        print("[WARNING] No Data From Admin")
                
                elif message[0] == "customer":
                    sendCustomerHistory(conn,addr)
                
                elif message[0] == "sales":
                    sendSalesDay(conn,addr)
            else:
                print(f"[LOGOUT] {user[1]} Logged Out From The System")
                cont = False
        
    else:
        status = "no"
        status = json.dumps(status)
        conn.sendall(bytes(status,encoding="utf-8"))
    

#this function create new user
def createUser(conn,addr,receive_msg):
    sql = "SELECT * FROM user where username = %s;"
    mycursor.execute(sql, (receive_msg[1],))
    row = mycursor.rowcount
    if(row > 0):
        status = "no"
        conn.send(status.encode(FORMAT))
    else:
        sql = "INSERT INTO user (id, username, password, address, role) VALUES (NULL,%s, %s, %s, %s);"
        mycursor.execute(sql, (receive_msg[1],receive_msg[2], receive_msg[3], 2))
        database.commit()
        status = "yes"
        conn.send(status.encode(FORMAT))


#this function send the latest menu to the client when requested by customer
def sendMenu(conn,addr):
    sql = "SELECT menu_name, price FROM menu;"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    lists = json.dumps(result)
    conn.sendall(bytes(lists,encoding="utf-8"))


#this function send order history to the customer based on customer username
def sendHistory(conn,addr,message):
    sql = """select menu.menu_name, sales.quantity, sales.total_price, CAST(sales.date AS CHAR) from sales
        inner join menu on menu.id = sales.menu_id inner join user
        on user.id = sales.user_id where user.username = %s order by sales.date desc;"""
    mycursor.execute(sql, (message[1],))
    result = mycursor.fetchall()
    lists = json.dumps(result)
    conn.sendall(bytes(lists,encoding="utf-8"))


#this function calculate the total price for customer order and insert the order into sales table
def calculate(conn,addr,orderMessage,message):
    totalPrice = 0
    listLen = len(orderMessage)
    listLen = int(listLen / 2)
    y = 0
    sql1 = "SELECT id, address FROM user where username = %s;"
    mycursor.execute(sql1, (message[1],))
    userId = mycursor.fetchone()
    for x in range(listLen):
        sql2 = "SELECT id, price FROM menu limit %s,1;"
        limit = int(orderMessage[y]) - 1
        mycursor.execute(sql2, (limit,))
        result = mycursor.fetchone()
        price = float(result[1]) * float(orderMessage[y+1])
        price = "{:.2f}".format(price)
        totalPrice = float(totalPrice) + (float(result[1]) * float(orderMessage[y+1]))
        totalPrice = "{:.2f}".format(totalPrice)

        today = str(date.today())
        sql3 = "INSERT INTO sales (id, menu_id, user_id, quantity, total_price, date) VALUES (NULL,%s, %s, %s, %s, %s);"
        mycursor.execute(sql3, (result[0], userId[0], orderMessage[y+1], price, today))
        database.commit()
        y=y+2
    lists = [totalPrice, userId[1]]    
    lists = json.dumps(lists)
    conn.sendall(bytes(lists,encoding="utf-8"))  
    print("[INFO] New Sales Successfully Stored In Database")


#this function allow customer to change their delivery address
def changeAddress(conn,addr,message,address):
    sql = "UPDATE user SET address = %s WHERE username = %s;"
    mycursor.execute(sql, (address,message[1]))
    database.commit()
    result = ["\n[SERVER] Address Changed Successfully"]
    result = json.dumps(result)
    conn.sendall(bytes(result,encoding="utf-8"))


#this function allow admin to add new menu into menu table
def addMenu(conn,addr,newMenu):
        sql = "SELECT * FROM menu WHERE menu_name = %s;"
        mycursor.execute(sql, (newMenu[0],))
        row = mycursor.rowcount
        if row > 0:
            status = ["\n[SERVER] Menu Already Exist In Database, Please Create Unique Menu"]
            status = json.dumps(status)
            conn.sendall(bytes(status,encoding="utf-8"))
        else:
            sql = "INSERT INTO menu (id, menu_name, price) VALUES (NULL, %s, %s);"
            mycursor.execute(sql, (newMenu[0], newMenu[1]))
            database.commit()
            status = ["\n[SERVER] New Menu Successfully Created"]
            status = json.dumps(status)
            conn.sendall(bytes(status,encoding="utf-8"))
            print("[SERVER] New Menu Successfully Added To Database")

#this function send all of the customers orders to the admin
def sendCustomerHistory(conn,addr):
    sql = """select user.username, menu.menu_name, sales.quantity, sales.total_price, CAST(sales.date AS CHAR), user.address from sales
    inner join menu on menu.id = sales.menu_id inner join user
    on user.id = sales.user_id order by sales.date desc;"""
    mycursor.execute(sql)
    result = mycursor.fetchall()
    lists = json.dumps(result)
    conn.sendall(bytes(lists,encoding="utf-8"))

#this function calculates the total sales of current day
def sendSalesDay(conn,addr):
    today = str(date.today())
    sql = "SELECT SUM(cast(total_price AS DECIMAL(10,2))) AS total_sales FROM sales where date = %s";
    mycursor.execute(sql,(today,))
    result = mycursor.fetchall()
    result = str(result[0][0])
    lists = json.dumps(result)
    conn.sendall(bytes(lists,encoding="utf-8"))

#this function allow user to choose either login or create a new account. It will call the appropriate function
def handle_client(conn,addr):
    try:
        try:
            connected = True
            while connected:
                receive_msg = conn.recv(10000).decode(FORMAT)
                if receive_msg:
                    receive_msg = json.loads(receive_msg)             
                    if receive_msg[0] == "1":
                        checkUser(conn,addr,receive_msg)  
                    elif receive_msg[0] == "2":
                        createUser(conn,addr,receive_msg)  
            conn.close()
        except OverflowError:
            print("[OVERFLOW] Overflow Error")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)    
    except KeyboardInterrupt:
        print('[INTERRUPT] Server Has Been Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)    


#this function mainly allows multi-threading where it will send new connection to function handle_client()
def start():
    try:
        try:
            server.listen()
            try:
                while True:
                    try:
                        conn, addr = server.accept()
                        thread = threading.Thread(target=handle_client, args=(conn,addr))
                        thread.start()
                    except socket.error:
                        print("Socket Error")
            except Exception as e:
                print("[EXCEPTION] An Exception Has Occured:")
                print(e)
                sys.exit(1)
        except OverflowError:
            print("[OVERFLOW] Overflow Error")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)    
    except KeyboardInterrupt:
        print('[INTERRUPT] Server Has Been Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


#main function
if __name__ == "__main__":
    print("[STARTING] SERVER IS STARTING")
    start()
