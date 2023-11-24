import json
import socket
import configparser
import pandas as pd
import os
import numpy as np
from HW1.common.resources import Keys
import threading

k = Keys()


def read_data(file_name: str = "data.csv"):
    df = pd.read_csv(os.path.join(os.getcwd(), file_name), skipinitialspace=True)
    # Remove single quotes from column names
    df.columns = df.columns.str.replace("'", "")
    # Remove single quotes from data values
    df = df.apply(lambda x: x.str.replace("'", "") if x.dtype == "object" else x)
    df["id"] = df["id"].astype(int)
    return df


def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = " ".join(format(ord(letter), "b") for letter in str)
    return binary


def convert_data_frame_to_json_format(df: pd.DataFrame):
    df["json"] = df.apply(lambda x: x.to_json(), axis=1)
    data = df["json"].values
    if isinstance(data, np.ndarray):
        data = data.tolist()
        data = [json.loads(item) for item in data]
        return data
    raise Exception("type is not np.ndarray")


def setup(config_file: str = "config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    client_amount = int(config["server"]["client_amount"])
    port = int(config["server"]["port"])
    return client_amount, port


client_amount, port = setup()


def handler(connections, conn, data):
    while True:
        received_data = conn["conn"].recv(1024).decode()
        if not received_data:
            return
        data += received_data
        json_data = json.loads(received_data)
        if json_data["state"] == k.SEARCH_STATE:
            for c in connections:
                if conn["addr"] is not c["addr"]:
                    c["conn"].send(
                        json.dumps(
                            {
                                "state": k.SEARCH_STATE,
                                "data": json_data["id"],
                                "address": conn["addr"],
                            }
                        ).encode("utf-8")
                    )
        elif json_data["state"] == k.RESPONSE:
            if json_data["status"] is k.OK:
                for c in connections:
                    if (
                        c["addr"][0] == json_data["address"][0]
                        and c["addr"][1] == json_data["address"][1]
                    ):
                        c["conn"].send(
                            json.dumps(
                                {
                                    "state": k.RESPONSE,
                                    "data": json_data["data"],
                                    "address": c["addr"],
                                    "status": k.OK,
                                }
                            ).encode("utf-8")
                        )


def server_program():
    # get the hostname
    host = socket.gethostname()
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(client_amount)
    connections = []
    print("Server started. Waiting for connections...")
    for _ in range(client_amount):
        conn, address = server_socket.accept()
        print("Connection from: " + str(address))
        connections.append({"conn": conn, "addr": address})
    data = convert_data_frame_to_json_format(read_data("RandomData.csv"))
    data_per_client = len(data) // client_amount
    for i, conn in enumerate(connections):
        start_index = i * data_per_client
        end_index = (i + 1) * data_per_client if i < client_amount - 1 else len(data)
        batch_data = data[start_index:end_index]
        data_json = {"state": k.INIT_STATE, "data": batch_data}
        data_json = json.dumps(data_json)
        data_bytes = data_json.encode("utf-8")
        conn["conn"].send(data_bytes)  # send data batch to the client
        print(
            "Sent batch {count} to client with address {addr}".format(
                count=i + 1, addr=conn["addr"]
            )
        )
    try:
        thread_list = []
        for i in range(client_amount):
            thread_list.append(threading.Thread(target=handler, args=(connections, connections[i], data)))
        for item in thread_list:
            item.start()
        for item in thread_list:
            item.join()
    except Exception as e:
        # Handle the exception if any error occurs
        print("ERROR : ", e)

    server_socket.close()  # close the server socket


if __name__ == "__main__":
    server_program()
