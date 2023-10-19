import socket
import configparser

def setup(config_file:str = "config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    client_amount = int(config["server"]['client_amount'])
    port = int(config["server"]['port'])
    return client_amount, port

client_amount , port = setup()
def server_program():
    # get the hostname
    host = socket.gethostname()
    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together
    # configure how many client the server can listen simultaneously
    server_socket.listen(client_amount)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data))
        data = input(' -> ')
        conn.send(data.encode())  # send data to the client

    conn.close()  # close the connection


if __name__ == '__main__':
    server_program()