#imports
import socket
import os
import ollama
import time
import subprocess
import threading
global serverSocket #can be used anywhere
import signal
import sys

#encode command converts data into bytes and decode does the opposite

def signal_handler(sig, frame): #when ctrl + c is used it exists
    global serverSocket
    print("\n? Shutting down...")
    serverSocket.close()

def generateResponse(prompt):
    response=ollama.chat( #talks to the ollama server
        model='phi3',
        messages = [{'role': 'user', 'content': prompt}]
    )
    return response['message']['content'] # return response

def handleClient(clientSocket, addr): #handles on or more clients
    print("Got a connection from %s" % str(addr))
    clientSocket.send("Connection established".encode())
    while True: #in a loop forever waiting for bytes which in the form of messages from the client
        data = clientSocket.recv(16384)
        if not data: #if client sent 0 bytes
            break
        #if bytes were sent
        print("Received: ", data.decode())#convert from bytes to original data
        userInput = data.decode()
        clientSocket.send("Generating response ...".encode())
        ai_response = generateResponse(userInput)
        clientSocket.send(ai_response.encode())


def signal_handler(sig, frame):
    global serverSocket
    print("\nShutting down server...")
    try:
        serverSocket.close()
    except:
        pass
    sys.exit(0)

def connect_to_ollama(): #runs command to communicate with ollama server and to get model
    subprocess.Popen(['ollama', 'serve'],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    #pause execution for a bit
    time.sleep(3)

    #pull Phi-3 model
    subprocess.run(
        ['ollama','pull','phi3'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def main():
    global serverSocket
    #make socket object
    serverSocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse the address

    signal.signal(signal.SIGINT, signal_handler)# Ctrl+c
    signal.signal(signal.SIGTERM, signal_handler) #IDE kill button

    #get local machine name
    host=socket.gethostname()
    port=8888

    #bind them
    serverSocket.bind((host,port))

    # queue up to 5 requests
    serverSocket.listen(5) #listens

    #this starts ollama and makes a thread to handle multiple clients
    threading.Thread(target=connect_to_ollama, daemon=True).start()

    if serverSocket.fileno()==-1:
        print("Server failed")
    else:
        print("Server started !")

    while True: #listens forever
        # accept a connection
        clientSocket,addr = serverSocket.accept()

        #start thread for each client
        #also accepts many clients
        threading.Thread(target=handleClient, args=(clientSocket, addr), daemon=True).start()

    #run in terminal
main()



