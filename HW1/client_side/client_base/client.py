import datetime
import socket
import json
import sys
import threading
import time
sys.path.append("../")
from common.resources import Keys


class Client(Keys):
    def __init__(self, port: int = 5000):
        super().__init__()
        self.port = port
        self.data_saved = []
        self.time_start = None
        self.time_out = 5

    def client_program(self) -> None:
        host = socket.gethostname()
        client_socket = socket.socket()
        client_socket.connect((host, self.port))
        try:
            t1 = threading.Thread(target=self.handler, args=(client_socket,))
            t2 = threading.Thread(target=self.set_input, args=(client_socket,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        except Exception as e:
            print("ERROR : ", e)
            # Handle the exception if any error occurs
        client_socket.close()

    def search_id(self, id: int) -> bool:
        if id in [item["id"] for item in self.data_saved]:
            return True
        return False

    def get_data(self, id: int) -> dict:
        return [item for item in self.data_saved if item["id"] == id][0]

    def check_state(self, input: dict = None) -> str:
        return input["state"]

    def listener(self, client_socket):
        data = ""
        received_data = client_socket.recv(1024).decode()
        if not received_data:
            return None
        data += received_data
        json_data = json.loads(received_data)
        return json_data

    def set_input(self, client_socket):
        while True:
            if self.time_start is None:
                id = int(input("Enter the id of data > "))
                if self.search_id(id):
                    print("\nData exist in this client\n")
                else:
                    print("\nWaiting ...\n")
                    self.time_start = datetime.datetime.now().second
                    client_socket.send(
                        json.dumps({"state": self.SEARCH_STATE, "id": id}).encode("utf-8")
                    )
            elif datetime.datetime.now().second - self.time_start > 5:
                print("\nSorry time out data not found :(\n")
                self.time_start = None



    def handler(self, client_socket):
        while True:
            try:
                json_data = self.listener(client_socket=client_socket)
                if json_data is None:
                    return
                print("\ndata receive from server ... \n", json_data)
                if self.check_state(json_data) == self.INIT_STATE:
                    print("\ndata saved in memory : \n", json_data)
                    self.data_saved = json_data["data"]
                elif self.check_state(json_data) == self.SEARCH_STATE:
                    id = int(json_data["data"])
                    if self.search_id(id):
                        client_socket.send(
                            json.dumps(
                                {
                                    "state": self.RESPONSE,
                                    "data": self.get_data(id),
                                    "address": json_data["address"],
                                    "status": self.OK
                                }
                            ).encode("utf-8")
                        )
                    else:
                        client_socket.send(
                            json.dumps(
                                {"state": self.RESPONSE, "data": "", "status": self.NOT_FOUND}
                            ).encode("utf-8")
                        )
                if self.check_state(json_data) == self.RESPONSE:
                    self.time_start = None
                    print(
                        "\ndata found :) ",
                        json_data["data"],
                        "\nin client {address}".format(address=json_data["address"]),
                    )
            except Exception as e:
                print("\nERROR in handler client : ", e)
