from providers.configuration_handler import ConfigurationHandler
from providers.driver_handler import DriverHandler


class AuthenticationHandler:

    @staticmethod
    def __request_credentials():
        username = input('Please insert your email or phone number\n')
        password = input('Please insert your password\n')
        return [username, password]

    @staticmethod
    def login():
        username, password = AuthenticationHandler.__request_credentials()

        driver = DriverHandler.get_driver()
        login_configuration = ConfigurationHandler.get_configuration()['endpoints']['longin']
        url = login_configuration['url']

        driver.get(url)

        # Redirected
        if driver.current_url != url:
            return

        username_field = driver.find_element_by_id(login_configuration['usernameElementId'])
        password_field = driver.find_element_by_id(login_configuration['passwordElementId'])

        username_field.send_keys(username)
        password_field.send_keys(password)

        username_field.submit()
