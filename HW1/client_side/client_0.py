from utils.utilities import Utils
from client_base.client import Client

utils = Utils()
port = utils.setup()
client = Client(port=port)

if __name__ == "__main__":
    client.client_program()
