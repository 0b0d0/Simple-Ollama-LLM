# echo_client.py
import socket
import threading
import tkinter as tk
from tkinter import ttk # modern themed widgets
import time
#encode command converts data into bytes and decode does the opposite


class client:
    def __init__(self): #initialise variables
        self.host = socket.gethostname()
        self.port = 8888                  # The same port as used by the server
        self.s=None
        self.running=True

    def connect(self): #connects
        #self.s value also changes when the function is called
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # communication socket
        self.s.connect((self.host, self.port))


    def wait_For_Server(self): #checks if server is up
        try:
            self.connect()
            threading.Thread(target=self.receiveMessage, daemon=True).start()# start message listener thread

        except ConnectionRefusedError: # when connection is down
            self.chat_box.config(state='normal')
            self.chat_box.insert('end', "\nWaiting for server or reconnect...\n")
            self.chat_box.config(state='disabled')
            #print("Waiting for server...")
            self.root.after(3000, self.wait_For_Server) # call function again after 3 seconds

    def addMessage(self,brand,msg):
        self.chat_box.config(state='normal')
        self.chat_box.insert('end', f"{brand} {msg}\n")
        self.chat_box.config(state='disabled')

    def stopAnimation(self):
        self.animating = False

    def startAnimation(self):
        self.animating = True
        frames = ["|", "/", "-", "\\"]
        self.animation_index = 0

        #dds first animation line once
        self.addMessage("Ollama:", f"Generating {frames[0]}")

        def animate():
            if not self.animating: # if false
                return #exits out loop
            frame = frames[self.animation_index]
            self.animation_index = (self.animation_index + 1) % len(frames)
            # --- overwrite the last line directly ---
            self.chat_box.config(state='normal')
            self.chat_box.delete("end-2l", "end-1c")  # delete last line
            self.chat_box.insert("end", f"Ollama: Generating {frame}\n")
            self.chat_box.config(state='disabled')
            self.chat_box.see("end")
            # ----------------------------------------

            self.root.after(150, animate)#repeats function every x seconds

        animate()

    #Lambda makes the gui calls work
    def receiveMessage(self):
        while self.running:
            try:
                msg=self.s.recv(16384).decode() # get message
                if msg: #if there is data
                    #check if animation is still running
                    if hasattr(self,"animating") and self.animating:
                        self.stopAnimation() #stop start animation function
                    self.addMessage("Ollama:",msg)

            except OSError:  #displays information if connection breaks
                # Socket error or forced disconnect
                self.running = False
                self.root.after(0, self.onDisconnect)
                break



    def onDisconnect(self):
        try:
            self.s.close()
        except:
            pass
        self.chat_box.config(state='normal')  # Enable
        self.chat_box.insert('end', "\n[Disconnected from server]\n")#insert message on chat box
        self.chat_box.config(state='disabled')  # Disable
        self.chat_box.see('end')

    def send_message(self,event=None):
        message = self.input_box.get("1.0", "end-1c")  # get text in input box
        if isinstance(message,str): #if it is a string
            if message.strip(): # removes whitespace
                self.chat_box.config(state='normal')
                self.chat_box.insert('end', f"You: {message}\n")#insert message on chat box
                self.chat_box.config(state='disabled')

                try:
                    self.s.send(message.encode())#convert data into bytes
                    self.startAnimation()#start animation
                except OSError: #displays information if server disconnects
                    self.running = False
                    self.root.after(0, self.onDisconnect)#call function on main thread
                self.input_box.delete("1.0", "end")

            elif message == "":  # if empty
                self.chat_box.config(state='normal')
                self.chat_box.insert('end', f"You: There is no data \n")  # insert message on chat box
                self.chat_box.config(state='disabled')

        return "break" #stops enter adding new line




    #padx and pady move the shapes
    def setGui(self):
        self.root = tk.Tk()
        self.root.title("Chat Box")
        self.root.geometry("500x450")

        # Set minimum window size here
        self.root.minsize(400, 300)

        style = ttk.Style()
        style.theme_use("clam")  # modern theme

        # chat frame
        chat_frame = ttk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # displays chat box
        self.chat_box = tk.Text(chat_frame, state='disabled', wrap="word")
        self.chat_box.pack(fill="both", expand=True)

        # input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        # displays input
        self.input_box = tk.Text(input_frame, height=3, bd=1, relief="solid")
        self.input_box.pack(fill="x")
        self.input_box.bind("<Return>",self.send_message)#makes enter key event work

        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=(0, 10))
        # displays button
        self.send_button = ttk.Button(button_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="left", padx=5)

        self.send_button2 = ttk.Button(button_frame, text="Upload Image - Not done yet")
        self.send_button2.pack(side="left", padx=5)

        # Schedule wait_For_Server to run after GUI is ready
        self.root.after(100, self.wait_For_Server)
        self.root.mainloop()

client=client()
client.setGui() # displays gui
client.wait_For_Server()  # checks if the server is down





