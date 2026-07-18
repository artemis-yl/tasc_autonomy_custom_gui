import socket
import json
import threading
import sys

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    buffer = ""
    
    # Set a timeout on the client socket as well so it doesn't block forever
    client_socket.settimeout(0.5)
    
    try:
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            command = json.loads(line)
                            print(f"\n[RECEIVED DATA] Processing camera request:")
                            print(json.dumps(command, indent=4))
                            
                            state = command.get("state")
                            camera = command.get("camera")
                            
                            response = {"status": "success", "msg": f"Command '{state}' executed for {camera}"}
                            client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                            
                        except json.JSONDecodeError:
                            print(f"[ERROR] Malformed line: {line}")
            except socket.timeout:
                # Loop back to let the thread check if the system is shutting down
                continue
    except ConnectionResetError:
        print(f"[DISCONNECT] Lost connection with {client_address}.")
    finally:
        client_socket.close()

def start_server(host="127.0.0.1", port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    
    # This is the secret sauce: stops server.accept() from blocking forever
    server.settimeout(0.5)
    
    print(f"[LISTENING] Mock Server is running on {host}:{port}. Press Ctrl+C to stop.")
    
    try:
        while True:
            try:
                client_sock, client_addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(client_sock, client_addr))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                # Briefly yields so Python can register your Ctrl+C
                continue
    except KeyboardInterrupt:
        print("\n[SHUTTING DOWN] Closing server.")
    finally:
        server.close()
        sys.exit(0)

if __name__ == "__main__":
    start_server()