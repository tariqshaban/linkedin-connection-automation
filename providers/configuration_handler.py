import json


class ConfigurationHandler:
    __configuration = None

    @staticmethod
    def get_configuration():
        if ConfigurationHandler.__configuration is None:
            file = open('./config.json')
            ConfigurationHandler.__configuration = json.load(file)

        return ConfigurationHandler.__configuration.copy()
