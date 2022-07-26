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
    def __connect_to_user(url: Union[str, list[str]]):
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
            )[1].find_element_by_xpath('..')

            driver.execute_script('arguments[0].click();', accept_button)

            try:
                connect_confirmation_button = driver.find_element(
                    By.XPATH,
                    '//*[text()="' + user_configuration['confirmInnerHTML'] + '"]'
                )
                connect_confirmation_button.find_element_by_xpath('..').click()
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
                connect_button.find_element_by_xpath('..').click()

                connect_confirmation_button = driver.find_element(
                    By.XPATH,
                    '//*[text()="' + user_configuration['confirmInnerHTML'] + '"]'
                )
                connect_confirmation_button.find_element_by_xpath('..').click()

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            sleep(user_configuration['closeDelay'])

    @staticmethod
    def handle_suggestions(connect: bool = False):
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
            ).find_element_by_xpath('..').find_element_by_xpath('..')
            people = suggestion_section.find_element_by_class_name(suggestions_configuration['listClass']) \
                .find_elements_by_tag_name('li')

            for i in range(counter, len(people)):
                counter += 1

                name = people[i] \
                    .find_element_by_class_name(suggestions_configuration['nameClass']) \
                    .get_attribute('innerText')
                headline = people[i] \
                    .find_element_by_class_name(suggestions_configuration['headlineClass']) \
                    .get_attribute('innerText')
                link = people[i] \
                    .find_element_by_class_name(suggestions_configuration['linkClass']) \
                    .get_attribute('href')

                if connect:
                    button = people[i].find_elements_by_tag_name('button')[-1]
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

            people = driver.find_element_by_class_name(people_search_configuration['listClass']) \
                .find_elements_by_tag_name('li')

            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            sleep(people_search_configuration['buttonRenderDelay'])

            pagination_threshold = \
                int(driver.find_element_by_class_name(people_search_configuration['paginationInnerHTML'])
                    .find_elements_by_tag_name('li')[-1]
                    .find_elements_by_css_selector('*')[0]
                    .find_elements_by_css_selector('*')[0]
                    .get_attribute('innerText'))

            driver.execute_script('window.scrollTo(0, 0);')

            for person in people:
                counter += 1

                name = person \
                    .find_element_by_class_name(people_search_configuration['nameClass']) \
                    .find_elements_by_css_selector('*')[0] \
                    .find_elements_by_css_selector('*')[0] \
                    .find_elements_by_css_selector('*')[0] \
                    .find_elements_by_css_selector('*')[0] \
                    .get_attribute('innerText')
                headline = person \
                    .find_element_by_class_name(people_search_configuration['headlineClass']) \
                    .get_attribute('innerText')
                link = person \
                    .find_element_by_class_name(people_search_configuration['linkClass']) \
                    .find_elements_by_css_selector('*')[0] \
                    .find_elements_by_css_selector('*')[0] \
                    .get_attribute('href').split('?')[0]

                if connect:
                    button = person.find_element_by_tag_name('button')
                    button_text = button.find_element_by_tag_name('span').get_attribute('innerText')
                    if button_text == people_search_configuration['connectInnerHTML']:
                        button.click()
                        connect_confirmation_button = driver.find_element(
                            By.XPATH,
                            '//*[text()="' + people_search_configuration['confirmInnerHTML'] + '"]'
                        )
                        connect_confirmation_button.find_element_by_xpath('..').click()
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
    def __handle_profile_connections(profile_name, accumulated_links: list[str], connect: bool = False, depth=1):
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
                    .find_element_by_class_name(profile_connections_configuration['connectionsIndicatorClass']) \
                    .find_element_by_tag_name('a') \
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

                people = driver.find_element_by_class_name(profile_connections_configuration['listClass']) \
                    .find_elements_by_tag_name('li')

                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(profile_connections_configuration['buttonRenderDelay'])

                pagination_threshold = \
                    int(driver.find_element_by_class_name(profile_connections_configuration['paginationInnerHTML'])
                        .find_elements_by_tag_name('li')[-1]
                        .find_elements_by_css_selector('*')[0]
                        .find_elements_by_css_selector('*')[0]
                        .get_attribute('innerText'))

                driver.execute_script('window.scrollTo(0, 0);')

                for person in people:
                    counter += 1

                    name = person \
                        .find_element_by_class_name(profile_connections_configuration['nameClass']) \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
                        .get_attribute('innerText')
                    headline = person \
                        .find_element_by_class_name(profile_connections_configuration['headlineClass']) \
                        .get_attribute('innerText')
                    link = person \
                        .find_element_by_class_name(profile_connections_configuration['linkClass']) \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
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
                        button = person.find_element_by_tag_name('button')
                        button_text = button.find_element_by_tag_name('span').get_attribute('innerText')
                        if button_text == profile_connections_configuration['connectInnerHTML']:
                            button.click()
                            connect_confirmation_button = driver.find_element(
                                By.XPATH,
                                '//*[text()="' + profile_connections_configuration['confirmInnerHTML'] + '"]'
                            )
                            connect_confirmation_button.find_element_by_xpath('..').click()
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
    def handle_profile_connections(connect: bool = False, depth=1):
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
                    .find_element_by_class_name(profile_connections_configuration['connectionsIndicatorClass']) \
                    .find_element_by_tag_name('a') \
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

                people = driver.find_element_by_class_name(profile_connections_configuration['listClass']) \
                    .find_elements_by_tag_name('li')

                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(profile_connections_configuration['buttonRenderDelay'])

                pagination_threshold = \
                    int(driver.find_element_by_class_name(profile_connections_configuration['paginationInnerHTML'])
                        .find_elements_by_tag_name('li')[-1]
                        .find_elements_by_css_selector('*')[0]
                        .find_elements_by_css_selector('*')[0]
                        .get_attribute('innerText'))

                driver.execute_script('window.scrollTo(0, 0);')

                for person in people:
                    counter += 1

                    name = person \
                        .find_element_by_class_name(profile_connections_configuration['nameClass']) \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
                        .get_attribute('innerText')
                    headline = person \
                        .find_element_by_class_name(profile_connections_configuration['headlineClass']) \
                        .get_attribute('innerText')
                    link = person \
                        .find_element_by_class_name(profile_connections_configuration['linkClass']) \
                        .find_elements_by_css_selector('*')[0] \
                        .find_elements_by_css_selector('*')[0] \
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
                        button = person.find_element_by_tag_name('button')
                        button_text = button.find_element_by_tag_name('span').get_attribute('innerText')
                        if button_text == profile_connections_configuration['connectInnerHTML']:
                            button.click()
                            connect_confirmation_button = driver.find_element(
                                By.XPATH,
                                '//*[text()="' + profile_connections_configuration['confirmInnerHTML'] + '"]'
                            )
                            connect_confirmation_button.find_element_by_xpath('..').click()
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
                people = driver.find_element_by_class_name(company_people_configuration['listClass']) \
                    .find_elements_by_tag_name('li')

                for i in range(counter, len(people)):
                    counter += 1

                    try:
                        name = people[i] \
                            .find_element_by_class_name(company_people_configuration['nameClass']) \
                            .get_attribute('innerText')
                        headline = people[i] \
                            .find_element_by_class_name(company_people_configuration['headlineClass']) \
                            .get_attribute('innerText')
                        link = people[i] \
                            .find_element_by_class_name(company_people_configuration['linkClass']) \
                            .get_attribute('href')

                        button = people[i].find_element_by_tag_name('button')
                        button_text = button.find_element_by_tag_name('span').get_attribute('innerText')
                    except NoSuchElementException:
                        continue

                    if connect:
                        degree = people[i] \
                            .find_element_by_class_name(company_people_configuration['degreeClass']) \
                            .get_attribute('innerText')

                        if company_people_configuration['firstDegreeInnerHTML'] in degree:
                            continue

                        if button_text == company_people_configuration['connectInnerHTML']:
                            button.click()
                            connect_confirmation_button = driver.find_element(
                                By.XPATH,
                                '//*[text()="' + company_people_configuration['confirmInnerHTML'] + '"]'
                            )
                            connect_confirmation_button.find_element_by_xpath('..').click()
                            sleep(company_people_configuration['connectDelay'])
                        elif button_text == company_people_configuration['messageInnerHTML'] or \
                                button_text == company_people_configuration['followInnerHTML']:
                            link = people[i] \
                                .find_element_by_class_name(company_people_configuration['linkClass']) \
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
            .find_element_by_class_name(received_invitations_configuration['invitationListClass']) \
            .find_elements_by_tag_name('li')

        names = []
        headlines = []
        links = []

        for person in people:
            names.append(
                person
                .find_element_by_class_name(received_invitations_configuration['nameClass'])
                .get_attribute('innerText')
            )
            headlines.append(
                person
                .find_element_by_class_name(received_invitations_configuration['headlineClass'])
                .get_attribute('innerText')
            )
            links.append(
                person
                .find_element_by_class_name(received_invitations_configuration['linkClass'])
                .get_attribute('href')
            )

            if accept:
                accept_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['acceptInnerHTML'] + '"]'
                ).find_element_by_xpath('..')
                accept_button.click()

                accept_confirmation_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['acceptConfirmationInnerHTML'] + '"]'
                ).find_element_by_xpath('..')
                accept_confirmation_button.click()
                sleep(received_invitations_configuration['acceptDelay'])

            if ignore:
                ignore_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['ignoreInnerHTML'] + '"]'
                ).find_element_by_xpath('..')
                ignore_button.click()

                ignore_confirmation_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + received_invitations_configuration['ignoreConfirmationInnerHTML'] + '"]'
                ).find_element_by_xpath('..')
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
        sent_invitations_configuration = \
            ConfigurationHandler.get_configuration()['endpoints']['sentInvitations']

        driver = DriverHandler.get_driver()
        url = sent_invitations_configuration['url']

        driver.get(url)

        WebDriverWait(driver, ConfigurationHandler.get_configuration()['webLoadDelay']) \
            .until(EC.presence_of_element_located((By.CLASS_NAME, sent_invitations_configuration['nameClass'])))

        people = driver \
            .find_element_by_class_name(sent_invitations_configuration['invitationListClass']) \
            .find_elements_by_tag_name('li')

        names = []
        headlines = []
        links = []

        for person in people:
            names.append(
                person
                .find_element_by_class_name(sent_invitations_configuration['nameClass'])
                .get_attribute('innerText')
            )
            headlines.append(
                person
                .find_element_by_class_name(sent_invitations_configuration['headlineClass'])
                .get_attribute('innerText')
            )
            links.append(
                person
                .find_element_by_class_name(sent_invitations_configuration['linkClass'])
                .get_attribute('href')
            )

            if withdraw:
                withdraw_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + sent_invitations_configuration['withdrawInnerHTML'] + '"]'
                ).find_element_by_xpath('..')
                withdraw_button.click()

                withdraw_confirmation_button = person.find_element(
                    By.XPATH,
                    '//*[text()="' + sent_invitations_configuration['withdrawConfirmationInnerHTML'] + '"]'
                ).find_element_by_xpath('..')
                withdraw_confirmation_button.click()
                sleep(sent_invitations_configuration['withdrawDelay'])

        df = pd.DataFrame(
            {'Name': names,
             'HeadLine': headlines,
             'Link': links
             })

        df.to_csv('./out/Sent Invitations.csv', index=False)
