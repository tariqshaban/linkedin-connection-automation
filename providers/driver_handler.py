from selenium import webdriver
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.chrome import ChromeDriverManager

from enums.web_drivers import WebDrivers
from providers.configuration_handler import ConfigurationHandler


class DriverHandler:
    __driver = None

    @staticmethod
    def get_driver():
        if DriverHandler.__driver is None:
            web_driver = ConfigurationHandler.get_configuration()['webDriver']
            if web_driver == WebDrivers.INTERNET_EXPLORER.value:
                DriverHandler.__driver = webdriver.Ie(IEDriverManager().install())
            elif web_driver == WebDrivers.EDGE.value:
                DriverHandler.__driver = webdriver.Edge(EdgeChromiumDriverManager().install())
            elif web_driver == WebDrivers.FIREFOX.value:
                DriverHandler.__driver = webdriver.Firefox(GeckoDriverManager().install())
            elif web_driver == WebDrivers.OPERA.value:
                DriverHandler.__driver = webdriver.Opera(OperaDriverManager().install())
            else:
                DriverHandler.__driver = webdriver.Chrome(ChromeDriverManager().install())
            DriverHandler.__driver.maximize_window()

        return DriverHandler.__driver
