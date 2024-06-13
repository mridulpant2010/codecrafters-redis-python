import socket
import threading
import time


# what is asyncore library and how is it useful?


class RedisError(Exception):
    pass


class Redis:

    def parse_response(self, input_string):
        """_summary_
            + : denotes the simple string
            $ denotes the bulk string
            * denotes the array
            : denotes the integer
            - denotes the error
            . denotes the null byte
        Args:
            input_string (_type_): _description_
        """
        self.input_string = input_string
        intermediate_data = self.input_string[1:].strip()
        prefix = self.input_string[0]
        if prefix == "+":
            # return string
            return intermediate_data
        elif prefix == ":":
            # handle integers
            print("intermediate is:", intermediate_data)
            return int(intermediate_data)
        elif prefix == "-":
            raise RedisError(
                f"Redis Error {intermediate_data}"
            )  # it should return something else as well, right?
        elif prefix == "$":
            length, data = intermediate_data.split(CRLF, 1)
            return data[: int(length)]
        elif prefix == "*":
            length, rest_data = intermediate_data.split(CRLF, 1)
            elements = []
            for _ in range(int(length)):
                print("rest_data is: ", rest_data)
                el, rest_data = self.parse_response(rest_data)
                elements.append(el)
            return elements


class Hash:
    def __init__(self, expire=None):
        self.expiry = expire
        self.expire_factor = None
        self.hash = {}

    def set(self, key, value):
        self.hash[key] = value

    def get(self, key):
        return self.hash[key]


def handle_connection(conn):
    while True:
        data = conn.recv(1024).decode()
        if data == b"":
            break
        response_data = data.split(CRLF)
        try:
            if "echo" in data.lower():
                response_data = response_data[-2]
                response = f"+{response_data}{CRLF}".encode()
            elif "set" in data.lower():
                hash.set(response_data[4], response_data[6])

                if "px" in data.lower():
                    hash.expiry = time.time()
                    hash.expire_factor = int(response_data[10])
                response = f"+OK{CRLF}".encode()
            elif "get" in data.lower():
                ans = hash.get(response_data[4])
                if (
                    hash.expiry
                    and (time.time() - hash.expiry) * 1000 > hash.expire_factor
                ):
                    raise KeyError
                response = f"${len(ans)}{CRLF}{ans}{CRLF}".encode()
            else:
                response = f"+PONG{CRLF}".encode()
        except KeyError:
            response = f"$-1{CRLF}".encode()
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
    CRLF = "\r\n"

    hash = Hash()

    main()
