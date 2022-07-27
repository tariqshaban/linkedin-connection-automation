from enum import Enum


class WebDrivers(Enum):
    """
    Enumerate web driver types.
    """
    INTERNET_EXPLORER = 'internet explorer'
    EDGE = 'edge'
    FIREFOX = 'firefox'
    OPERA = 'opera'
    CHROME = 'chrome'
