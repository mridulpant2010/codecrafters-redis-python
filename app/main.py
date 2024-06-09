# Uncomment this to pass the first stage
import socket


def main(HOST,PORT):
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    #server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    #connection, address = server_socket.accept()
    with socket.create_connection((HOST,PORT)) as conn:
        data = conn.recv(1024).decode()
        print("data is ", data)
        response = ""
        try:
            result = data.split("\r\n")
            if "PING" in result:
                response = f"+PONG\r\n"
        except Exception as e:
            response = None

        conn.sendall(response.encode())
        conn.close()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 6379
    main(HOST,PORT)
