from socket import*
import time
import threading

#Server
serverName = "127.0.0.1"
serverPort = 12100
serverSocket = socket(AF_INET,SOCK_STREAM) #TCP
serverSocket.bind((serverName,serverPort))
userLogin = ["bas"]
serverLog = []
serverErrorLog = []
serverInfoLog = []
serverMsgLog = []

#Room info
roomNumber = "1001"
roomOnline = [False] #pass by ref
roomPassword = "100"
authorizedUser = ["oom","ryuu","bas","guy"]
userInRoom = {}
roomMessage = ["2024-02-10 20:34:31,Oom,Hello","2024-02-10 20:36:30,Ryuu,Doggo","2024-02-10 20:37:01,Bas,yolo"]
roomMessageLock = threading.Lock()

#Time
currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

print("===================================================")
print("                ::Server Side::")
print("===================================================")
print("HostName:",gethostname())
print("Myaddress: ",gethostbyname(gethostname()))
print("MyPort:    ",serverPort)
print("[Info] The server is ready to receive")

#wait for client
serverSocket.listen(5)

def infoLog(*text):
    combinedString = ','.join(text)
    msg = "[Info]",currentTime,addr,combinedString
    serverLog.append(print(str(msg)))
    serverErrorLog.append(msg)

def errorLog(*text):
    combinedString = ','.join(text)
    msg = "[Error]",currentTime,addr,combinedString
    serverLog.append(print(str(msg)))
    serverErrorLog.append(msg)

def msgLog(*text):
    combinedString = ','.join(text)
    msg = "[Msg]",currentTime,addr,combinedString
    serverLog.append(print(str(msg)))
    serverMsgLog.append(msg)


#send to all user
def broadcast(message, clientSocket=None, code="301"):
    for userSocketInRoom in userInRoom.values():
        if userSocketInRoom != clientSocket:
            try:
                if code == "301":
                    userSocketInRoom.send(("301,"+message).encode())
                elif code == "204":
                    userSocketInRoom.send(("204,"+message).encode())
                elif code == "205":
                    userSocketInRoom.send(("205,"+message).encode())
            except error as e:
                print(e)

def handleFirst(connectionSocket, addr):
    messageCode = ["301","302","205","666"]
    firstMsg = connectionSocket.recv(1024).decode()
    firstMsgIndex = firstMsg.split(",")

    #Check Login Status Code
    if firstMsgIndex[0] not in messageCode:
        client_thread = threading.Thread(target=handleClient, args=(connectionSocket,addr,firstMsg))
        client_thread.start()

#handle Room for user
def handleRoom(connectionSocket, addr,conToRoomNum,username):
    infoLog("Handle Room Thread start")
    msgLog("Broadcast: 204,Username:",username,"join Room:",conToRoomNum)
    #sent join room
    broadcast((currentTime+f",{username}, Join The Room"),connectionSocket,"204")
    while True:  
        #Terminate room
        if len(userInRoom) <= 0:
            infoLog(("Room Offline Room:",conToRoomNum))
            roomOnline[0] = False
            infoLog("CLOSE CONNECTION")
            connectionSocket.close()
            break
        try:
            msg = connectionSocket.recv(1024).decode()
        except ConnectionResetError as e:
            print(f"ConnectionResetError: {e}")
            connectionSocket.close()
        msgIndex = msg.split(",")

        #205 user left the room
        if msgIndex[0] == "205":
            infoLog("Recv: 205,",username,"Left The Room")
            username = msgIndex[1]
            #remove user in user in room
            if username in userInRoom:
                #connectionSocket.send(f"205,{currentTime},{username}, left The Room".encode())
                #send to all user
                broadcast((currentTime+f",{username}, left The Room"),None,"205")
                msgLog("Broadcast: 205",username,"Left The Room",conToRoomNum)
                #remove user login
                del userInRoom[username]
                userLogin.remove(username)
                if len(userInRoom) <= 0:
                    infoLog("Room Offline Room:",conToRoomNum)
                    roomOnline[0] = False
                break
            else:
                connectionSocket.close()
                errorLog("401 unexpected exception")
                break       

        #301 receive,sent Message
        if msgIndex[0] == "301":
            msgTime = msgIndex[1]
            username = msgIndex[2]
            infoLog("Recv: 301",username,msgTime,msgIndex[3])
            message = msgTime+","+username+","+msgIndex[3]
            msgLog("Broadcast: 301,Time:",msgTime,"Username:",username,msgIndex[3])
            with roomMessageLock:
                roomMessage.append(message)
            #send to all user
            broadcast(message, connectionSocket)
            
        #302 request all Message / update
        if msgIndex[0] == "302": 
            infoLog("Recv: 302",username,"get all message")
            username = msgIndex[1]
            #send 302 back
            connectionSocket.send("302, request all message".encode())
            infoLog("Send: 302 get all message")
            msg = connectionSocket.recv(1024).decode()
            msgIndex = msg.split(",")
            if msgIndex[0] == "333":
                infoLog("Recv: 333",username,"OK")

            #authorize
            if username in userInRoom:
                for chat in roomMessage:
                    #send
                    infoLog("Send: 301",username,chat)
                    connectionSocket.send(chat.encode())
                    #receive
                    msg = connectionSocket.recv(1024).decode()
                    msgIndex = msg.split(",")
                    if msgIndex[0] == "333":
                        infoLog("Recv: 333",username,"OK")
                #end off message stack 
                connectionSocket.send("300, End Message".encode())
                infoLog("Send: 300",username,"End Message")
        #666 Pinging
        if msgIndex[0]== "666":
                infoLog("Recv: 666",username,"Ping")
                connectionSocket.send(("666"+","+currentTime).encode())
                infoLog("Send: 666",username,"Ping")
    connectionSocket.close()

