# echo_client.py
import socket
import threading
import tkinter as tk
from tkinter import ttk # modern themed widgets
import time


class client:
    def __init__(self): #initialise variables
        self.host = socket.gethostname()
        self.port = 8888                  # The same port as used by the server
        self.s=None
        self.running=True

    def connect(self): #connects
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # communication socket
        self.s.connect((self.host, self.port))


    def wait_For_Server(self): #checks if server is up
        while True:
            try:
                test_socket = socket.socket() #temporary socket
                test_socket.connect((self.host, self.port))
                test_socket.close()
                return # exit out of loop if server is up
            except ConnectionRefusedError:
                print("Waiting for server...")
                time.sleep(1)

    def receiveMessage(self):
        while self.running:
            try:
                msg=self.s.recv(1024).decode()
                if msg: #if there is data
                    self.chat_box.config(state='normal')  # Enable
                    self.chat_box.insert('end', f"Ollama: {msg}\n")
                    self.chat_box.config(state='disabled')  # Disable
                    self.chat_box.see('end')
            except OSError:  #displays information if connection breaks
                # Socket error or forced disconnect
                self.running = False
                self.onDisconnect()
                break


    def onDisconnect(self):
        try:
            self.s.close()
        except:
            pass
        self.chat_box.config(state='normal')  # Enable
        self.chat_box.insert('end', "\n[Disconnected from server]\n")
        self.chat_box.config(state='disabled')  # Disable
        self.chat_box.see('end')

    def send_message(self):
        message = self.input_box.get("1.0", "end-1c")  # get text in input box
        if message.strip():
            self.chat_box.config(state='normal')
            self.chat_box.insert('end', f"You: {message}\n")
            self.chat_box.config(state='disabled')

            try:
                self.s.send(message.encode())
            except OSError: #displays information if server disconnects
                self.running = False
                self.onDisconnect()

            self.input_box.delete("1.0", "end")


    def setGui(self):
        self.root = tk.Tk()
        self.root.title("Chat Box")
        self.root.geometry("500x450")

        style=ttk.Style()
        style.theme_use("clam")#modern theme

    #chat frame
        chat_frame=ttk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        #displays chat box
        self.chat_box = tk.Text(self.root, state='disabled')
        self.chat_box.pack(fill="both", expand=True, padx=10, pady=10)

    #input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        #displays input
        self.input_box = tk.Text(self.root, height=3, bd=1, relief="solid")
        self.input_box.pack(fill="x", padx=10, pady=(0, 10))

    #Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=(0, 10))
        #displays button
        self.send_button = ttk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

        #start listening thread
        threading.Thread(target=self.receiveMessage,daemon=True).start()
        self.root.mainloop()

client=client()
client.wait_For_Server() # checks if the server is down
client.connect() # connects to server
client.setGui() # displays gui



