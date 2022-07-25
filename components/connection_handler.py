from time import sleep
from typing import Union

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from providers.configuration_handler import ConfigurationHandler
from providers.driver_handler import DriverHandler


class ConnectionHandler:

    @staticmethod
    def __connect_to_user():
        raise NotImplementedError

    @staticmethod
    def connect_to_suggestions():
        raise NotImplementedError

    @staticmethod
    def get_suggestions():
        raise NotImplementedError

    @staticmethod
    def connect_to_profile_connections(profile_name: Union[str, list[str]], depth=1):
        raise NotImplementedError

    @staticmethod
    def get_profile_connections(profile_name: Union[str, list[str]], depth=1):
        raise NotImplementedError

    @staticmethod
    def connect_to_company_people(company_name: Union[str, list[str]]):
        raise NotImplementedError

    @staticmethod
    def get_company_people(company_name: Union[str, list[str]]):
        received_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['companyPeople']

        driver = DriverHandler.get_driver()
        url = received_invitations_configuration['url']
        url = url.replace('COMPANY_NAME', company_name)

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, received_invitations_configuration['nameClass'])))

        names = []
        headlines = []
        links = []

        counter = 0
        maximum_connections = ConfigurationHandler.get_configuration()['maximumConnections']
        prev_len = 0

        while counter < maximum_connections or maximum_connections == -1:
            people = driver.find_element_by_class_name(received_invitations_configuration['listClass']) \
                .find_elements_by_tag_name("li")

            for i in range(counter, len(people)):
                try:
                    name = people[i].find_element_by_class_name(received_invitations_configuration['nameClass'])
                    headline = people[i].find_element_by_class_name(received_invitations_configuration['headlineClass'])
                    link = people[i].find_element_by_class_name(received_invitations_configuration['linkClass'])
                except NoSuchElementException:
                    continue

                if name in names:
                    continue

                names.append(name)
                headlines.append(headline)
                links.append(link)

                counter += 1
                if counter >= maximum_connections != -1:
                    break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(received_invitations_configuration['scrollDelay'])

            if prev_len == len(people):
                break
            prev_len = len(people)

        names = [name.get_attribute('innerText') for name in names]
        headlines = [headline.get_attribute('innerText') for headline in headlines]
        links = [link.get_attribute('href') for link in links]

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv(f'./out/Company People - {company_name}.csv', index=False)

    @staticmethod
    def accept_received_invitations():
        received_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['receivedInvitations']

        driver = DriverHandler.get_driver()
        url = received_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, received_invitations_configuration['nameClass'])))

        accept_buttons = driver.find_elements(
            By.XPATH,
            '//*[text()="' + received_invitations_configuration['acceptInnerHTML'] + '"]'
        )

        for accept_button in accept_buttons:
            accept_button.find_element_by_xpath('..').click()
            accept_confirmation_button = driver.find_element(
                By.XPATH,
                '//*[text()="' + received_invitations_configuration['acceptInnerHTML'] + '"]'
            )
            accept_confirmation_button.find_element_by_xpath('..').click()
            sleep(received_invitations_configuration['acceptDelay'])

    @staticmethod
    def ignore_received_invitations():
        received_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['receivedInvitations']

        driver = DriverHandler.get_driver()
        url = received_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, received_invitations_configuration['nameClass'])))

        ignore_buttons = driver.find_elements(
            By.XPATH,
            '//*[text()="' + received_invitations_configuration['ignoreInnerHTML'] + '"]'
        )

        for ignore_button in ignore_buttons:
            ignore_button.find_element_by_xpath('..').click()
            ignore_confirmation_button = driver.find_element(
                By.XPATH,
                '//*[text()="' + received_invitations_configuration['ignoreInnerHTML'] + '"]'
            )
            ignore_confirmation_button.find_element_by_xpath('..').click()
            sleep(received_invitations_configuration['ignoreDelay'])

    @staticmethod
    def get_received_invitations():
        received_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['receivedInvitations']

        driver = DriverHandler.get_driver()
        url = received_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, received_invitations_configuration['nameClass'])))

        names = driver.find_elements_by_class_name(received_invitations_configuration['nameClass'])
        headlines = driver.find_elements_by_class_name(received_invitations_configuration['headlineClass'])
        links = driver.find_elements_by_class_name(received_invitations_configuration['linkClass'])

        names = [name.get_attribute('innerText') for name in names]
        headlines = [headline.get_attribute('innerText') for headline in headlines]
        links = [link.get_attribute('href') for link in links]

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv('./out/Received Invitations.csv', index=False)

    @staticmethod
    def withdraw_sent_invitations():
        sent_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['sentInvitations']

        driver = DriverHandler.get_driver()
        url = sent_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, sent_invitations_configuration['nameClass'])))

        withdraw_buttons = driver.find_elements(
            By.XPATH,
            '//*[text()="' + sent_invitations_configuration['withdrawInnerHTML'] + '"]'
        )

        for withdraw_button in withdraw_buttons:
            withdraw_button.find_element_by_xpath('..').click()
            withdraw_confirmation_button = driver.find_element(
                By.XPATH,
                '//*[text()="' + sent_invitations_configuration['withdrawInnerHTML'] + '"]'
            )
            withdraw_confirmation_button.find_element_by_xpath('..').click()
            sleep(sent_invitations_configuration['withdrawDelay'])

    @staticmethod
    def get_sent_invitations():
        sent_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['sentInvitations']

        driver = DriverHandler.get_driver()
        url = sent_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, sent_invitations_configuration['nameClass'])))

        names = driver.find_elements_by_class_name(sent_invitations_configuration['nameClass'])
        headlines = driver.find_elements_by_class_name(sent_invitations_configuration['headlineClass'])
        links = driver.find_elements_by_class_name(sent_invitations_configuration['linkClass'])

        names = [name.get_attribute('innerText') for name in names]
        headlines = [headline.get_attribute('innerText') for headline in headlines]
        links = [link.get_attribute('href') for link in links]

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv('./out/Sent Invitations.csv', index=False)
