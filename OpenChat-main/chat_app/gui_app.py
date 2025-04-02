import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import socketio
import json
import os
from datetime import datetime
import random
import string
from PIL import Image, ImageTk
import time

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenChat")
        self.root.geometry("800x600")
        
        # Initialize SocketIO client
        self.sio = socketio.Client()
        self.setup_socket_events()
        
        # Variables
        self.room_code = None
        self.username = None
        self.connected = False
        self.max_retries = 3
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial login screen
        self.show_login_screen()
        
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', padding=5)
        style.configure('TEntry', padding=5)
        
    def connect_to_server(self):
        retries = 0
        while retries < self.max_retries:
            try:
                if not self.connected:
                    self.sio.connect('http://localhost:8080')
                    return True
            except Exception as e:
                retries += 1
                if retries < self.max_retries:
                    time.sleep(2)  # Wait before retrying
                    continue
                messagebox.showerror("Connection Error", 
                    f"Could not connect to server after {self.max_retries} attempts.\n"
                    "Please make sure the server is running on http://localhost:8080")
                return False
        return False
        
    def show_login_screen(self):
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.login_frame, text="OpenChat", font=('Helvetica', 24))
        title_label.pack(pady=20)
        
        # Create/Join Room buttons
        btn_frame = ttk.Frame(self.login_frame)
        btn_frame.pack(pady=20)
        
        create_btn = ttk.Button(btn_frame, text="Create Room", command=self.create_room)
        create_btn.pack(side=tk.LEFT, padx=10)
        
        # Join room frame
        join_frame = ttk.Frame(self.login_frame)
        join_frame.pack(pady=20)
        
        self.room_entry = ttk.Entry(join_frame, width=20)
        self.room_entry.pack(side=tk.LEFT, padx=5)
        
        join_btn = ttk.Button(join_frame, text="Join Room", command=self.join_room)
        join_btn.pack(side=tk.LEFT)
        
    def show_chat_screen(self):
        self.login_frame.destroy()
        
        # Chat container
        self.chat_container = ttk.Frame(self.main_frame)
        self.chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Room info
        room_info = ttk.Frame(self.chat_container)
        room_info.pack(fill=tk.X, pady=5)
        
        room_label = ttk.Label(room_info, text=f"Room: {self.room_code}")
        room_label.pack(side=tk.LEFT)
        
        username_label = ttk.Label(room_info, text=f"Username: {self.username}")
        username_label.pack(side=tk.LEFT, padx=20)
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(self.chat_container, wrap=tk.WORD, height=20)
        self.chat_area.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chat_area.config(state=tk.DISABLED)
        
        # Input area
        input_frame = ttk.Frame(self.chat_container)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.LEFT)
        
        file_btn = ttk.Button(input_frame, text="Send File", command=self.send_file)
        file_btn.pack(side=tk.LEFT, padx=5)
        
        leave_btn = ttk.Button(input_frame, text="Leave Room", command=self.leave_room)
        leave_btn.pack(side=tk.LEFT)
        
    def setup_socket_events(self):
        @self.sio.on('connect')
        def on_connect():
            print("Connected to server")
            self.connected = True
            
        @self.sio.on('disconnect')
        def on_disconnect():
            print("Disconnected from server")
            self.connected = False
            
        @self.sio.on('message')
        def on_message(data):
            print(f"Received message: {data}")  # Debug print
            self.root.after(0, lambda: self.display_message(data))
            
        @self.sio.on('user_joined')
        def on_user_joined(data):
            print(f"User joined: {data}")  # Debug print
            self.root.after(0, lambda: self.display_system_message(f"{data['username']} joined the room"))
            
        @self.sio.on('user_left')
        def on_user_left(data):
            print(f"User left: {data}")  # Debug print
            self.root.after(0, lambda: self.display_system_message(f"{data['username']} left the room"))
            
    def create_room(self):
        try:
            if not self.connect_to_server():
                return
            
            self.username = self.generate_random_name()
            self.room_code = self.generate_room_code()
            
            self.sio.emit('join', {
                'username': self.username,
                'room': self.room_code
            })
            
            self.show_chat_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create room: {str(e)}")
            
    def join_room(self):
        room_code = self.room_entry.get().strip()
        if not room_code:
            messagebox.showerror("Error", "Please enter a room code")
            return
            
        try:
            if not self.connect_to_server():
                return
            
            self.username = self.generate_random_name()
            self.room_code = room_code
            
            self.sio.emit('join', {
                'username': self.username,
                'room': self.room_code
            })
            
            self.show_chat_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Could not join room: {str(e)}")
            
    def send_message(self):
        message = self.message_entry.get().strip()
        if message and self.connected:
            try:
                data = {
                    'room': self.room_code,
                    'message': message,
                    'username': self.username,
                    'type': 'message'
                }
                print(f"Sending message: {data}")  # Debug print
                self.sio.emit('message', data)
                
                # Also display the message locally
                self.display_message({
                    'message': message,
                    'username': self.username
                })
                
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                print(f"Error sending message: {str(e)}")  # Debug print
                messagebox.showerror("Error", f"Could not send message: {str(e)}")
            
    def send_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ('Text files', '*.txt'),
                ('PDF files', '*.pdf'),
                ('Image files', '*.png;*.jpg;*.jpeg;*.gif'),
                ('Document files', '*.doc;*.docx')
            ]
        )
        if file_path:
            # TODO: Implement file upload functionality
            messagebox.showinfo("Info", "File upload will be implemented in future versions")
            
    def leave_room(self):
        try:
            self.sio.emit('leave', {
                'username': self.username,
                'room': self.room_code
            })
            self.sio.disconnect()
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error leaving room: {str(e)}")
            
    def display_message(self, data):
        try:
            self.chat_area.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M")
            message = data.get('message', '')
            username = data.get('username', 'Unknown')
            
            # Format the message
            formatted_message = f"[{timestamp}] {username}: {message}\n"
            print(f"Displaying message: {formatted_message}")  # Debug print
            
            self.chat_area.insert(tk.END, formatted_message)
            self.chat_area.see(tk.END)
            self.chat_area.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error displaying message: {str(e)}")  # Debug print
            
    def display_system_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_area.insert(tk.END, f"[{timestamp}] System: {message}\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)
        
    @staticmethod
    def generate_room_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
    @staticmethod
    def generate_random_name():
        ADJECTIVES = ['Happy', 'Clever', 'Brave', 'Gentle', 'Swift', 'Bright', 'Kind', 'Wise', 'Quick', 'Cool']
        NOUNS = ['Panda', 'Fox', 'Eagle', 'Tiger', 'Dolphin', 'Wolf', 'Bear', 'Lion', 'Hawk', 'Owl']
        return f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}"

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
