import configparser


class Utils:
    def __init__(self):
        pass

    def setup(self, config_file: str = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)
        time_out = int(config["client"]["time_out"])
        port = int(config["client"]["port"])
        return port, time_out
