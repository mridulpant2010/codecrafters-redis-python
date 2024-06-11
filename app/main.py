# Uncomment this to pass the first stage
import socket


def main(HOST,PORT):
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    #server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    #
    with socket.create_server((HOST,PORT),reuse_port=True) as server_socket:
        conn, address = server_socket.accept()
        while True:
            data = conn.recv(1024).decode()
            print("data is ", data)
            response = b"+PONG\r\n"
            #try:
                # result = data.split("\n")
                # for each_re in result:
            if "PING" in data:
                conn.sendall(response)
            # except Exception as e:
            #     response = None
        conn.close()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 6379
    main(HOST,PORT)
