import socket
class Client:

    def __init__(self, port:int = 5000):
        self.port = port
    def client_program(self):
        host = socket.gethostname()  # as both code is running on same pc
        client_socket = socket.socket()  # instantiate
        client_socket.connect((host, self.port))  # connect to the server
        message = input(" -> ")  # take input
        while message.lower().strip() != 'bye':
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response
            print('Received from server: ' + data)  # show in terminal
            message = input(" -> ")  # again take input
        client_socket.close()  # close the connection