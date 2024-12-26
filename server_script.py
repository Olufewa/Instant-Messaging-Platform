"""
Project 1: Instant Messaging (IM) Platform

Description:
This project implements a real-time messaging platform using networking concepts and protocols.
Key features include a client-server architecture, secure user authentication, private messaging,
broadcast messaging, and visibility of online clients.

Features:
1. Network Architecture:
   - Central server handles multiple client connections using TCP/IP.
   - SQLite database for user authentication.

2. User Authentication:
   - Secure registration with <username> and <password>.
   - Prevents duplicate registrations.
   - Tracks user status (online/offline).

3. Messaging Features:
   - Broadcast messages to all connected users.
   - Private messaging between users.

Authors:
- Timilehin Falusi
- Olufewa Favour Alonge

Other Sources:
- ChatGPT (comments and documentation.)

Date: 12/15/2024
"""

import socket  # For network communication
import threading  # For handling multiple clients concurrently
import sqlite3  # For secure user authentication storage

# Initialize the SQLite database for user credentials
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()  # Save changes to the database

# Dictionary to track online users and their respective sockets
online_clients = {}

# Function to broadcast a message to all connected clients
def broadcast(message, sender=None):
    # Iterate over all connected clients
    for username, client_socket in online_clients.items():
        if username != sender:  # Skip the sender if specified
            client_socket.send(message.encode('utf-8'))

# Function to handle commands from a single client
def handle_client(client_socket, address):
    username = None  # Initialize username as None until login
    while True:
        try:
            # Receive a command from the client
            command = client_socket.recv(1024).decode('utf-8')

            # Handle user registration
            if command.startswith("REGISTER"):
                _, uname, pwd = command.split()  # Parse username and password
                cursor.execute("SELECT * FROM users WHERE username = ?", (uname,))
                if cursor.fetchone():  # Check if the username exists
                    client_socket.send("ERROR: Username already exists.".encode('utf-8'))
                else:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (uname, pwd))
                    conn.commit()  # Save new user to the database
                    client_socket.send("Registration successful.".encode('utf-8'))

            # Handle user login
            elif command.startswith("LOGIN"):
                _, uname, pwd = command.split()  # Parse username and password
                cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (uname, pwd))
                if cursor.fetchone():  # Validate credentials
                    if uname in online_clients:  # Check if already logged in
                        client_socket.send("ERROR: User already logged in.".encode('utf-8'))
                    else:
                        username = uname  # Set the username for this session
                        online_clients[username] = client_socket  # Add to online clients
                        client_socket.send("Login successful.".encode('utf-8'))
                else:
                    client_socket.send("ERROR: Invalid credentials.".encode('utf-8'))

            # Handle request for online clients
            elif command == "ONLINE":
                online_list = ", ".join(online_clients.keys())  # Get all online usernames
                client_socket.send(f"Online users: {online_list}".encode('utf-8'))

            # Handle broadcast messages
            elif command.startswith("MESSAGE"):
                _, msg = command.split(maxsplit=1)  # Parse the message
                if username:  # Ensure the user is logged in
                    broadcast(f"{username}: {msg}", sender=username)
                else:
                    client_socket.send("ERROR: Please log in first.".encode('utf-8'))

            # Handle private messages
            elif command.startswith("PRIVATE"):
                _, target_user, msg = command.split(maxsplit=2)  # Parse recipient and message
                if target_user in online_clients:  # Check if recipient is online
                    online_clients[target_user].send(f"Private from {username}: {msg}".encode('utf-8'))
                else:
                    client_socket.send("ERROR: User not online.".encode('utf-8'))

            # Handle user disconnect
            elif command == "QUIT":
                client_socket.send("Goodbye!".encode('utf-8'))
                if username:  # Remove user from online clients if logged in
                    del online_clients[username]
                client_socket.close()  # Close the connection
                break

            # Handle unknown commands
            else:
                client_socket.send("ERROR: Unknown command.".encode('utf-8'))

        except Exception as e:
            # Handle disconnection or errors
            if username and username in online_clients:
                del online_clients[username]
            client_socket.close()  # Close the socket
            break

# Function to start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    server.bind(('127.0.0.1', 5555))  # Bind to localhost and port 5555
    server.listen(5)  # Listen for up to 5 connections
    print("Server started on port 5555.")

    while True:
        client_socket, address = server.accept()  # Accept new connections
        print(f"Connection from {address}")  # Log the connection
        threading.Thread(target=handle_client, args=(client_socket, address)).start()  # Handle client in a new thread

if __name__ == "__main__":
    start_server()  # Start the server
