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
    """
    Static methods which handles various connection procedures in LinkedIn.

    Methods
    -------
        __connect_to_user(url: Union[str, list[str]]):
            Connects to a specified user(s).
        handle_suggestions(connect: bool = False):
            Iterates through profiles in the `suggestions section <SUGGESTIONS_>`_.
        handle_people_search(connect: bool = False):
            Iterates through profiles in the `search page <PEOPLE_SEARCH_>`_.
        __handle_profile_connections(profile_name: str, accumulated_links: list[str], connect: bool = False, depth: int = 1):
            Recursively iterate through profiles per specified user(s) in the `search page (with filters)
            <PROFILE_CONNECTIONS_>`_.
        handle_profile_connections(connect: bool = False, depth: int = 1):
            Recursively iterate through profiles per specified user(s) in the `search page (with filters)
            <PROFILE_CONNECTIONS_>`_.
        handle_company_people(connect: bool = False):
            Iterates through profiles working in a specified company(s).
        handle_received_invitations(accept: bool = False, ignore: bool = False):
            Iterates through profiles in the `received invitations page <RECEIVED_INVITATIONS_>`_.
        handle_sent_invitations(withdraw: bool = False):
            Iterates through profiles in the `sent invitations page <SENT_INVITATIONS_>`_.

    .. _SUGGESTIONS: https://www.linkedin.com/mynetwork/
    .. _PEOPLE_SEARCH: https://www.linkedin.com/search/results/people/
    .. _PROFILE_CONNECTIONS: https://www.linkedin.com/search/results/people/
    .. _RECEIVED_INVITATIONS: https://www.linkedin.com/mynetwork/invitation-manager/
    .. _SENT_INVITATIONS: https://www.linkedin.com/mynetwork/invitation-manager/sent/
    """

    @staticmethod
    def __connect_to_user(url: Union[str, list[str]]):
        """
        Connects to a specified user(s).

        :param Union[str, list[str]] url: Specify which user to connect to by their URL
        """
        user_configuration = ConfigurationHandler.get_configuration()['endpoints']['profile']

        driver = DriverHandler.get_driver()

        urls = []

        if isinstance(url, str):
            urls.append(url)
        else:
            urls = url

        for url in urls:
            driver.execute_script('window.open("' + url + '");')
            driver.switch_to.window(driver.window_handles[-1])

            accept_button = driver.find_elements(
                By.XPATH,
                '//*[text()="' + user_configuration['connectInnerHTML'] + '"]'
            )[1].find_element(By.XPATH, '..')

            driver.execute_script('arguments[0].click();', accept_button)

            try:
                connect_confirmation_button = driver.find_element(
                    By.XPATH,
                    '//*[text()="' + user_configuration['confirmInnerHTML'] + '"]'
                )
                connect_confirmation_button.find_element(By.XPATH, '..').click()
            except (Exception,):
                connect_button_reason = driver.find_element(
                    By.XPATH,
                    '//*[text()="' + user_configuration['otherInnerHTML'] + '"]'
                )
                connect_button_reason.click()

                connect_button = driver.find_element(
                    By.XPATH,
                    '//*[text()="' + user_configuration['connectInnerHTML'] + '"]'
                )
                connect_button.find_element(By.XPATH, '..').click()

                connect_confirmation_button = driver.find_element(
                    By.XPATH,
                    '//*[text()="' + user_configuration['confirmInnerHTML'] + '"]'
                )
                connect_confirmation_button.find_element(By.XPATH, '..').click()

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            sleep(user_configuration['closeDelay'])

    @staticmethod
    def handle_suggestions(connect: bool = False):
        """
        Iterates through profiles in the `suggestions section <SUGGESTIONS_>`_.

        :param bool connect: Specify whether to connect to the retrieved list of profiles or not

        .. _SUGGESTIONS: https://www.linkedin.com/mynetwork/
        """
        suggestions_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['suggestions']

        driver = DriverHandler.get_driver()

        url = suggestions_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, suggestions_configuration['nameClass'])))

        names = []
        headlines = []
        links = []

        counter = 0
        maximum_connections = ConfigurationHandler.get_configuration()['maximumConnections']
        prev_len = 0

        while len(names) < maximum_connections or maximum_connections == -1:
            suggestion_section = driver.find_element(
                By.XPATH,
                '//*[text()="' + suggestions_configuration['headerInnerHTML'] + '"]'
            ).find_element(By.XPATH, '..').find_element(By.XPATH, '..')
            people = suggestion_section.find_element(By.CLASS_NAME, suggestions_configuration['listClass']) \
                .find_elements(By.TAG_NAME, 'li')

            for i in range(counter, len(people)):
                counter += 1

                name = people[i] \
                    .find_element(By.CLASS_NAME, suggestions_configuration['nameClass']) \
                    .get_attribute('innerText')
                headline = people[i] \
                    .find_element(By.CLASS_NAME, suggestions_configuration['headlineClass']) \
                    .get_attribute('innerText')
                link = people[i] \
                    .find_element(By.CLASS_NAME, suggestions_configuration['linkClass']) \
                    .get_attribute('href')

                if connect:
                    button = people[i].find_elements(By.TAG_NAME, 'button')[-1]
                    button.click()
                    sleep(suggestions_configuration['connectDelay'])

                names.append(name)
                headlines.append(headline)
                links.append(link)

                if len(names) >= maximum_connections != -1:
                    break

            if prev_len == len(people):
                if driver.execute_script('(window.innerHeight + window.scrollY) >= document.body.scrollHeight'):
                    break
                else:
                    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

            prev_len = len(people)

            sleep(suggestions_configuration['scrollDelay'])

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv(f'./out/Suggestions.csv', index=False)

    @staticmethod
    def handle_people_search(connect: bool = False):
        """
        Iterates through profiles in the `search page <PEOPLE_SEARCH_>`_.

        :param bool connect: Specify whether to connect to the retrieved list of profiles or not

        .. _PEOPLE_SEARCH: https://www.linkedin.com/search/results/people/
        """
        people_search_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['peopleSearch']

        driver = DriverHandler.get_driver()

        names = []
        headlines = []
        links = []

        counter = 0
        pagination = 1
        pagination_threshold = 100
        maximum_connections = ConfigurationHandler.get_configuration()['maximumConnections']

        while (len(names) < maximum_connections or maximum_connections == -1) and pagination <= pagination_threshold:
            driver.get(f'{people_search_configuration["url"]}'
                       f'?{people_search_configuration["paginationURL"]}={pagination}')
            pagination += 1

            WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, people_search_configuration['buttonClass'])
                ))

            people = driver.find_element(By.CLASS_NAME, people_search_configuration['listClass']) \
                .find_elements(By.TAG_NAME, 'li')

            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(people_search_configuration['buttonRenderDelay'])

            pagination_threshold = \
                int(driver.find_element(By.CLASS_NAME, people_search_configuration['paginationInnerHTML'])
                    .find_elements(By.TAG_NAME, 'li')[-1]
                    .find_elements(By.CSS_SELECTOR, '*')[0]
                    .find_elements(By.CSS_SELECTOR, '*')[0]
                    .get_attribute('innerText'))

            driver.execute_script('window.scrollTo(0, 0);')

            for person in people:
                counter += 1

                name = person \
                    .find_element(By.CLASS_NAME, people_search_configuration['nameClass']) \
                    .find_elements(By.CSS_SELECTOR, '*')[0] \
                    .find_elements(By.CSS_SELECTOR, '*')[0] \
                    .find_elements(By.CSS_SELECTOR, '*')[0] \
                    .find_elements(By.CSS_SELECTOR, '*')[0] \
                    .get_attribute('innerText')
                headline = person \
                    .find_element(By.CLASS_NAME, people_search_configuration['headlineClass']) \
                    .get_attribute('innerText')
                link = person \
                    .find_element(By.CLASS_NAME, people_search_configuration['linkClass']) \
                    .find_elements(By.CSS_SELECTOR, '*')[0] \
                    .find_elements(By.CSS_SELECTOR, '*')[0] \
                    .get_attribute('href').split('?')[0]

                if connect:
                    button = person.find_element(By.TAG_NAME, 'button')
                    button_text = button.find_element(By.TAG_NAME, 'span').get_attribute('innerText')
                    if button_text == people_search_configuration['connectInnerHTML']:
                        button.click()
                        connect_confirmation_button = driver.find_element(
                            By.XPATH,
                            '//*[text()="' + people_search_configuration['confirmInnerHTML'] + '"]'
                        )
                        connect_confirmation_button.find_element(By.XPATH, '..').click()
                        sleep(people_search_configuration['connectDelay'])
                    elif button_text == people_search_configuration['messageInnerHTML'] or \
                            button_text == people_search_configuration['followInnerHTML']:
                        ConnectionHandler.__connect_to_user(url=link)
                    else:
                        continue

                names.append(name)
                headlines.append(headline)
                links.append(link)

                if len(names) >= maximum_connections != -1:
                    break

            sleep(people_search_configuration['paginationDelay'])

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv(f'./out/People Search.csv', index=False)

    @staticmethod
    def __handle_profile_connections(profile_name: str, accumulated_links: list[str], connect: bool = False,
                                     depth: int = 1):
        """
        Recursively iterate through profiles per specified user(s) in the `search page (with filters)
        <PROFILE_CONNECTIONS_>`_.

        :param str profile_name: Specify which profile name to view their connections
        :param list[str] accumulated_links: Accumulate handled links to avoid infinite callbacks
               (when an already processed profile gets processed again at a different depth)
        :param bool connect: Specify whether to connect to the retrieved list of profiles or not
        :param int depth: Specify the depth of the recursion, that is, the depth of connecting to a profile's
                          connections who is a connection to the root profile (set to one for no recursion)

        .. _PROFILE_CONNECTIONS: https://www.linkedin.com/search/results/people/
        """
        profile_connections_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['profileConnections']

        driver = DriverHandler.get_driver()

        profiles = [profile_name]

        for profile in profiles:
            url = profile_connections_configuration['url']
            url = url.replace('PROFILE_NAME', profile)
            driver.get(url)

            WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, profile_connections_configuration['connectionsIndicatorClass'])
                ))

            try:
                url = driver \
                    .find_element(By.CLASS_NAME, profile_connections_configuration['connectionsIndicatorClass']) \
                    .find_element(By.TAG_NAME, 'a') \
                    .get_attribute('href')
                url = url[0:url.index(profile_connections_configuration['degreeQueryString'])]
            except NoSuchElementException:
                continue

            names = []
            headlines = []
            links = []

            counter = 0
            pagination = 1
            pagination_threshold = 100
            maximum_connections = ConfigurationHandler.get_configuration()['maximumConnections']

            while (len(names) < maximum_connections or maximum_connections == -1) \
                    and pagination <= pagination_threshold:
                driver.get(f'{url}&{profile_connections_configuration["paginationURL"]}={pagination}')
                pagination += 1

                WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, profile_connections_configuration['buttonClass'])
                    ))

                people = driver.find_element(By.CLASS_NAME, profile_connections_configuration['listClass']) \
                    .find_elements(By.TAG_NAME, 'li')

                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(profile_connections_configuration['buttonRenderDelay'])

                pagination_threshold = \
                    int(driver.find_element(By.CLASS_NAME, profile_connections_configuration['paginationInnerHTML'])
                        .find_elements(By.TAG_NAME, 'li')[-1]
                        .find_elements(By.CSS_SELECTOR, '*')[0]
                        .find_elements(By.CSS_SELECTOR, '*')[0]
                        .get_attribute('innerText'))

                driver.execute_script('window.scrollTo(0, 0);')

                for person in people:
                    counter += 1

                    name = person \
                        .find_element(By.CLASS_NAME, profile_connections_configuration['nameClass']) \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .get_attribute('innerText')
                    headline = person \
                        .find_element(By.CLASS_NAME, profile_connections_configuration['headlineClass']) \
                        .get_attribute('innerText')
                    link = person \
                        .find_element(By.CLASS_NAME, profile_connections_configuration['linkClass']) \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .get_attribute('href').split('?')[0]

                    if depth - 1 > 0 and link not in accumulated_links:
                        driver.execute_script('window.open("");')
                        driver.switch_to.window(driver.window_handles[-1])
                        accumulated_links.append(link)
                        ConnectionHandler.__handle_profile_connections(connect=connect,
                                                                       depth=depth - 1,
                                                                       profile_name=link[link.rindex('/') + 1:],
                                                                       accumulated_links=accumulated_links)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[-1])

                    if connect:
                        button = person.find_element(By.TAG_NAME, 'button')
                        button_text = button.find_element(By.TAG_NAME, 'span').get_attribute('innerText')
                        if button_text == profile_connections_configuration['connectInnerHTML']:
                            button.click()
                            connect_confirmation_button = driver.find_element(
                                By.XPATH,
                                '//*[text()="' + profile_connections_configuration['confirmInnerHTML'] + '"]'
                            )
                            connect_confirmation_button.find_element(By.XPATH, '..').click()
                            sleep(profile_connections_configuration['connectDelay'])
                        elif button_text == profile_connections_configuration['messageInnerHTML'] or \
                                button_text == profile_connections_configuration['followInnerHTML']:
                            ConnectionHandler.__connect_to_user(url=link)
                        else:
                            continue

                    names.append(name)
                    headlines.append(headline)
                    links.append(link)

                    if len(names) >= maximum_connections != -1:
                        break

                sleep(profile_connections_configuration['paginationDelay'])

            df = pd.DataFrame(
                {'Name': names,
                 'HeadLine': headlines,
                 'Link': links
                 })

            df.to_csv(f'./out/{profile} Connections.csv', index=False)

    @staticmethod
    def handle_profile_connections(connect: bool = False, depth: int = 1):
        """
        Recursively iterate through profiles per specified user(s) in the `search page (with filters)
        <PROFILE_CONNECTIONS_>`_.

        :param bool connect: Specify whether to connect to the retrieved list of profiles or not
        :param int depth: Specify the depth of the recursion, that is, the depth of connecting to a profile's
                          connections who is a connection to the root profile (set to one for no recursion)

        .. _PROFILE_CONNECTIONS: https://www.linkedin.com/search/results/people/
        """
        profile_connections_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['profileConnections']

        driver = DriverHandler.get_driver()

        profiles = ConfigurationHandler.get_configuration()['profileNames']

        for profile in profiles:
            url = profile_connections_configuration['url']
            url = url.replace('PROFILE_NAME', profile)
            driver.get(url)

            WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, profile_connections_configuration['connectionsIndicatorClass'])
                ))

            try:
                url = driver \
                    .find_element(By.CLASS_NAME, profile_connections_configuration['connectionsIndicatorClass']) \
                    .find_element(By.TAG_NAME, 'a') \
                    .get_attribute('href')
                url = url[0:url.index(profile_connections_configuration['degreeQueryString'])]
            except NoSuchElementException:
                continue

            names = []
            headlines = []
            links = []

            counter = 0
            pagination = 1
            pagination_threshold = 100
            maximum_connections = ConfigurationHandler.get_configuration()['maximumConnections']

            while (len(names) < maximum_connections or maximum_connections == -1) \
                    and pagination <= pagination_threshold:
                driver.get(f'{url}&{profile_connections_configuration["paginationURL"]}={pagination}')
                pagination += 1

                WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, profile_connections_configuration['buttonClass'])
                    ))

                people = driver.find_element(By.CLASS_NAME, profile_connections_configuration['listClass']) \
                    .find_elements(By.TAG_NAME, 'li')

                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(profile_connections_configuration['buttonRenderDelay'])

                pagination_threshold = \
                    int(driver.find_element(By.CLASS_NAME, profile_connections_configuration['paginationInnerHTML'])
                        .find_elements(By.TAG_NAME, 'li')[-1]
                        .find_elements(By.CSS_SELECTOR, '*')[0]
                        .find_elements(By.CSS_SELECTOR, '*')[0]
                        .get_attribute('innerText'))

                driver.execute_script('window.scrollTo(0, 0);')

                for person in people:
                    counter += 1

                    name = person \
                        .find_element(By.CLASS_NAME, profile_connections_configuration['nameClass']) \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .get_attribute('innerText')
                    headline = person \
                        .find_element(By.CLASS_NAME, profile_connections_configuration['headlineClass']) \
                        .get_attribute('innerText')
                    link = person \
                        .find_element(By.CLASS_NAME, profile_connections_configuration['linkClass']) \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .find_elements(By.CSS_SELECTOR, '*')[0] \
                        .get_attribute('href').split('?')[0]

                    if depth - 1 > 0:
                        driver.execute_script('window.open("");')
                        driver.switch_to.window(driver.window_handles[-1])
                        ConnectionHandler.__handle_profile_connections(connect=connect,
                                                                       depth=depth - 1,
                                                                       profile_name=link[link.rindex('/') + 1:],
                                                                       accumulated_links=[])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[-1])

                    if connect:
                        button = person.find_element(By.TAG_NAME, 'button')
                        button_text = button.find_element(By.TAG_NAME, 'span').get_attribute('innerText')
                        if button_text == profile_connections_configuration['connectInnerHTML']:
                            button.click()
                            connect_confirmation_button = driver.find_element(
                                By.XPATH,
                                '//*[text()="' + profile_connections_configuration['confirmInnerHTML'] + '"]'
                            )
                            connect_confirmation_button.find_element(By.XPATH, '..').click()
                            sleep(profile_connections_configuration['connectDelay'])
                        elif button_text == profile_connections_configuration['messageInnerHTML'] or \
                                button_text == profile_connections_configuration['followInnerHTML']:
                            ConnectionHandler.__connect_to_user(url=link)
                        else:
                            continue

                    names.append(name)
                    headlines.append(headline)
                    links.append(link)

                    if len(names) >= maximum_connections != -1:
                        break

                sleep(profile_connections_configuration['paginationDelay'])

            df = pd.DataFrame(
                {'Name': names,
                 'HeadLine': headlines,
                 'Link': links
                 })

            df.to_csv(f'./out/{profile} Connections.csv', index=False)

    @staticmethod
    def handle_company_people(connect: bool = False):
        """
        Iterates through profiles working in a specified company(s).

        :param bool connect: Specify whether to connect to the retrieved list of profiles or not
        """
        company_people_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['companyPeople']

        driver = DriverHandler.get_driver()

        companies = ConfigurationHandler.get_configuration()['companyNames']

        for company in companies:
            url = company_people_configuration['url']
            url = url.replace('COMPANY_NAME', company)

            driver.get(url)

            WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
                .until(EC.presence_of_element_located((By.CLASS_NAME, company_people_configuration['nameClass'])))

            names = []
            headlines = []
            links = []

            counter = 0
            maximum_connections = ConfigurationHandler.get_configuration()['maximumConnections']
            prev_len = 0

            while len(names) < maximum_connections or maximum_connections == -1:
                people = driver.find_element(By.CLASS_NAME, company_people_configuration['listClass']) \
                    .find_elements(By.TAG_NAME, 'li')

                for i in range(counter, len(people)):
                    counter += 1

                    try:
                        name = people[i] \
                            .find_element(By.CLASS_NAME, company_people_configuration['nameClass']) \
                            .get_attribute('innerText')
                        headline = people[i] \
                            .find_element(By.CLASS_NAME, company_people_configuration['headlineClass']) \
                            .get_attribute('innerText')
                        link = people[i] \
                            .find_element(By.CLASS_NAME, company_people_configuration['linkClass']) \
                            .get_attribute('href')

                        button = people[i].find_element(By.TAG_NAME, 'button')
                        button_text = button.find_element(By.TAG_NAME, 'span').get_attribute('innerText')
                    except NoSuchElementException:
                        continue

                    if connect:
                        degree = people[i] \
                            .find_element(By.CLASS_NAME, company_people_configuration['degreeClass']) \
                            .get_attribute('innerText')

                        if company_people_configuration['firstDegreeInnerHTML'] in degree:
                            continue

                        if button_text == company_people_configuration['connectInnerHTML']:
                            button.click()
                            connect_confirmation_button = driver.find_element(
                                By.XPATH,
                                '//*[text()="' + company_people_configuration['confirmInnerHTML'] + '"]'
                            )
                            connect_confirmation_button.find_element(By.XPATH, '..').click()
                            sleep(company_people_configuration['connectDelay'])
                        elif button_text == company_people_configuration['messageInnerHTML'] or \
                                button_text == company_people_configuration['followInnerHTML']:
                            link = people[i] \
                                .find_element(By.CLASS_NAME, company_people_configuration['linkClass']) \
                                .get_attribute('href')
                            ConnectionHandler.__connect_to_user(url=link)
                        else:
                            continue

                    names.append(name)
                    headlines.append(headline)
                    links.append(link)

                    if len(names) >= maximum_connections != -1:
                        break

                if prev_len == len(people):
                    if driver.execute_script('(window.innerHeight + window.scrollY) >= document.body.scrollHeight'):
                        break
                    else:
                        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

                prev_len = len(people)

                sleep(company_people_configuration['scrollDelay'])

            df = pd.DataFrame(
                {'Name': names,
                 'HeadLine': headlines,
                 'Link': links
                 })

            df.to_csv(f'./out/Company People - {company}.csv', index=False)

    @staticmethod
    def handle_received_invitations(accept: bool = False, ignore: bool = False):
        """
        Iterates through profiles in the `received invitations page <RECEIVED_INVITATIONS_>`_.

        :param bool accept: Specify whether to accept the invitation of the retrieved list of profiles or not
        :param bool ignore: Specify whether to ignore the invitation of the retrieved list of profiles or not
        :raises ValueError: if both accept and ignore are truthful

        .. _RECEIVED_INVITATIONS: https://www.linkedin.com/mynetwork/invitation-manager/
        """
        if accept and ignore:
            raise ValueError('accept and ignore cannot be set to True at the same time')

        received_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['receivedInvitations']

        driver = DriverHandler.get_driver()
        url = received_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, received_invitations_configuration['nameClass'])))

        people = driver \
            .find_element(By.CLASS_NAME, received_invitations_configuration['invitationListClass']) \
            .find_elements(By.TAG_NAME, 'li')

        names = []
        headlines = []
        links = []

        for person in people:
            names.append(
                person
                .find_element(By.CLASS_NAME, received_invitations_configuration['nameClass'])
                .get_attribute('innerText')
            )
            headlines.append(
                person
                .find_element(By.CLASS_NAME, received_invitations_configuration['headlineClass'])
                .get_attribute('innerText')
            )
            links.append(
                person
                .find_element(By.CLASS_NAME, received_invitations_configuration['linkClass'])
                .get_attribute('href')
            )

            if accept:
                accept_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['acceptInnerHTML'] + '"]'
                ).find_element(By.XPATH, '..')
                accept_button.click()

                accept_confirmation_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['acceptConfirmationInnerHTML'] + '"]'
                ).find_element(By.XPATH, '..')
                accept_confirmation_button.click()
                sleep(received_invitations_configuration['acceptDelay'])

            if ignore:
                ignore_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['ignoreInnerHTML'] + '"]'
                ).find_element(By.XPATH, '..')
                ignore_button.click()

                ignore_confirmation_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['ignoreConfirmationInnerHTML'] + '"]'
                ).find_element(By.XPATH, '..')
                ignore_confirmation_button.click()
                sleep(received_invitations_configuration['ignoreDelay'])

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv('./out/Received Invitations.csv', index=False)

    @staticmethod
    def handle_sent_invitations(withdraw: bool = False):
        """
        Iterates through profiles in the `sent invitations page <SENT_INVITATIONS_>`_.

        :param bool withdraw: Specify whether to withdraw the invitation sent to the retrieved list of profiles or not
        :raises ValueError: if both accept and ignore are truthful

        .. _SENT_INVITATIONS: https://www.linkedin.com/mynetwork/invitation-manager/sent/
        """
        sent_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['sentInvitations']

        driver = DriverHandler.get_driver()
        url = sent_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, sent_invitations_configuration['nameClass'])))

        people = driver \
            .find_element(By.CLASS_NAME, sent_invitations_configuration['invitationListClass']) \
            .find_elements(By.TAG_NAME, 'li')

        names = []
        headlines = []
        links = []

        for person in people:
            names.append(
                person
                .find_element(By.CLASS_NAME, sent_invitations_configuration['nameClass'])
                .get_attribute('innerText')
            )
            headlines.append(
                person
                .find_element(By.CLASS_NAME, sent_invitations_configuration['headlineClass'])
                .get_attribute('innerText')
            )
            links.append(
                person
                .find_element(By.CLASS_NAME, sent_invitations_configuration['linkClass'])
                .get_attribute('href')
            )

            if withdraw:
                withdraw_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + sent_invitations_configuration['withdrawInnerHTML'] + '"]'
                ).find_element(By.XPATH, '..')
                withdraw_button.click()

                withdraw_confirmation_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + sent_invitations_configuration['withdrawConfirmationInnerHTML'] + '"]'
                ).find_element(By.XPATH, '..')
                withdraw_confirmation_button.click()
                sleep(sent_invitations_configuration['withdrawDelay'])

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv('./out/Sent Invitations.csv', index=False)
