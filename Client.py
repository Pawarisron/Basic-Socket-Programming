from socket import*
from datetime import datetime
import time
import threading
import os

#Status code
    #100 login success
    #101 login fail
    #102 request login

    #200 room Online
    #201 room Offline
    #202 request create room
    #203 not request create room
    #204 user join room
    #205 user left room

    #300 End message
    #301 sent message
    #302 request all message
    #333 OK

    #666 ping

#Client
username = None
serverName = "127.0.0.1"
serverPort = 12100
clientSocket = socket(AF_INET,SOCK_STREAM) #TCP
error = None

#Room
roomIsOnline = False
roomMessage = []
tmpMessage = []

#Event Thread
serverEvent = threading.Event()
serverEvent.set()
roomMessageLock = threading.Lock()



print("===================================================")
print("                ::Client Side::")
print("===================================================")


def helpCmd():
    os.system('clear') #for Mac
    os.system('cls')  #for Window
    print("===================================================")
    print(f"                ::Room{roomNumber}::")
    print("===================================================")
    print("/help      | To view all commands.")
    print("/update    | To make the messages sent from the server up to date. ")
    print("/ping      | To Ping Server.")
    print("/exit      | To exit the program. ")
    print("===================================================")
    print(f"Press any key:")
    input()

def updateScene():
    os.system('clear') #for Mac
    os.system('cls')  #for Window
    print("===================================================")
    print(f"                ::Room{roomNumber}::")
    print("===================================================")
    #print room message
    for tmp in roomMessage:
        printMsg = tmp.split(",")
        print("[MSG]",printMsg[0],printMsg[1]+":"+printMsg[2])
    #print tmp message
    for tmp in tmpMessage:
        print(tmp)
    #clear tmp message
    tmpMessage.clear()
    print("===================================================")
    print(f"[{username}] Input:")

def requestAllMessage(username,roomNumber,roomPassword):
    serverEvent.clear()
    roomMessage = []
    #send 302 request all message
    sendMsg = "302"+","+username+","+roomNumber+","+roomPassword
    print("[Info] Get All Message")
    clientSocket.send(sendMsg.encode())
    recvMsg = clientSocket.recv(1024).decode()
    recvMsgIndex = recvMsg.split(",")
    if recvMsgIndex[0] == "302":
        sendMsg = "333"+","+username+","+roomNumber+","+"OK"
        clientSocket.send(sendMsg.encode())
        #receive room message
        while True:
            recvMsg = clientSocket.recv(1024).decode()
            recvMsgIndex = recvMsg.split(",")
            sendMsg = "333"+","+username+","+roomNumber+","+"OK"
            clientSocket.send(sendMsg.encode())
            #End Message
            if recvMsgIndex[0] == "300":
                break
            roomMessage.append(recvMsg)
    serverEvent.set()
    return roomMessage

def requestUpdate(username,roomNumber,roomPassword):
    serverEvent.clear()
    roomMessage = []
    sendMsg = "333"+","+username+","+roomNumber+","+"OK"
    clientSocket.send(sendMsg.encode())
    #receive room message
    while True:
        recvMsg = clientSocket.recv(1024).decode()
        recvMsgIndex = recvMsg.split(",")
        sendMsg = "333"+","+username+","+roomNumber+","+"OK"
        clientSocket.send(sendMsg.encode())
        #End Message
        if recvMsgIndex[0] == "300":
            break
        roomMessage.append(recvMsg)
    serverEvent.set()
    return roomMessage

def handleUpdate(clientSocket):
    global roomMessage
    while True:
        recvMsg = clientSocket.recv(1024).decode()
        recvMsgIndex = recvMsg.split(",")
        statusCode = recvMsgIndex[0]
        serverEvent.clear()

        #this exit program / terminate handleUpdate
        if statusCode == "205":
            msgTime = recvMsgIndex[1]
            whoSended = recvMsgIndex[2]
            msg = recvMsgIndex[3]
            message = msgTime+",ROOM,"+whoSended+" left Room"
            #This client left the room
            if whoSended == username:
                clientSocket.close()
                break
            with roomMessageLock:
                roomMessage.append(message)
            #update scene
            updateScene()
        #request all message / update
        elif statusCode == "302":
            roomMessage = requestUpdate(username,roomNumber,roomPassword)
        #server ping
        elif statusCode == "666":
            #cal Ping
            msgTime = recvMsgIndex[1]
            newMsgTime = datetime.strptime(msgTime,"%Y-%m-%d %H:%M:%S")
            newCurrentTime = datetime.strptime(currentTime,"%Y-%m-%d %H:%M:%S")
            timeDiff = newCurrentTime - newMsgTime 
            ping = timeDiff.total_seconds() *1000
            tmpMessage.append(f"[Server]:Ping")
        
        elif statusCode == "301":
            msgTime = recvMsgIndex[1]
            whoSended = recvMsgIndex[2]
            msg = recvMsgIndex[3]
            message = msgTime+","+whoSended+","+msg

            with roomMessageLock:
                roomMessage.append(message)
            #update scene
            updateScene()

        elif statusCode == "204":
            msgTime = recvMsgIndex[1]
            whoSended = recvMsgIndex[2]
            msg = recvMsgIndex[3]
            message = msgTime+",ROOM,"+whoSended+" Join Room"

            with roomMessageLock:
                roomMessage.append(message)
            #update scene
            updateScene()
        
        #continue server stop event
        serverEvent.set()


