import configparser


def load_config(config_path="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


CONFIG = load_config()
DB_PATH = CONFIG["Paths"]["database_path"]
