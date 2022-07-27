import json


class ConfigurationHandler:
    """
    Static methods which handles config.json decoding.

    Attributes
    ----------
        __configuration  Acts as a cache for storing the configuration dictionary

    Methods
    -------
        get_configuration() -> dict:
            Provides a dictionary of the configuration.
    """

    __configuration = None

    @staticmethod
    def get_configuration() -> dict:
        """
        Provides a dictionary of the configuration.

        :returns: Configurations as is from config.json file
        :rtype: dict
        """
        if ConfigurationHandler.__configuration is None:
            file = open('./config.json')
            ConfigurationHandler.__configuration = json.load(file)

        return ConfigurationHandler.__configuration.copy()
