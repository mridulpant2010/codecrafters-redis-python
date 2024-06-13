import socket
import threading

#what is asyncore library and how is it useful?

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
            print("intermediate is:",intermediate_data)
            return int(intermediate_data)
        elif prefix == "-":
            raise RedisError(f"Redis Error {intermediate_data}") # it should return something else as well, right?
        elif prefix == "$":
            length,data = intermediate_data.split(CRLF,1)
            return data[:int(length)]
        elif prefix == "*":
            length, rest_data = intermediate_data.split(CRLF,1)
            elements=[]
            for _ in range(int(length)):
                print("rest_data is: ",rest_data)
                el ,rest_data = self.parse_response(rest_data)
                elements.append(el)    
            return elements
                                    
# line = "$12\r\n*3\r\n:1\r\n:2\r\n:3\r\n\r\n"
# line.split("\r\n",1)
def handle_connection(conn):
    while True:
        data = conn.recv(1024).decode()
        response = b"+PONG\r\n"
        if data == b"":
            break
        if "PING" in data:
            conn.sendall(response)
        
        if "echo" in data.lower():
            response_data=data.split(CRLF)[-2]
            response = f"+{response_data}{CRLF}".encode()
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
    main()
    # parser = Redis()
    # response = "*3\r\n:1\r\n:2\r\n:3\r\n"
    # #response = "*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n"
    # parsed_data = parser.parse_response(response)
    # print(parsed_data)