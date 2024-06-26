import socket
import threading
import time
import argparse
from urllib import request


# what is asyncore library and how is it useful?
# lot of folks have used async functions and mututal exclusion, is it really necessary?


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
            elif "info" in data.lower():
                server_type = f"role:{REPLICAOF}\n"
                replication_id = f"master_replid:{repl_id}\n"
                replication_offset = f"master_repl_offset:{repl_offset}\n"
                response = server_type + replication_id + replication_offset
                response = f"${len(response)}{CRLF}{response}{CRLF}".encode()
                # {replication_id}{CRLF}{replication_offset}{CRLF}".encode()
            elif "replconf" in data.lower():
                response = f"+OK{CRLF}".encode()
            elif "psync" in data.lower():
                response = []
                res = f"+FULLRESYNC {repl_id} {repl_offset}{CRLF}".encode()
                response.append(res)

                rdb_content = bytes.fromhex(rdb_hex)
                rdb_data = f"${len(rdb_content)}{CRLF}".encode()
                response.append(rdb_data + rdb_content)
            else:
                response = f"+PONG{CRLF}".encode()
        except KeyError:
            response = f"$-1{CRLF}".encode()
        if isinstance(response, list):
            for each_re in response:
                conn.sendall(each_re)
        else:
            conn.sendall(response)
    conn.close()


def send_request(soc, request):
    soc.sendall(request)
    soc.recv(1024).decode()


def connect_to_master_server():
    try:
        if args.replicaof:
            host, port = args.replicaof.split(" ")
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # understand this
            soc.connect((host, int(port)))
            request = f"*1{CRLF}$4{CRLF}PING{CRLF}".encode()
            send_request(soc, request)
            # REPLCONF
            request = f"*3{CRLF}$8{CRLF}REPLCONF{CRLF}$14{CRLF}listening-port{CRLF}$4{CRLF}{PORT}{CRLF}".encode()
            send_request(soc, request)
            request = f"*3{CRLF}$8{CRLF}REPLCONF{CRLF}$4{CRLF}capa{CRLF}$6{CRLF}psync2{CRLF}".encode()
            send_request(soc, request)

            request = (
                f"*3{CRLF}$5{CRLF}PSYNC{CRLF}$1{CRLF}?{CRLF}$2{CRLF}-1{CRLF}".encode()
            )
            send_request(soc, request)
    except socket.error as err:
        print(f"Socket creation failed with error: {err}")


def main():

    print("Logs from your program will appear here!")
    with socket.create_server((HOST, PORT), reuse_port=True) as server_socket:
        while True:
            conn, _ = server_socket.accept()
            thread = threading.Thread(target=handle_connection, args=(conn,))
            thread.start()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    CRLF = "\r\n"

    rdb_hex = "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d62697473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
    repl_id = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
    repl_offset = "0"

    parser = argparse.ArgumentParser(description="a command line example")
    parser.add_argument(
        "--port",
        dest="port",
        action="store",
        type=int,
        default=6379,
        help="port for the server to run",
    )
    parser.add_argument(
        "--replicaof",
        dest="replicaof",
        action="store",
        type=str,
        help="provides host and port of the master redis server",
    )
    args = parser.parse_args()

    PORT = args.port
    REPLICAOF = "slave" if args.replicaof else "master"

    hash = Hash()
    connect_to_master_server()
    main()
