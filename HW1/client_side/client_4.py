from utils.utilities import Utils
from client_base.client import Client

utils = Utils()
port, time_out = utils.setup()
client = Client(port=port, time_out=time_out)
if __name__ == "__main__":
    client.client_program()