import socket
import threading
import json
import os
import base64
import uuid

# Define the server media folder
SERVER_MEDIA = str(uuid.uuid4())

if not os.path.exists(SERVER_MEDIA):
    os.makedirs(SERVER_MEDIA)

HOST = '127.0.0.1'
PORT = 11111

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server is listening on {HOST}:{PORT}")

# List to store connected clients
clients = []

def broadcast_message(sender, room, text):
    message = {
        "sender": sender,
        "room": room,
        "text": text
    }
    for client in clients:
        if client['room'] == room:
            send_message(client['socket'], "message", message)

def send_message(sock, message_type, payload):
    message = {
        "type": message_type,
        "payload": payload
    }
    message_json = json.dumps(message)
    sock.send(message_json.encode('utf-8'))

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        received_message = json.loads(data)
        message_type = received_message["type"]
        payload = received_message["payload"]

        if message_type == "connect":
            client_info = {
                "socket": client_socket,
                "name": payload["name"],
                "room": payload["room"]
            }
            clients.append(client_info)

            # Acknowledge the connection
            ack_message = {
                "message": "Connected to the room."
            }
            send_message(client_socket, "connect_ack", ack_message)

        elif message_type == "message":
            sender = payload["sender"]
            room = payload["room"]
            text = payload["text"]
            broadcast_message(sender, room, text)


        elif message_type == "upload_file":

            file_name = payload["file_name"]

            file_data_base64 = payload["file_data_base64"]

            # Convert base64-encoded string back to bytes

            file_data = base64.b64decode(file_data_base64.encode('utf-8'))

            # Save the uploaded file to the server media folder

            file_path = os.path.join(SERVER_MEDIA, file_name)

            with open(file_path, 'wb') as file:

                file.write(file_data)

            print(f"User {payload['sender']} uploaded the {file_name} file")


        elif message_type == "download_file":

            file_name = payload["file_name"]

            file_path = os.path.join(SERVER_MEDIA, file_name)

            if os.path.exists(file_path):

                with open(file_path, 'rb') as file:

                    file_data = file.read()

                # Convert file data to base64-encoded string

                file_data_base64 = base64.b64encode(file_data).decode('utf-8')

                download_message = {

                    "file_name": file_name,

                    "file_data_base64": file_data_base64

                }

                send_message(client_socket, "download_file", download_message)

            else:

                response_message = {

                    "message": f"The {file_name} doesn't exist"

                }

                send_message(client_socket, "download_file", response_message)

    # Remove the client from the list
    client_socket.close()
    clients.remove(client_info)


while True:
    client_socket, client_address = server_socket.accept()

    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
