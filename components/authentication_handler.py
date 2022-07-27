from time import sleep

import pyautogui as pyautogui

from providers.configuration_handler import ConfigurationHandler
from providers.driver_handler import DriverHandler


class AuthenticationHandler:
    """
    Static methods which handles logging into LinkedIn platform.

    Methods
    -------
        __request_credentials() -> list[str]:
            Handles credentials acquisition directly from the console stream.
        login():
            Attempts to log in to LinkedIn with the provided credentials, fetches the credentials from endpoints.longin
            in config.json, if empty, calls __request_credentials().
    """

    @staticmethod
    def __request_credentials() -> list[str]:
        """
        Handles credentials acquisition directly from the console stream.

        :returns: The acquired username and password
        :rtype: list[str]
        """
        username = input('Please insert your email or phone number:\n')
        password = pyautogui.password(title='Please insert your password:', mask='*')
        return [username, password]

    @staticmethod
    def login():
        """
        Attempts to log in to LinkedIn with the provided credentials, fetches the credentials from endpoints.longin
        in config.json, if empty, calls __request_credentials().
        """
        login_configuration = ConfigurationHandler.get_configuration()['endpoints']['longin']

        username = login_configuration['username']
        password = login_configuration['password']

        if not username or not password:
            username, password = AuthenticationHandler.__request_credentials()

        driver = DriverHandler.get_driver()
        url = login_configuration['url']

        driver.get(url)

        # Redirected
        if driver.current_url != url:
            return

        username_field = driver.find_element_by_id(login_configuration['usernameElementId'])
        password_field = driver.find_element_by_id(login_configuration['passwordElementId'])

        username_field.send_keys(username)
        password_field.send_keys(password)

        del username
        del password

        username_field.submit()

        sleep(ConfigurationHandler.get_configuration()['securityVerificationDelay'])
