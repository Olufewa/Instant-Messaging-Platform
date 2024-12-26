"""
Project 1: Instant Messaging (IM) Platform

Description:
This is the client-side script for the Instant Messaging platform. It allows users to connect to
the server, register, log in, view online users, send broadcast messages, send private messages,
and disconnect from the platform.

Features:
1. Server Connection:
   - Establishes a TCP connection to the central server.

2. User Commands:
   - REGISTER: Register a new user with a username and password.
   - LOGIN: Log in using a valid username and password.
   - ONLINE: View a list of currently online users.
   - MESSAGE: Broadcast a message to all online users.
   - PRIVATE: Send a private message to a specific user.
   - QUIT: Disconnect from the server.

Authors:
- Timilehin Falusi
- Olufewa Favour Alonge

Other Sources:
- ChatGPT (comments and documentation.)

Date: 12/15/2024
"""

import socket  # For creating the network connection

# Function to start the client application
def start_client():
    # Create a TCP socket for the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server (localhost and port 5555)
        client.connect(("127.0.0.1", 5555))
        print("Connected to the server.")  # Notify the user of a successful connection
        print("Commands:")
        print("REGISTER <username> <password>, LOGIN <username> <password>,")
        print("ONLINE, MESSAGE <message>, PRIVATE <username> <message>, QUIT")

        while True:
            # Prompt the user for a command
            command = input("You: ")

            # Send the command to the server
            client.send(command.encode('utf-8'))

            # Handle the QUIT command to disconnect
            if command.lower() == "quit":
                # Receive and display the server's response
                print(client.recv(1024).decode('utf-8'))
                client.close()  # Close the connection
                break

            else:
                # Receive and display the server's response for other commands
                response = client.recv(1024).decode('utf-8')
                print(response)

    except ConnectionRefusedError:
        # Handle the case where the server is not reachable
        print("ERROR: Unable to connect to the server.")
    except Exception as e:
        # Handle unexpected errors
        print(f"ERROR: {str(e)}")
    finally:
        # Ensure the client socket is closed on exit
        client.close()

# Run the client application
if __name__ == "__main__":
    start_client()