#handle user isn't in Room  
def handleClient(connectionSocket, addr, firstMsg):
    #01 first receive
    recvMsgIndex = firstMsg.split(",")
    #request login to room [102]
    if(recvMsgIndex[0] == "102"):
        
        recvMsgIndex = str(firstMsg).split(",")
        statusCode = recvMsgIndex[0]
        conUsername = recvMsgIndex[1]
        conToRoomNum = recvMsgIndex[2]
        conToRoomPass = recvMsgIndex[3]
        infoLog("Recv: 102,Username:", conUsername,"connectTo:",conToRoomNum,"pass:",conToRoomPass,"Request Login")
        #check login
        if conUsername in authorizedUser and conToRoomNum == roomNumber and conToRoomPass == roomPassword and conUsername not in userLogin: 
            #send
            connectionSocket.send("100,Login success".encode())
            infoLog("Send: 100,Login success")
            userLogin.append(conUsername)

            #Room not create 
            if not roomOnline[0]:
                #send 201, Room no create
                connectionSocket.send("201,Room offline".encode())
                infoLog("Send: 201,Room Offline")

                ##receive for create room? 202|203
                recvMsg = connectionSocket.recv(1024).decode()
                recvMsgIndex = recvMsg.split(",")
                
                #check want to create room ?
                #202 request create room
                if recvMsgIndex[0] == "202":
                    infoLog("Recv: 202,Request create room") 
                    #create Room from number
                    roomOnline[0] = True
                    #Message Status Code
                    infoLog("Room Online Room:",roomNumber)
                
                #203 not request to create room
                elif recvMsgIndex[0] == "203": 
                    infoLog("Recv: 203,Not Request create room") 
                    userLogin.remove(conUsername)
                    connectionSocket.close()
                else:
                    connectionSocket.close()
                    errorLog("401 unexpected exception")

            #Room was created
            if roomOnline[0]:
                infoLog("Send: 200,Room Online")
                #send 200,Room Online
                connectionSocket.send("200,Room Online".encode())
                roomThread = threading.Thread(target=handleRoom, args=(connectionSocket,addr,conToRoomNum,conUsername))
                #user join room
                userInRoom[conUsername] = connectionSocket
                roomThread.start()
        else:
            #send
            infoLog("Username:"+conUsername+"connectTo:"+conToRoomNum+"pass:"+conToRoomPass+"Login fail")
            connectionSocket.send("101,Login Fail".encode())
            infoLog("Send: 101,Login Fail")
            connectionSocket.close()
            infoLog("CLOSE CONNECTION")
            
#main
while True:
    currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #accept connect 
    connectionSocket, addr = serverSocket.accept()
    infoLog("OPEN CONNECTION")
    first_thread = threading.Thread(target=handleFirst, args=(connectionSocket,addr))
    first_thread.start()

    #make room offline
    if len(userInRoom) <= 0:
        infoLog(("Room Offline Room:"+roomNumber))
        roomOnline[0] = False

    