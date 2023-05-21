"""A stupid todo app.

Created http server using only the standard lib w/ socket

What I cannot create, I do not understand
~ Richard Feynman


Warning!: spaghetti & un-extensible code, mainly just for learning
"""


import socket
import threading
import os
from getpass import getpass
import json
import traceback
import select
import html



SERVER_HOST = "0.0.0.0"
SERVER_PORT = 80


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set re-use address option
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER_HOST, SERVER_PORT))
print(f"-> Bind to http://{SERVER_HOST}:{SERVER_PORT}")

server_socket.listen(1)
print("-> Listening...")


# This is a hack to handle Ctrl-c on windows...
# This is because blocking socket functions don't receive the SIGINT signal
def stop_loop(func):
    while True:
        while True:
            try:
                getpass("")
            except (KeyboardInterrupt, Exception) as _:
                print("-> Attempt to gracefully quit...")
                try:
                    func()
                except Exception as e:
                    traceback.print_exception(e)
                    break
                os._exit(0)
threading.Thread(target=stop_loop, args=(server_socket.close,), daemon=True).start()


# Server state
file_cache = {}

# App state
tasks = []
tasks_html = ""

# The event loop
while True:
    client_connection, client_address = server_socket.accept()
    print(f"-> New connection from {client_address[0]}:{client_address[1]}")

    # 100 ms timeout for reading request from client
    ready, _, _ = select.select([client_connection], [], [], 0.1)
    if not ready:
        print("-> Timeout!")
        client_connection.close()
        continue

    request = client_connection.recv(1024).decode()
    print(request)

    reqtype, file, _ = request.splitlines()[0].split()
    if file == "/":
        file = "/index.html"

    responce = "HTTP/1.1 200 OK\r\n\r\n"
    if reqtype == "GET":
        try:
            content = ""
            if file in file_cache:
                content = file_cache[file]
            else:
                with open(f"./todo{file}") as f:
                    content = f.read()
                    file_cache[file] = content
            if file == "/index.html":  # Server-side rendering
                content = content.replace("{{tasks}}", tasks_html)
            responce += content
        except FileNotFoundError:
            responce = "HTTP/1.1 404 Not Found\r\n\r\nNot Found"
    elif reqtype == "POST":
        if file == "/add":
            request_body = request[request.index("\r\n\r\n") + 4:]
            task = json.loads(request_body)["item-content"]
            task = html.escape(task)  # prevent XSS attack
            task_html = f"<li>{task}</li>\r\n"
            tasks.append(task)
            tasks_html = task_html + tasks_html

    client_connection.sendall(responce.encode())
    client_connection.close()
