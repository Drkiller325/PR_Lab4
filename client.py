import socket
import threading
import json
import os
import base64

def send_message(sock, message_type, payload):
    message = {
        "type": message_type,
        "payload": payload
    }
    message_json = json.dumps(message)
    sock.send(message_json.encode('utf-8'))


def upload_file(sock, file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} doesn't exist.")
        return

    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Convert bytes data to base64-encoded string
    file_data_base64 = base64.b64encode(file_data).decode('utf-8')

    file_name = os.path.basename(file_path)
    message = {
        'sender': connect_message['name'],
        "file_name": file_name,
        "file_data_base64": file_data_base64
    }
    send_message(sock, "upload_file", message)

def download_file(sock, file_name):
    request = {
        "file_name": file_name
    }
    send_message(sock, "download_file", request)



# Server configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 11111  # Server's port
# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
client_socket.connect((HOST, PORT))

name = input("enter your name: ")
room = input("enter the name of the room: ")

# Connect to the server
connect_message = {
    "name": name,
    "room": room
}
send_message(client_socket, "connect", connect_message)


# Function to receive and display messages
def receive_messages():
    # Receive and handle messages from the server
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        received_message = json.loads(data)
        message_type = received_message["type"]
        payload = received_message["payload"]

        if message_type == "connect_ack":
            print(f"Server Acknowledgment: {payload['message']}")
        elif message_type == "message":
            print(f"Received message from {payload['sender']} in room {payload['room']}: {payload['text']}")
        elif message_type == "notification":
            print(f"Server Notification: {payload['message']}")
        elif message_type == "download_file":
            if "file_data_base64" in payload:
                file_data_base64 = payload["file_data_base64"]

                # Convert base64-encoded string back to bytes

                file_data = base64.b64decode(file_data_base64.encode('utf-8'))

                # Save the uploaded file to the server media folder

                file_path = os.path.join('downloads', payload['file_name'])

                with open(file_path, 'wb') as file:

                    file.write(file_data)
                print(f"Downloaded file: {payload['file_name']}")
            else:
                print(f"Server Response: {payload['message']}")


# Start the message reception thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Thread will exit when the main program exits
receive_thread.start()
while True:
    message = input("Enter a message (or 'exit' to quit): ")
    if message.lower() == 'upload':
        path = input('enter the path: ')
        upload_file(client_socket,path)
    elif message.lower() == 'download':
        name = input('enter the file name: ')
        download_file(client_socket,name)
    elif message.lower() == 'exit':
        break
    else:
        payload = {
            "sender": connect_message['name'],
            "room": connect_message['room'],
            "text": message
        }
        send_message(client_socket,"message",payload)





# Close the client socket when done
client_socket.close()
