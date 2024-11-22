# Import necessary libraries
import csv
import os
import pandas as pd
import re
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Exception handling
class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def initialise_driver(chromedriverfilepath: str, headlessflg: bool = False):
    """
    This function takes in the filepath pointing to the chromedriver.exe file
    and initialise the chromium web driver, taking into consideration whether
    headless or otherwise

    Args:
    ----------
    chromedriverfilepath (str) : absolute file path pointing to the chromedriver.exe file
    headlessflg (boolean) : determines whether driver is initialised in headless
                            mode. The default is False.

    Raises
    ------
    MyError : Inform user that Chrome Webdriver file path cannot be located
    Returns
    -------
    driver (object) : webdriver
    """
    if os.path.exists(chromedriverfilepath):
        # Tune setup options
        options = Options()
        options.headless = headlessflg  # Decides whether headless mode or not
        # options.add_argument("--window-size=1920,1080")  # Define the window size of the browser 1920x1080 px
        options.add_argument("--start-maximized")  # maximise the browser window
        cService = webdriver.ChromeService(executable_path=chromedriverfilepath)
        driver = webdriver.Chrome(options=options, service=cService)
        return driver
    else:
        raise MyError("Unable to locate Chrome Webdriver filepath")


if __name__ == "__main__":
    pass
