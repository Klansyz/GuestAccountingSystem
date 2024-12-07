import configparser


def load_config(config_path="config.ini"):
    """
    Загружает конфигурацию из указанного файла.
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


# Загружаем конфигурацию при инициализации
CONFIG = load_config()
DB_PATH = CONFIG["Paths"]["database_path"]
