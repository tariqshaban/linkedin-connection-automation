from typing import Union


class ConnectionHandler:

    @staticmethod
    def connect_to_suggestion():
        raise NotImplementedError

    @staticmethod
    def connect_to_all_profile_connections(profile_name: Union[str, list[str]]):
        raise NotImplementedError

    @staticmethod
    def get_profile_connections(profile_name: Union[str, list[str]]):
        raise NotImplementedError
