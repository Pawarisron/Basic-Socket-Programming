# Socket Programming Project

## 📌 Project Overview
This project is a **network application** that enables communication between users through a **central server**. Users must be authorized with a **room name** and **room password** before they can join the chat room. Once connected, users can send and receive messages with each other. 

The application uses **TCP** as the transport layer protocol for reliable and ordered data transmission.

## 🎯 Objectives
The purpose of this program is to:
- Allow users to connect and chat with each other through a server.
- Implement authentication with room names and passwords.
- Ensure that all messages are reliably transmitted using TCP.

## 📡 **PAW Protocol**
The **PAW Protocol** is the custom protocol used for communication between the client and server. The protocol uses status codes to indicate the state of the communication.

### Status Codes:
- **100**: Login success
- **101**: Login fail
- **102**: Request login
- **200**: Room Online
- **201**: Room Offline
- **202**: Request create room
- **203**: Not request create room
- **204**: User join room
- **205**: User left room
- **300**: End message
- **301**: Sent message
- **302**: Request all message
- **333**: OK
- **666**: Ping

## 🖥️ **How to Use**
1. Run the **server program** to start the chat room service.
2. Run the **client program** to connect to the server.
3. Authenticate by providing the room name and password.
4. Once authenticated, join the room and start chatting.

## 📜 License
This project is for educational purposes and part of the course requirements.