#Connection
while True:
    currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        clientSocket.connect((serverName, serverPort))
        break
    except BaseException as e:
        print("[Error] ",currentTime,"No connection",)
        #reconnect every 5 sec.
        time.sleep(5)

if not error:
    clientAddress = clientSocket.getsockname()
    # print("Username:  ",username)
    print("ServerName:",gethostname())
    print("MyAddress:   ",gethostbyname(gethostname()))
    print("MyPort:      ",clientAddress[1])

    print("[Info] Connected successfully")

    username = input("[Input] Username: ")
    roomNumber = input("[Input] RoomNumber: ")
    roomPassword = input("[Input] RoomPassword: ")
    
    #send request login
    sendMsg = "102"+","+username+","+roomNumber+","+roomPassword
    clientSocket.send(sendMsg.encode())
    #receive
    recvMsg = clientSocket.recv(1024).decode()
    recvMsgIndex = recvMsg.split(",")
    
    #login success 100
    if recvMsgIndex[0] == "100": 
        print("[Server]",currentTime,"Login success")
        #receive
        recvMsg = clientSocket.recv(1024).decode()
        recvMsgIndex = recvMsg.split(",")
        if recvMsgIndex[0] == "201":
            print("[Server]",currentTime,"Room Offline")
            tmp = input("[Input] Do you want to create room (0/1):")
            if tmp == "1":
                #send 202,request create room
                print("[Info] request create room")
                sendMsg = "202,request create room"
                clientSocket.send(sendMsg.encode())
                recvMsg = clientSocket.recv(1024).decode()
                recvMsgIndex = recvMsg.split(",")
                if recvMsgIndex[0] == "200" :
                    print("[Server]",currentTime,"Room Online")
                    roomIsOnline = True       
            else:
                #send 203,not request create room
                print("[Info] not request create room")
                sendMsg = "203,not request create room"
                clientSocket.send(sendMsg.encode()) 

        if recvMsgIndex[0] == "200" :
            print("[Server]",currentTime,"Room Online")
            roomIsOnline = True 
        
        #Chat
        if roomIsOnline:
            #send 302 request all message
            roomMessage = requestAllMessage(username,roomNumber,roomPassword)
            
            #Thread Update
            updateThread = threading.Thread(target=handleUpdate, args=(clientSocket,))
            updateThread.start() 

            #Enter the Room Here::
            while True:
                #Stop when have server Event
                serverEvent.wait()
                #clear terminal
                updateScene()
                #Input
                sendMsg = input()
                #301 sent message
                if sendMsg:
                    #Exit
                    if sendMsg == "/exit":
                        print("[Info] Exit")
                        print("===================================================")
                        #205 user left the room
                        roomIsOnline = False
                        clientSocket.send(("205,"+username).encode())
                        break
                    #Update
                    elif sendMsg == "/update":
                        sendMsg = "302"+","+username+","+roomNumber+","+roomPassword
                        print("[Info] Get All Message")
                        clientSocket.send(sendMsg.encode())
                        serverEvent.clear()
                    #Ping
                    elif sendMsg == "/ping":
                        clientSocket.send(("666,"+currentTime+","+username).encode())
                    #Help
                    elif sendMsg == "/help":
                        helpCmd()
                    #unknown command
                    elif sendMsg[0] == "/" and len(sendMsg) > 4:
                        tmpMessage.append(f"[ROOM]:Unknown command, viewing all commands /help")
                    else:
                        try:
                            clientSocket.send(("301,"+currentTime+","+username+","+sendMsg).encode())
                            roomMessage.append(currentTime+","+username+","+sendMsg)
                        except:
                            print("An error occurred!")
                            clientSocket.close()
            #join thread to main        
            updateThread.join()
        clientSocket.close()

    #101 login fail
    elif recvMsgIndex[0] == "101":
        print("[Server]",currentTime,"Login fail")      
clientSocket.close()   
    

