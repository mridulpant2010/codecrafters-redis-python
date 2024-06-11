import socket
import threading


def handle_connection(conn):
    while True:
        data = conn.recv(1024).decode()
        response = b"+PONG\r\n"
        if response == b"PONG":
            break
        if "PING" in data:
            conn.sendall(response)
    conn.close()


def main():
    print("Logs from your program will appear here!")
    with socket.create_server((HOST, PORT), reuse_port=True) as server_socket:
        while True:
            conn, _ = server_socket.accept()
            thread = threading.Thread(target=handle_connection, args=(conn,))
            thread.start()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 6379
    main()


# one conn and we have multiple request from a single client.

# with socket.create_server((HOST,PORT),reuse_port=True) as server:
#     conn,add = server.accept()
#     while True:
#         data = conn.recv(1024).decode()
#         print("data is "+data)
#         if data == b"":
#             break
#         response = b"+PONG\r\n"
#         conn.sendall(response)
#     conn.close()

# multiple connection and multiple requests from multiple clients.
